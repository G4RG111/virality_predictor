import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { ScoreBand } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getBandColor(band: ScoreBand): string {
  const colors: Record<ScoreBand, string> = {
    low: "#9CA3AF",
    moderate: "#D97706",
    high: "#059669",
    viral: "#7C3AED",
  };
  return colors[band] ?? "#9CA3AF";
}

export function getBandBg(band: ScoreBand): string {
  const classes: Record<ScoreBand, string> = {
    low: "bg-gray-50 text-gray-500 border-gray-200",
    moderate: "bg-amber-50 text-amber-700 border-amber-200",
    high: "bg-emerald-50 text-emerald-700 border-emerald-200",
    viral: "bg-violet-50 text-violet-700 border-violet-200",
  };
  return classes[band] ?? classes.low;
}

export function formatScore(score: number | null | undefined): string {
  if (score == null) return "—";
  return score.toFixed(1);
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function shapeShapValue(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(1)} pts`;
}
