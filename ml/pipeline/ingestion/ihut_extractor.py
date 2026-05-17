# -*- coding: utf-8 -*-
"""
iHUT PDF Extractor.
Processes SharkNinja In-Home User Testing PDF reports (PowerPoint exports).
Uses pdfplumber for layout-aware extraction that preserves tester verbatims.
"""
from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

from ..features.base_extractor import IHUTChunk
from ..utils.lexicons import (
    HACKABILITY_PHRASES,
    EXPERIMENT_INTENT_PHRASES,
    contains_any,
)


@dataclass
class IHUTDocument:
    """Parsed iHUT PDF document."""
    file_path: str
    product: str
    market: str
    chunks: list[IHUTChunk] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def verbatim_chunks(self) -> list[IHUTChunk]:
        return [c for c in self.chunks if c.chunk_type == "verbatim"]

    @property
    def hackability_chunks(self) -> list[IHUTChunk]:
        """iHUT chunks containing pre-launch hackability signals."""
        return [
            c for c in self.verbatim_chunks
            if contains_any(c.text, HACKABILITY_PHRASES + EXPERIMENT_INTENT_PHRASES)
        ]


# Font-size thresholds for classifying slide text
_HEADER_MIN_SIZE = 16.0
_VERBATIM_MAX_SIZE = 11.0

# Section header keywords that signal tester verbatim sections
_VERBATIM_SECTION_KEYWORDS = [
    "verbatim", "quotes", "what testers said", "in their words",
    "tester comments", "open-ended", "feedback", "comments",
    "key quotes", "notable quotes", "consumer verbatims",
    "voice of", "in their own words", "what they said",
]

# Quote characters as unicode escapes (ASCII-safe source file)
# U+201C LEFT DOUBLE QUOTATION MARK, U+201D RIGHT DOUBLE QUOTATION MARK
# U+201E DOUBLE LOW-9 QUOTATION MARK, U+201F DOUBLE HIGH-REVERSED-9 QUOTATION MARK
# U+2018 LEFT SINGLE QUOTATION MARK, U+2019 RIGHT SINGLE QUOTATION MARK
# U+00AB LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
# U+00BB RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
# U+2039 SINGLE LEFT-POINTING ANGLE QUOTATION MARK
# U+203A SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
_QUOTE_SET = (
    "“”„‟"  # curly/low double quotes
    "‘’"              # curly single quotes
    "«»"              # guillemets
    "‹›"              # angle quotes
    "\"\'"                      # ASCII fallback
)
_QUOTE_PATTERN = re.compile(
    "[" + _QUOTE_SET + "](.{15,400})[" + _QUOTE_SET + "]",
    re.DOTALL,
)

# Bullet symbols used in iHUT decks as unicode escapes
# U+2022 BULLET, U+25E6 WHITE BULLET, U+25AA BLACK SMALL SQUARE
# U+25B8 BLACK RIGHT-POINTING SMALL TRIANGLE, U+25BA BLACK RIGHT-POINTING POINTER
# U+2023 TRIANGULAR BULLET, U+2043 HYPHEN BULLET, U+2219 BULLET OPERATOR
# U+25AB WHITE SMALL SQUARE, U+25CB WHITE CIRCLE, U+25CF BLACK CIRCLE
# U+25A1 WHITE SQUARE, U+25A0 BLACK SQUARE
_BULLET_SET = (
    "•◦▪▸►"
    "‣⁃∙▫○●□■"
    "\\-"  # ASCII dash as fallback
)
_BULLET_PATTERN = re.compile(
    r"^[\s]*[" + _BULLET_SET + r"]\s+(.{20,})"
)

# First-person language strongly signals a direct tester quote
_FIRST_PERSON_RE = re.compile(
    r"\b(i |i've |i'm |i don't |i would |my |me |we |our |"
    r"felt like|reminded me|loved it|hated it)\b",
    re.IGNORECASE,
)

