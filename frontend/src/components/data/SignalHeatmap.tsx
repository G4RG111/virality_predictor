"use client";

import type { DimensionScore } from "@/lib/types";
import { DIMENSION_LABELS } from "@/lib/types";
import { getBandColor } from "@/lib/utils";

interface Props {
  dimensions: DimensionScore[];
}

function getIntensityColor(score: number): string {
  if (score >= 70) return "#8b5cf6";
  if (score >= 50) return "#3b82f6";
  if (score >= 30) return "#f59e0b";
  return "#64748b";
}

export function SignalHeatmap({ dimensions }: Props) {
  return (
    <div className="grid gap-2">
      {dimensions.map((d) => {
        const color = getIntensityColor(d.normalized_score);
        const width = `${d.normalized_score}%`;

        return (
          <div key={d.dimension} className="group">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400 group-hover:text-white transition-colors">
                {DIMENSION_LABELS[d.dimension] ?? d.dimension}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-semibold" style={{ color }}>
                  {d.normalized_score.toFixed(1)}
                </span>
                <span className="text-xs text-slate-600">
                  ×{(d.weight * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            <div className="h-1.5 rounded-full bg-[#2a2a45] overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width, backgroundColor: color }}
              />
            </div>
            {d.top_signals && d.top_signals.length > 0 && (
              <div className="mt-1 hidden group-hover:flex flex-wrap gap-1">
                {d.top_signals.slice(0, 3).map((s, i) => (
                  <span key={i} className="text-[10px] bg-[#1a1a2e] border border-[#2a2a45] text-slate-500 px-1.5 py-0.5 rounded">
                    {s.value}
                  </span>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
