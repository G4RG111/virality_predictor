"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { DimensionScore } from "@/lib/types";
import { DIMENSION_LABELS } from "@/lib/types";

interface Props {
  dimensions: DimensionScore[];
  color?: string;
  label?: string;
}

export function VibeDimensionRadar({ dimensions, color = "#8b5cf6", label }: Props) {
  const data = dimensions.map((d) => ({
    subject: DIMENSION_LABELS[d.dimension] ?? d.dimension,
    score: d.normalized_score,
    fullMark: 100,
  }));

  return (
    <div className="w-full">
      {label && <p className="text-xs text-slate-400 text-center mb-2">{label}</p>}
      <ResponsiveContainer width="100%" height={320}>
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#2a2a45" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#9999bb", fontSize: 11, fontFamily: "Inter, sans-serif" }}
          />
          <Radar
            name="VIBE"
            dataKey="score"
            stroke={color}
            fill={color}
            fillOpacity={0.15}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{ background: "#1a1a2e", border: "1px solid #2a2a45", borderRadius: 8 }}
            labelStyle={{ color: "#ffffff" }}
            formatter={(v: number) => [`${v.toFixed(1)} / 100`, "Score"]}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