# Analyst / template text patterns - skip these
_ANALYST_RE = re.compile(
    r"(n=\d+|base:|respondents|figure \d+|chart \d+|"
    r"copyright|confidential|proprietary|"
    r"^(slide|section|chapter|agenda|summary|contents)\b)",
    re.IGNORECASE,
)

# Market detection from filename
_MARKET_PATTERNS = {
    "DE": ["de ihut", "germany", "german", "_de_", " de "],
    "UK": ["uk ihut", "uk slim", "united kingdom", "_uk_", " uk "],
    "US": ["us ihut", "united states", "_us_", " us "],
    "AU": ["au ihut", "australia", "_au_"],
    "Global": ["global", "master"],
}

# Zero-width and other invisible Unicode characters to strip
_INVISIBLE_RE = re.compile(
    "[​‌‍﻿­]"  # zero-width, BOM, soft-hyphen
)

# Leading bullet/symbol chars to strip when cleaning text
_LEADING_BULLETS_RE = re.compile(
    r"^[\s]*[" + _BULLET_SET.replace("\\-", "") + r"\-]+\s*"
)


def _clean_text(text: str) -> str:
    """Remove unicode artifacts and normalize whitespace."""
    text = _INVISIBLE_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _strip_bullets(text: str) -> str:
    """Remove leading bullet symbols from text."""
    return _LEADING_BULLETS_RE.sub("", text).strip()


def _detect_market(filename: str) -> str:
    fn_lower = filename.lower()
    for market, patterns in _MARKET_PATTERNS.items():
        if any(p in fn_lower for p in patterns):
            return market
    return "Unknown"


def _detect_product(filename: str) -> str:
    fn = Path(filename).stem
    fn = re.sub(r"ihut|master.?deck|compressed|pptx|_\d{1,2}[a-z]{3}", "", fn, flags=re.IGNORECASE)
    fn = re.sub(r"[_\-]+", " ", fn).strip()
    return fn or "Unknown Product"


def _is_verbatim_section_header(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in _VERBATIM_SECTION_KEYWORDS)


def _classify_chunk_type(
    text: str,
    font_size: float | None,
    in_verbatim_section: bool,
) -> str:
    """Classify a text block as header, body, or verbatim."""
    if _ANALYST_RE.search(text) and not _FIRST_PERSON_RE.search(text):
        return "body"

    if font_size and font_size >= _HEADER_MIN_SIZE:
        return "header"

    # No font size from compressed PDF — detect headers by keyword + short length
    if not font_size and len(text) < 80 and _is_verbatim_section_header(text):
        return "header"

    if _QUOTE_PATTERN.search(text):
        return "verbatim"

    bullet_m = _BULLET_PATTERN.match(text)
    if bullet_m and _FIRST_PERSON_RE.search(bullet_m.group(1)):
        return "verbatim"

    if in_verbatim_section and len(text) > 30:
        return "verbatim"

    if _FIRST_PERSON_RE.search(text) and len(text) > 40:
        return "verbatim"

    if font_size and font_size <= _VERBATIM_MAX_SIZE and len(text) > 40:
        return "verbatim"

    return "body"


