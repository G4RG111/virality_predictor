"use client";

import Link from "next/link";
import type { Product } from "@/lib/types";
import { BAND_LABELS, BAND_COLORS } from "@/lib/types";
import { formatScore } from "@/lib/utils";
import { VibeScoreGauge } from "./VibeScoreGauge";

interface Props {
  product: Product;
  trend?: "up" | "down" | "stable";
}

export function VibeScoreCard({ product, trend: _trend }: Props) {
  const band = product.score_band ?? "low";
  const score = product.current_vibe_score ?? null;

  return (
    <Link
      href={`/products/${product.id}`}
      className="block rounded-lg border border-white/[0.06] bg-[#0d0d1f] p-5 hover:border-white/[0.12] hover:bg-[#0f0f24] transition-all duration-150 group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0 pr-3">
          <h3 className="text-[13px] font-semibold text-[#d0d0f0] truncate group-hover:text-white transition-colors">
            {product.name}
          </h3>
          <div className="flex items-center gap-1.5 mt-1 flex-wrap">
            {product.market && <span className="text-[11px] text-[#3d3d60]">{product.market}</span>}
            {product.category && <span className="text-[11px] text-[#2a2a45]">· {product.category}</span>}
          </div>
        </div>
        {score != null && (
          <span
            className="text-[10px] font-semibold tracking-wider uppercase flex-shrink-0"
            style={{ color: BAND_COLORS[band] }}
          >
            {BAND_LABELS[band]}
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        {score != null ? (
          <>
            <VibeScoreGauge score={score} band={band} size={72} showLabel={false} />
            <div>
              <div className="text-2xl font-bold text-white tabular-nums leading-none">
                {formatScore(score)}
              </div>
              <div className="text-[10px] tracking-[0.12em] uppercase text-[#3a3a55] mt-1.5">VIBE Score</div>
              {product.confidence && (
                <div className="text-[11px] text-[#3a3a55] mt-1">
                  {product.confidence} confidence
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-[72px] h-[72px] rounded-full border border-dashed border-white/[0.08] flex items-center justify-center flex-shrink-0">
              <span className="text-[10px] text-[#2a2a45]">—</span>
            </div>
            <div>
              <div className="text-[13px] text-[#3a3a55]">Not scored</div>
              <div className="text-[11px] text-[#2a2a45] mt-0.5">Upload data to score</div>
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}
