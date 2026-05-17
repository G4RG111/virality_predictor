"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, RotateCcw, Loader2, Upload } from "lucide-react";
import { DimensionBars } from "@/components/vibe/DimensionBars";
import type { Product, VibeScore, KeyDriversResponse, ScoreBand } from "@/lib/types";
import { BAND_LABELS, BAND_COLORS, DIMENSION_LABELS } from "@/lib/types";
import { getBandColor, formatDate } from "@/lib/utils";
import { products as productsApi, scoring, explain } from "@/lib/api-client";

function DriversSection({ drivers }: { drivers: KeyDriversResponse }) {
  const pos = drivers.positive_drivers.slice(0, 3);
  const neg = drivers.negative_drivers.slice(0, 3);
  if (pos.length === 0 && neg.length === 0) return null;

  return (
    <div className="grid grid-cols-2 gap-8">
      <div>
        <h3 className="text-[10px] font-bold tracking-[0.18em] uppercase text-emerald-600 mb-4">The Viral Case</h3>
        <div className="space-y-4">
          {pos.map((d) => (
            <div key={d.dimension} className="flex gap-3">
              <span className="text-[12px] font-bold font-mono text-emerald-600 flex-shrink-0 w-12 text-right pt-0.5">{d.impact}</span>
              <div>
                <div className="text-[13px] font-semibold text-[#111111]">{DIMENSION_LABELS[d.dimension] ?? d.dimension}</div>
                <div className="text-[11px] text-[#777777] mt-0.5 leading-relaxed">{d.reason}</div>
              </div>
            </div>
          ))}
          {pos.length === 0 && <p className="text-[12px] text-[#BBBBBB]">No significant positive drivers.</p>}
        </div>
      </div>
      <div>
        <h3 className="text-[10px] font-bold tracking-[0.18em] uppercase text-red-500 mb-4">The Drag</h3>
        <div className="space-y-4">
          {neg.map((d) => (
            <div key={d.dimension} className="flex gap-3">
              <span className="text-[12px] font-bold font-mono text-red-500 flex-shrink-0 w-12 text-right pt-0.5">{d.impact}</span>
              <div>
                <div className="text-[13px] font-semibold text-[#111111]">{DIMENSION_LABELS[d.dimension] ?? d.dimension}</div>
                <div className="text-[11px] text-[#777777] mt-0.5 leading-relaxed">{d.reason}</div>
              </div>
            </div>
          ))}
          {neg.length === 0 && <p className="text-[12px] text-[#BBBBBB]">No significant limiting factors.</p>}
        </div>
      </div>
    </div>
  );
}

