"use client";

import { useEffect, useState } from "react";
import { RefreshCw, Loader2, TrendingUp, MessageSquare } from "lucide-react";
import { social as socialApi } from "@/lib/api-client";
import type { SocialSignalResponse } from "@/lib/types";

function ScoreBar({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center">
        <span className="text-[11px] text-[#5a5a80]">{label}</span>
        <span className="text-[11px] font-semibold text-[#8080a0] tabular-nums">{Math.round(value * 100)}</span>
      </div>
      <div className="h-1 rounded-full bg-white/[0.05] overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${value * 100}%`, background: color }}
        />
      </div>
    </div>
  );
}

export function SocialBuzzPanel({ productId }: { productId: string }) {
  const [data, setData] = useState<SocialSignalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    socialApi.get(productId)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [productId]);

  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      const fresh = await socialApi.refresh(productId);
      setData(fresh);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40">
        <Loader2 className="w-4 h-4 text-violet-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[10px] font-semibold tracking-[0.15em] uppercase text-[#4a4a70]">Social Buzz Signals</span>
          {data?.cached && (
            <div className="text-[10px] text-[#3a3a55] mt-0.5">
              Cached · {data.fetched_at ? new Date(data.fetched_at).toLocaleString() : "—"}
            </div>
          )}
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-1.5 text-[12px] px-3 py-1.5 rounded-md border border-white/[0.08] text-[#7070a0] hover:text-[#a0a0c0] font-medium transition-colors disabled:opacity-40"
        >
          {refreshing ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
          {refreshing ? "Fetching…" : "Refresh"}
        </button>
      </div>

      {error && (
        <p className="text-[12px] text-red-400 bg-red-500/[0.08] rounded-md px-3 py-2">{error}</p>
      )}

      {!data ? (
        <div className="text-center py-12 border border-dashed border-white/[0.06] rounded-lg">
          <TrendingUp className="w-6 h-6 text-[#2a2a45] mx-auto mb-3" />
          <p className="text-[13px] text-[#4a4a70]">No social data yet.</p>
          <p className="text-[12px] text-[#3a3a55] mt-1">Score this product to fetch Google Trends + Reddit signals.</p>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="mt-3 text-[12px] font-medium text-violet-400 hover:text-violet-300 transition-colors disabled:opacity-40"
          >
            {refreshing ? "Fetching…" : "Fetch now →"}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border border-white/[0.06] bg-[#0d0d1f] p-4 space-y-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-3.5 h-3.5 text-violet-400 flex-shrink-0" />
              <span className="text-[10px] font-semibold tracking-[0.12em] uppercase text-[#4a4a70]">Google Trends</span>
            </div>
            <div className="text-3xl font-bold text-white tabular-nums leading-none">
              {Math.round(data.trend_score * 100)}
              <span className="text-sm font-normal text-[#4a4a70] ml-1">/ 100</span>
            </div>
            <ScoreBar
              value={data.trend_score}
              label="12-month interest"
              color={data.trend_score > 0.5 ? "#8b5cf6" : data.trend_score > 0.25 ? "#3b82f6" : "#4a4a70"}
            />
            <p className="text-[10px] text-[#3a3a55]">Average search interest over the past 12 months</p>
          </div>

          <div className="rounded-lg border border-white/[0.06] bg-[#0d0d1f] p-4 space-y-3">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-3.5 h-3.5 text-orange-400 flex-shrink-0" />
              <span className="text-[10px] font-semibold tracking-[0.12em] uppercase text-[#4a4a70]">Reddit</span>
            </div>
            <div className="text-3xl font-bold text-white tabular-nums leading-none">
              {data.mention_count}
              <span className="text-sm font-normal text-[#4a4a70] ml-1">mentions</span>
            </div>
            <ScoreBar value={data.reddit_score} label="mention density" color="#f97316" />
            <ScoreBar value={data.reddit_sentiment} label="community sentiment" color="#2dd4bf" />
          </div>

          {data.top_posts.length > 0 && (
            <div className="col-span-2 rounded-lg border border-white/[0.06] bg-[#0d0d1f] p-4">
              <h4 className="text-[10px] font-semibold tracking-[0.15em] uppercase text-[#4a4a70] mb-3">Top Community Posts</h4>
              <ul className="space-y-2.5">
                {data.top_posts.slice(0, 5).map((post, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="text-[11px] font-mono text-[#2a2a45] w-4 flex-shrink-0 mt-0.5">#{i + 1}</span>
                    <span className="text-[12px] text-[#6868a0] leading-relaxed">{post}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
