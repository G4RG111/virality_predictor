"use client";

import type { ScoreBand } from "@/lib/types";
import { getBandColor } from "@/lib/utils";

interface Props {
  score: number;
  band: ScoreBand;
  size?: number;
  showLabel?: boolean;
}

const RADIUS = 52;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

// VIBE scores top out at ~15 in current calibration (viral ≥ 11.0)
const VIBE_DISPLAY_MAX = 15;

export function VibeScoreGauge({ score, band, size = 140, showLabel = true }: Props) {
  const clampedScore = Math.min(VIBE_DISPLAY_MAX, Math.max(0, score));
  const offset = CIRCUMFERENCE * (1 - clampedScore / VIBE_DISPLAY_MAX);
  const color = getBandColor(band);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 120 120">
        {/* Background ring */}
        <circle
          cx="60" cy="60" r={RADIUS}
          fill="none"
          stroke="#2a2a45"
          strokeWidth="10"
        />
        {/* Score arc */}
        <circle
          cx="60" cy="60" r={RADIUS}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          transform="rotate(-90 60 60)"
          style={{ transition: "stroke-dashoffset 1.2s ease-out" }}
        />
        {/* Score text */}
        <text
          x="60" y="58"
          textAnchor="middle"
          fill="white"
          fontSize="20"
          fontWeight="700"
          fontFamily="Inter, system-ui, sans-serif"
        >
          {score.toFixed(1)}
        </text>
        <text
          x="60" y="72"
          textAnchor="middle"
          fill="#8888aa"
          fontSize="9"
          fontFamily="Inter, system-ui, sans-serif"
        >
          VIBE
        </text>
      </svg>
      {showLabel && (
        <div
          className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-semibold tracking-wider uppercase"
          style={{ color }}
        >
          {band}
        </div>
      )}
    </div>
  );
}