export default function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [product, setProduct] = useState<Product | null>(null);
  const [vibeScore, setVibeScore] = useState<VibeScore | null>(null);
  const [drivers, setDrivers] = useState<KeyDriversResponse | null>(null);
  const [computing, setComputing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [prod, history] = await Promise.all([productsApi.get(id), productsApi.vibeHistory(id)]);
      setProduct(prod);
      const latest = history.history[0] ?? null;
      setVibeScore(latest);
      if (latest) explain.keyDrivers(id).then(setDrivers).catch(() => {});
    } catch {
      setLoadError("Failed to load product data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [id]);

  const handleCompute = async () => {
    setComputing(true);
    try {
      await scoring.compute(id);
      await new Promise((r) => setTimeout(r, 3000));
      const history = await productsApi.vibeHistory(id);
      const latest = history.history[0] ?? null;
      setVibeScore(latest);
      if (latest) explain.keyDrivers(id).then(setDrivers).catch(() => {});
    } finally {
      setComputing(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center">
      <Loader2 className="w-5 h-5 text-[#E41E26] animate-spin" />
    </div>
  );

  if (loadError || !product) return (
    <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center">
      <div className="text-center">
        <p className="text-[14px] text-[#999999] mb-3">{loadError ?? "Product not found."}</p>
        <Link href="/" className="text-[13px] text-[#E41E26] hover:underline">← Back to Portfolio</Link>
      </div>
    </div>
  );

  const band = (vibeScore?.score_band ?? "low") as ScoreBand;
  const color = vibeScore ? getBandColor(band) : "#CCCCCC";

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      <div className="bg-white border-b border-[#E5E5E5] px-8 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-[12px] text-[#999999] hover:text-[#111111] transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />Portfolio
        </Link>
        <div className="flex items-center gap-2.5">
          <Link href={`/analyze?product_id=${id}`}
            className="flex items-center gap-1.5 text-[12px] font-medium text-[#555555] hover:text-[#111111] border border-[#E5E5E5] hover:border-[#CCCCCC] rounded px-3 py-1.5 transition-colors">
            <Upload className="w-3.5 h-3.5" />Upload Data
          </Link>
          <button onClick={handleCompute} disabled={computing}
            className="flex items-center gap-1.5 text-[12px] font-semibold text-white bg-[#E41E26] hover:bg-[#C8151B] rounded px-4 py-1.5 transition-colors disabled:opacity-50">
            {computing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
            {computing ? "Computing…" : "Compute VIBE"}
          </button>
        </div>
      </div>

      <main className="max-w-[860px] mx-auto px-8 py-10">
        <div className="mb-8">
          <h1 className="text-[26px] font-black text-[#111111] tracking-tight">{product.name}</h1>
          <div className="flex items-center gap-2 mt-1.5">
            {[product.category, product.market, product.sku, product.price_usd ? `$${product.price_usd}` : null]
              .filter(Boolean).map((item, i, arr) => (
                <span key={i} className="flex items-center gap-2">
                  <span className="text-[12px] text-[#AAAAAA]">{item}</span>
                  {i < arr.length - 1 && <span className="text-[#DDDDDD] text-[10px]">·</span>}
                </span>
              ))}
          </div>
        </div>

        {vibeScore ? (
          <>
            <div className="bg-white border border-[#E5E5E5] rounded-xl p-8 mb-5">
              <div className="flex items-end gap-8">
                <div>
                  <div className="text-[80px] font-black leading-none tabular-nums" style={{ color }}>
                    {vibeScore.vibe_score.toFixed(1)}
                  </div>
                  <div className="text-[10px] tracking-[0.2em] uppercase text-[#BBBBBB] font-semibold mt-2">VIBE Score</div>
                </div>
                <div className="pb-3">
                  <div className="text-[18px] font-black tracking-wider uppercase" style={{ color }}>
                    {BAND_LABELS[band]}
                  </div>
                  <div className="text-[12px] text-[#AAAAAA] mt-1 capitalize">{vibeScore.confidence} confidence</div>
                  <div className="text-[11px] text-[#CCCCCC] mt-0.5">Computed {formatDate(vibeScore.computed_at)}</div>
                </div>
              </div>
            </div>

            {drivers?.narrative && (
              <div className="bg-white border border-[#E5E5E5] rounded-xl p-6 mb-5">
                <h2 className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#BBBBBB] mb-3">AI Assessment</h2>
                <div className="pl-4 border-l-[3px] border-[#E41E26]/40">
                  <p className="text-[14px] text-[#444444] leading-relaxed">{drivers.narrative}</p>
                </div>
              </div>
            )}

            {drivers && (drivers.positive_drivers.length > 0 || drivers.negative_drivers.length > 0) && (
              <div className="bg-white border border-[#E5E5E5] rounded-xl p-6 mb-5">
                <h2 className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#BBBBBB] mb-5">Key Drivers</h2>
                <DriversSection drivers={drivers} />
              </div>
            )}

            <div className="bg-white border border-[#E5E5E5] rounded-xl p-6 mb-5">
              <h2 className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#BBBBBB] mb-5">All Dimensions</h2>
              {vibeScore.dimension_scores && vibeScore.dimension_scores.length > 0 ? (
                <DimensionBars dimensions={vibeScore.dimension_scores} band={band} />
              ) : (
                <p className="text-[13px] text-[#BBBBBB]">Dimension data unavailable.</p>
              )}
            </div>

            <Link href={`/products/${id}/explainability`}
              className="inline-flex items-center gap-2 text-[12px] font-medium text-[#999999] hover:text-[#E41E26] transition-colors group">
              <span>Full SHAP Explainability Analysis</span>
              <span className="group-hover:translate-x-0.5 transition-transform">→</span>
            </Link>
          </>
        ) : (
          <div className="bg-white border-2 border-dashed border-[#E5E5E5] rounded-xl py-16 text-center">
            <div className="w-16 h-16 rounded-full bg-[#F5F5F5] flex items-center justify-center mx-auto mb-5">
              <span className="text-[#CCCCCC] text-2xl font-black">—</span>
            </div>
            <h2 className="text-[16px] font-bold text-[#111111] mb-2">Not yet analyzed</h2>
            <p className="text-[13px] text-[#AAAAAA] mb-6 max-w-xs mx-auto leading-relaxed">
              Upload iHUT verbatims or Amazon reviews, then compute the VIBE score.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href={`/analyze?product_id=${id}`}
                className="flex items-center gap-1.5 px-4 py-2 text-[13px] font-semibold text-white bg-[#E41E26] hover:bg-[#C8151B] rounded transition-colors">
                <Upload className="w-3.5 h-3.5" />Upload Data
              </Link>
              <button onClick={handleCompute} disabled={computing}
                className="flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium text-[#555555] hover:text-[#111111] border border-[#E5E5E5] hover:border-[#CCCCCC] rounded transition-colors disabled:opacity-50">
                {computing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
                {computing ? "Computing…" : "Compute Anyway"}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
