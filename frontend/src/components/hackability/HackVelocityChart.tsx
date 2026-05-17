"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

interface MonthlyPoint {
  month: string;
  hack_mentions: number;
}

interface Props {
  data: MonthlyPoint[];
  height?: number;
}

export function HackVelocityChart({ data, height = 180 }: Props) {
  if (!data.length) {
    return <div className="text-sm text-slate-500 text-center py-8">No velocity data available.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" vertical={false} />
        <XAxis dataKey="month" tick={{ fill: "#8888aa", fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: "#8888aa", fontSize: 10 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ background: "#1a1a2e", border: "1px solid #2a2a45", borderRadius: 8 }}
          labelStyle={{ color: "#aaaacc", fontSize: 11 }}
          formatter={(v: number) => [v, "Hack Mentions"]}
        />
        <Bar dataKey="hack_mentions" fill="#8b5cf6" radius={[4, 4, 0, 0]} opacity={0.8} />
      </BarChart>
    </ResponsiveContainer>
  );
}