def extract_ihut_pdf(file_path: str | Path) -> IHUTDocument:
    """
    Extract structured chunks from an iHUT PDF.

    Strategy:
    1. Use pdfplumber for layout-aware text + font-size extraction
    2. Classify each text block as header / body / verbatim
    3. Track section context (verbatim section header detection)
    4. Apply first-person language and bullet-pattern heuristics
    5. Flag chunks with hackability signals for pre-launch scoring
    """
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError("pdfplumber not installed. Run: pip install pdfplumber") from e

    path = Path(file_path)
    product = _detect_product(path.name)
    market = _detect_market(path.name)

    chunks: list[IHUTChunk] = []
    current_section: str | None = None
    in_verbatim_section = False

    with pdfplumber.open(str(path)) as pdf:
        total_pages = len(pdf.pages)

        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(
                x_tolerance=3,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=True,
            )
            if not words:
                continue

            blocks = _group_words_into_blocks(words)

            for block_text, font_size in blocks:
                block_text = _clean_text(block_text)
                if len(block_text) < 5:
                    continue

                # Update section context
                if (font_size and font_size >= _HEADER_MIN_SIZE) or (
                    not font_size and len(block_text) < 80
                    and _is_verbatim_section_header(block_text)
                ):
                    current_section = block_text
                    in_verbatim_section = _is_verbatim_section_header(block_text)

                chunk_type = _classify_chunk_type(block_text, font_size, in_verbatim_section)

                # Extract quoted sub-strings as separate verbatim chunks
                if chunk_type == "body":
                    for q in _QUOTE_PATTERN.findall(block_text):
                        q = _clean_text(q)
                        if len(q) > 20:
                            chunks.append(IHUTChunk(
                                text=q,
                                chunk_type="verbatim",
                                slide_number=page_num,
                                section=current_section,
                                market=market,
                                product=product,
                            ))

                # Emit bullet-verbatims as a cleaned chunk instead of the raw one
                if chunk_type in ("verbatim", "body"):
                    bullet_m = _BULLET_PATTERN.match(block_text)
                    if bullet_m:
                        cleaned = _clean_text(bullet_m.group(1))
                        if len(cleaned) > 20 and cleaned != block_text:
                            chunks.append(IHUTChunk(
                                text=cleaned,
                                chunk_type="verbatim",
                                slide_number=page_num,
                                section=current_section,
                                market=market,
                                product=product,
                            ))
                            continue  # skip raw bullet line

                chunks.append(IHUTChunk(
                    text=block_text,
                    chunk_type=chunk_type,
                    slide_number=page_num,
                    section=current_section,
                    market=market,
                    product=product,
                ))

    chunks += _extract_table_cells(str(path), product, market)

    return IHUTDocument(
        file_path=str(path),
        product=product,
        market=market,
        chunks=chunks,
        metadata={"total_pages": total_pages, "total_chunks": len(chunks)},
    )


def _group_words_into_blocks(
    words: list[dict],
    y_tolerance: float = 5.0,
) -> list[tuple[str, float | None]]:
    """Group pdfplumber word dicts into lines by Y-coordinate proximity."""
    if not words:
        return []

    lines: list[list[dict]] = []
    current_line: list[dict] = [words[0]]

    for word in words[1:]:
        prev_y = current_line[-1].get("top", 0)
        curr_y = word.get("top", 0)
        if abs(curr_y - prev_y) <= y_tolerance:
            current_line.append(word)
        else:
            lines.append(current_line)
            current_line = [word]
    lines.append(current_line)

    result = []
    for line in lines:
        text = " ".join(w.get("text", "") for w in line)
        sizes = [w.get("size") for w in line if w.get("size")]
        avg_size = sum(sizes) / len(sizes) if sizes else None
        result.append((text, avg_size))
    return result


def _extract_table_cells(
    file_path: str,
    product: str,
    market: str,
) -> list[IHUTChunk]:
    """Extract text from tables (satisfaction rating grids, open-ended columns)."""
    try:
        import pdfplumber
    except ImportError:
        return []

    chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            for table in page.extract_tables():
                for row in table:
                    for cell in row:
                        if not cell:
                            continue
                        cleaned = _clean_text(str(cell))
                        if len(cleaned) < 10:
                            continue
                        chunk_type = "verbatim" if _FIRST_PERSON_RE.search(cleaned) else "table_cell"
                        chunks.append(IHUTChunk(
                            text=cleaned,
                            chunk_type=chunk_type,
                            slide_number=page_num,
                            section=None,
                            market=market,
                            product=product,
                        ))
    return chunks


def extract_multiple_ihut_pdfs(file_paths: list[str | Path]) -> list[IHUTDocument]:
    """Process a list of iHUT PDF files and return all documents."""
    return [extract_ihut_pdf(fp) for fp in file_paths]
