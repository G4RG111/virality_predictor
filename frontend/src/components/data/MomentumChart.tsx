"use client";

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

interface DataPoint {
  date: string;
  count: number;
}

interface Props {
  data: DataPoint[];
  height?: number;
  color?: string;
}

export function MomentumChart({ data, height = 140, color = "#3b82f6" }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
        <defs>
          <linearGradient id="momentumGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" vertical={false} />
        <XAxis dataKey="date" tick={{ fill: "#8888aa", fontSize: 9 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: "#8888aa", fontSize: 9 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ background: "#1a1a2e", border: "1px solid #2a2a45", borderRadius: 8 }}
          labelStyle={{ color: "#aaaacc", fontSize: 10 }}
        />
        <Area type="monotone" dataKey="count" stroke={color} fill="url(#momentumGrad)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
