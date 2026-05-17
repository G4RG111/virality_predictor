"use client";

import { Wrench, Zap } from "lucide-react";
import type { HackabilityFeedResponse } from "@/lib/types";
import { formatPercent } from "@/lib/utils";

interface Props {
  data: HackabilityFeedResponse;
}

const CLUSTER_ACCENTS = [
  { border: "border-violet-500/20", bg: "bg-violet-500/[0.05]", quote: "border-violet-500/30", tag: "bg-violet-500/10 text-violet-400 border-violet-500/20" },
  { border: "border-blue-500/20", bg: "bg-blue-500/[0.05]", quote: "border-blue-500/30", tag: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  { border: "border-emerald-500/20", bg: "bg-emerald-500/[0.05]", quote: "border-emerald-500/30", tag: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  { border: "border-amber-500/20", bg: "bg-amber-500/[0.05]", quote: "border-amber-500/30", tag: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
  { border: "border-rose-500/20", bg: "bg-rose-500/[0.05]", quote: "border-rose-500/30", tag: "bg-rose-500/10 text-rose-400 border-rose-500/20" },
  { border: "border-cyan-500/20", bg: "bg-cyan-500/[0.05]", quote: "border-cyan-500/30", tag: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20" },
];

export function HackabilityFeed({ data }: Props) {
  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <div className="flex items-center gap-6 rounded-lg border border-white/[0.06] bg-[#0d0d1f] p-4">
        <div className="flex items-center gap-2.5">
          <Wrench className="w-3.5 h-3.5 text-violet-400 flex-shrink-0" />
          <span className="text-sm font-bold text-white tabular-nums">{data.total_hack_mentions}</span>
          <span className="text-[11px] text-[#5a5a80]">hack mentions</span>
        </div>
        <div className="h-3 w-px bg-white/[0.06]" />
        <div className="flex items-center gap-2.5">
          <Zap className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
          <span className="text-sm font-bold text-white tabular-nums">{formatPercent(data.hack_mention_rate)}</span>
          <span className="text-[11px] text-[#5a5a80]">of reviews</span>
        </div>
        <div className="h-3 w-px bg-white/[0.06]" />
        <div className="flex items-center gap-2.5">
          <span className="text-sm font-bold text-white tabular-nums">{data.hack_clusters.length}</span>
          <span className="text-[11px] text-[#5a5a80]">use-case clusters</span>
        </div>
      </div>

      {data.hack_clusters.length === 0 ? (
        <div className="text-center py-10 text-[#4a4a70] text-[13px] border border-dashed border-white/[0.06] rounded-lg">
          No hackability signals detected yet.
        </div>
      ) : (
        <div className="grid gap-3">
          {data.hack_clusters.map((cluster, i) => {
            const accent = CLUSTER_ACCENTS[i % CLUSTER_ACCENTS.length];
            return (
              <div key={cluster.cluster_id} className={`rounded-lg border ${accent.border} ${accent.bg} p-4`}>
                <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                  <div className="flex items-center gap-2.5">
                    <span className="text-[10px] font-mono text-[#4a4a70]">USE #{cluster.cluster_id + 1}</span>
                    <span className="text-[11px] text-[#5a5a80]">{cluster.quote_count} reviews</span>
                  </div>
                  {cluster.matched_phrases.length > 0 && (
                    <div className="flex gap-1.5 flex-wrap">
                      {cluster.matched_phrases.slice(0, 3).map((p) => (
                        <span key={p} className={`text-[11px] px-2 py-0.5 rounded-full border ${accent.tag}`}>
                          {p}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  {cluster.sample_quotes.slice(0, 3).map((q, qi) => (
                    <blockquote key={qi} className={`text-[12px] text-[#7070a0] italic border-l-2 ${accent.quote} pl-3 leading-relaxed`}>
                      &ldquo;{q.length > 200 ? q.slice(0, 200) + "…" : q}&rdquo;
                    </blockquote>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
