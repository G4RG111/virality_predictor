"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { TrendPoint } from "@/lib/types";
import { BAND_COLORS } from "@/lib/types";
import { formatDate } from "@/lib/utils";

interface Props {
  trend: TrendPoint[];
  height?: number;
}

export function VibeTrendLine({ trend, height = 200 }: Props) {
  const data = trend.map((t) => ({
    date: new Date(t.computed_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
    score: t.vibe_score,
    band: t.score_band,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
        <XAxis
          dataKey="date"
          tick={{ fill: "#8888aa", fontSize: 10 }}
          axisLine={{ stroke: "#2a2a45" }}
          tickLine={false}
        />
        <YAxis
          domain={([min, max]: [number, number]) => [Math.max(0, Math.floor(min) - 1), Math.ceil(max) + 1]}
          tick={{ fill: "#8888aa", fontSize: 10 }}
          axisLine={false}
          tickLine={false}
        />
        {/* VIBE band threshold lines */}
        <ReferenceLine y={11} stroke="#8b5cf6" strokeDasharray="4 4" strokeOpacity={0.5} label={{ value: "Viral ≥11", fill: "#8b5cf6", fontSize: 9 }} />
        <ReferenceLine y={7.5} stroke="#3b82f6" strokeDasharray="4 4" strokeOpacity={0.4} label={{ value: "High ≥7.5", fill: "#3b82f6", fontSize: 9 }} />
        <ReferenceLine y={4.5} stroke="#f59e0b" strokeDasharray="4 4" strokeOpacity={0.4} label={{ value: "Moderate ≥4.5", fill: "#f59e0b", fontSize: 9 }} />
        <Tooltip
          contentStyle={{ background: "#1a1a2e", border: "1px solid #2a2a45", borderRadius: 8 }}
          labelStyle={{ color: "#aaaacc" }}
          formatter={(v: number) => [`${v.toFixed(1)} / 100`, "VIBE Score"]}
        />
        <Line
          type="monotone"
          dataKey="score"
          stroke="#8b5cf6"
          strokeWidth={2.5}
          dot={{ fill: "#8b5cf6", r: 3 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
