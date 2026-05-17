"use client";

import type { DimensionScore, ScoreBand } from "@/lib/types";
import { DIMENSION_LABELS } from "@/lib/types";
import { getBandColor } from "@/lib/utils";

interface Props {
  dimensions: DimensionScore[];
  band: ScoreBand;
}

export function DimensionBars({ dimensions, band }: Props) {
  const color = getBandColor(band);
  const sorted = [...dimensions].sort((a, b) => b.weight - a.weight);

  return (
    <div className="space-y-5">
      {sorted.map((d) => {
        const pct = Math.min(100, Math.max(0, d.normalized_score));
        const label = DIMENSION_LABELS[d.dimension] ?? d.dimension;
        const weightPct = Math.round(d.weight * 100);
        return (
          <div key={d.dimension}>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[13px] text-[#333333] font-medium">{label}</span>
                <span className="text-[10px] text-[#BBBBBB] font-mono bg-[#F5F5F5] px-1.5 py-0.5 rounded">{weightPct}%</span>
              </div>
              <span
                className="text-[13px] font-semibold tabular-nums"
                style={{ color: pct >= 40 ? color : "#BBBBBB" }}
              >
                {pct.toFixed(0)}
              </span>
            </div>
            <div className="h-1.5 bg-[#F0F0F0] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${pct}%`,
                  backgroundColor: color,
                  opacity: 0.6 + d.weight * 1.5,
                  transition: "width 0.9s cubic-bezier(0.16, 1, 0.3, 1)",
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
