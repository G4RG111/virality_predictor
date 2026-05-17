"use client";

import type { WaterfallEntry } from "@/lib/types";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  ResponsiveContainer, ReferenceLine,
} from "recharts";

interface Props {
  waterfall: WaterfallEntry[];
  narrative: string;
}

export function VibeExplainPanel({ waterfall, narrative }: Props) {
  const barData = waterfall.map((entry) => ({
    name: entry.label,
    value: entry.type === "baseline" || entry.type === "total" ? entry.cumulative : entry.value,
    type: entry.type,
    cumulative: entry.cumulative,
    feature_display: entry.feature_display,
  }));

  const getColor = (type: string) => {
    if (type === "baseline") return "#333350";
    if (type === "total") return "#8b5cf6";
    if (type === "positive") return "#2dd4bf";
    if (type === "negative") return "#f87171";
    return "#4a4a70";
  };

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: typeof barData[0] }> }) => {
    if (!active || !payload?.length) return null;
    const d = payload[0]?.payload;
    return (
      <div className="bg-[#111126] border border-white/[0.1] rounded-lg shadow-xl p-3 text-[12px] max-w-[220px]">
        <p className="text-white font-semibold mb-1">{d.name}</p>
        <p className="text-[#8080a0]">
          {d.type === "baseline" || d.type === "total"
            ? `Score: ${d.value.toFixed(1)}`
            : `Impact: ${d.value >= 0 ? "+" : ""}${d.value.toFixed(1)} pts`}
        </p>
        {d.feature_display && (
          <p className="text-[#5a5a80] mt-1">{d.feature_display}</p>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Narrative */}
      <div className="rounded-lg bg-violet-500/[0.07] border border-violet-500/20 p-4">
        <p className="text-[13px] text-violet-200/80 leading-relaxed">{narrative}</p>
      </div>

      {/* Waterfall chart */}
      <div className="rounded-lg bg-[#0d0d1f] border border-white/[0.06] p-5">
        <h4 className="text-[10px] font-semibold tracking-[0.15em] uppercase text-[#4a4a70] mb-5">
          SHAP Contribution Waterfall
        </h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData} layout="vertical" margin={{ left: 120, right: 40, top: 0, bottom: 0 }}>
            <XAxis
              type="number"
              domain={["auto", "auto"]}
              tick={{ fill: "#3a3a55", fontSize: 9 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              dataKey="name"
              type="category"
              tick={{ fill: "#6868a0", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              width={115}
            />
            <ReferenceLine x={0} stroke="#1e1e35" />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
            <Bar dataKey="value" radius={[0, 3, 3, 0]}>
              {barData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.type)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="flex gap-5 mt-4 justify-center">
          {[["#2dd4bf", "Positive driver"], ["#f87171", "Negative driver"], ["#8b5cf6", "Final score"]].map(([color, label]) => (
            <div key={label} className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ background: color }} />
              <span className="text-[11px] text-[#5a5a80]">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
