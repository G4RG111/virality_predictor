from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..models import Product, IngestionJob, Review
from ..schemas.ingestion import IngestionJobResponse, UploadResponse
from ..config import settings
from ..services.ingestion_service import embed_reviews
from ..services.amazon_scraper import fetch_amazon_reviews, ScraperBlockedError

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

_ALLOWED_REVIEW_SUFFIXES = {".csv", ".xlsx", ".xls", ".json"}
_ALLOWED_PDF_SUFFIXES = {".pdf"}


def _save_upload(file: UploadFile, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / file.filename
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return dest


@router.post("/upload/ihut", response_model=UploadResponse, status_code=202)
async def upload_ihut_pdf(
    background_tasks: BackgroundTasks,
    product_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or Path(file.filename).suffix.lower() not in _ALLOWED_PDF_SUFFIXES:
        raise HTTPException(status_code=400, detail={"error": "file_must_be_pdf"})

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    dest = _save_upload(file, settings.upload_dir / "ihut")

    job = IngestionJob(
        product_id=product_id,
        source_type="ihut_pdf",
        source_file_name=file.filename,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id

    background_tasks.add_task(_process_ihut_pdf, job_id, str(dest), product_id)

    return UploadResponse(
        job_id=job_id,
        product_id=product_id,
        source_type="ihut_pdf",
        status="queued",
        message=f"iHUT PDF queued for processing. Poll /ingestion/jobs/{job_id} for status.",
    )


@router.post("/upload/reviews", response_model=UploadResponse, status_code=202)
async def upload_reviews(
    background_tasks: BackgroundTasks,
    product_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename).suffix.lower() if file.filename else ""
    if suffix not in _ALLOWED_REVIEW_SUFFIXES:
        raise HTTPException(status_code=400, detail={"error": "unsupported_file_type", "allowed": list(_ALLOWED_REVIEW_SUFFIXES)})

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    dest = _save_upload(file, settings.upload_dir / "reviews")

    job = IngestionJob(
        product_id=product_id,
        source_type="amazon_reviews",
        source_file_name=file.filename,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id

    background_tasks.add_task(_process_reviews, job_id, str(dest), product_id)

    return UploadResponse(
        job_id=job_id,
        product_id=product_id,
        source_type="amazon_reviews",
        status="queued",
        message=f"Reviews file queued for processing. Poll /ingestion/jobs/{job_id} for status.",
    )


@router.post("/fetch/amazon/{product_id}", response_model=UploadResponse, status_code=202)
def fetch_amazon(
    product_id: UUID,
    background_tasks: BackgroundTasks,
    asin: str | None = None,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    effective_asin = asin or product.asin
    if not effective_asin:
        raise HTTPException(status_code=400, detail={"error": "asin_required", "message": "Provide an ASIN or set one on the product first."})

    if not product.asin and asin:
        product.asin = asin
        db.commit()

    job = IngestionJob(
        product_id=product_id,
        source_type="amazon_scrape",
        source_file_name=f"amazon:{effective_asin}",
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id

    background_tasks.add_task(_process_amazon_scrape, job_id, effective_asin, product_id)

    return UploadResponse(
        job_id=job_id,
        product_id=product_id,
        source_type="amazon_scrape",
        status="queued",
        message=f"Amazon review fetch queued for ASIN {effective_asin}. Poll /ingestion/jobs/{job_id} for status.",
    )


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail={"error": "job_not_found"})
    return job


@router.get("/jobs", response_model=list[IngestionJobResponse])
def list_jobs(
    product_id: UUID | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(IngestionJob)
    if product_id:
        query = query.filter(IngestionJob.product_id == product_id)
    if status:
        query = query.filter(IngestionJob.status == status)
    return query.order_by(IngestionJob.created_at.desc()).limit(100).all()


def _process_ihut_pdf(job_id: UUID, file_path: str, product_id: UUID) -> None:
    db = SessionLocal()
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()

        ml_path = str(settings.ml_pipeline_path.resolve())
        if ml_path not in sys.path:
            sys.path.insert(0, ml_path)

        from pipeline.ingestion.ihut_extractor import extract_ihut_pdf

        doc = extract_ihut_pdf(file_path)
        count = 0
        new_ids = []

        for chunk in doc.verbatim_chunks:
            if len(chunk.text.strip()) < 15:
                continue
            review = Review(
                product_id=product_id,
                source="ihut",
                review_text=chunk.text,
                market=chunk.market,
                reviewer_type="tester",
                ingestion_job_id=job_id,
            )
            db.add(review)
            db.flush()
            new_ids.append(review.id)
            count += 1

        db.commit()
        embed_reviews(new_ids, db)

        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.record_count = count
        db.commit()

    except Exception as e:
        db.rollback()
        try:
            job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def _process_amazon_scrape(job_id: UUID, asin: str, product_id: UUID) -> None:
    db = SessionLocal()
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()

        raw_reviews = fetch_amazon_reviews(asin, max_pages=10)
        count = 0
        new_ids = []

        for r in raw_reviews:
            review = Review(
                product_id=product_id,
                source="amazon",
                review_text=r["review_text"],
                rating=r.get("rating"),
                review_date=r.get("review_date"),
                market=r.get("market", "US"),
                verified_purchase=r.get("verified_purchase", False),
                ingestion_job_id=job_id,
            )
            db.add(review)
            db.flush()
            new_ids.append(review.id)
            count += 1

        db.commit()
        embed_reviews(new_ids, db)

        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.record_count = count
        db.commit()

    except ScraperBlockedError as e:
        db.rollback()
        try:
            job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = f"Amazon blocked the request: {e}."
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
    except Exception as e:
        db.rollback()
        try:
            job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def _process_reviews(job_id: UUID, file_path: str, product_id: UUID) -> None:
    db = SessionLocal()
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()

        ml_path = str(settings.ml_pipeline_path.resolve())
        if ml_path not in sys.path:
            sys.path.insert(0, ml_path)

        from pipeline.ingestion.review_ingestion import ingest_reviews

        ml_reviews = ingest_reviews(file_path)
        count = 0
        new_ids = []

        for r in ml_reviews:
            review = Review(
                product_id=product_id,
                source=r.source,
                external_id=r.external_id,
                review_text=r.text,
                rating=r.rating,
                review_date=r.review_date,
                market=r.market,
                verified_purchase=r.verified_purchase,
                helpful_votes=r.helpful_votes,
                ingestion_job_id=job_id,
            )
            db.add(review)
            db.flush()
            new_ids.append(review.id)
            count += 1

        db.commit()
        embed_reviews(new_ids, db)

        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.record_count = count
        db.commit()

    except Exception as e:
        db.rollback()
        try:
            job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
