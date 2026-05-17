"use client";

import { Flame } from "lucide-react";
import type { BreakoutHack } from "@/lib/types";
import { formatPercent } from "@/lib/utils";

interface Props {
  hacks: BreakoutHack[];
}

export function BreakoutHackBadge({ hacks }: Props) {
  if (hacks.length === 0) {
    return (
      <div className="text-sm text-slate-500 py-4 text-center">
        No breakout hacks detected yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {hacks.map((hack) => (
        <div
          key={hack.phrase}
          className="rounded-lg border border-orange-500/30 bg-orange-500/5 p-3"
        >
          <div className="flex items-center gap-2 mb-2">
            <Flame className="w-4 h-4 text-orange-400 flex-shrink-0" />
            <span className="text-sm font-semibold text-orange-300">"{hack.phrase}"</span>
            <span className="ml-auto text-xs text-orange-400/80 font-mono">
              {formatPercent(hack.mention_rate)} of reviews
            </span>
          </div>
          {hack.sample_quotes[0] && (
            <blockquote className="text-xs text-slate-400 italic border-l-2 border-orange-500/30 pl-2 mt-1">
              "{hack.sample_quotes[0].slice(0, 180)}…"
            </blockquote>
          )}
        </div>
      ))}
    </div>
  );
}
