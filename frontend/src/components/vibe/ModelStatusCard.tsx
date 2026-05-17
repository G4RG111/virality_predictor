"use client";

import { useEffect, useState, useCallback } from "react";
import { Brain, CheckCircle2, Loader2, RefreshCw, Zap } from "lucide-react";
import { scoring } from "@/lib/api-client";
import type { ModelStatus } from "@/lib/types";

export function ModelStatusCard() {
  const [status, setStatus] = useState<ModelStatus | null>(null);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const s = await scoring.getModelStatus();
      setStatus(s);
    } catch {
      // silently ignore if backend unavailable
    }
  }, []);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const handleTrain = async () => {
    setTraining(true);
    setError(null);
    try {
      await scoring.triggerTraining();
      const poll = async () => {
        const s = await scoring.getModelStatus();
        setStatus(s);
        if (!s.trained) setTimeout(poll, 3000);
        else setTraining(false);
      };
      setTimeout(poll, 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Training failed");
      setTraining(false);
    }
  };

  if (!status) return null;

  return (
    <div className="rounded-lg border border-white/[0.06] bg-[#0d0d1f] p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <Brain className="w-4 h-4 text-violet-400 flex-shrink-0" />
          <span className="text-[13px] font-semibold text-[#c0c0e0]">XGBoost Virality Model</span>
          {status.trained && (
            <span className="flex items-center gap-1 text-[11px] bg-emerald-500/[0.1] text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full">
              <CheckCircle2 className="w-2.5 h-2.5" />
              Trained
            </span>
          )}
        </div>
        <button
          onClick={handleTrain}
          disabled={training}
          className="flex items-center gap-1.5 text-[12px] px-3 py-1.5 rounded-md border border-white/[0.08] text-[#7070a0] hover:text-[#a0a0c0] hover:border-white/[0.14] font-medium transition-colors disabled:opacity-40"
        >
          {training ? (
            <><Loader2 className="w-3 h-3 animate-spin" /> Training…</>
          ) : status.trained ? (
            <><RefreshCw className="w-3 h-3" /> Retrain</>
          ) : (
            <><Zap className="w-3 h-3" /> Train Model</>
          )}
        </button>
      </div>

      {status.trained ? (
        <div className="flex gap-7">
          <Stat label="AUC" value={status.auc != null ? status.auc.toFixed(3) : "—"} />
          <Stat label="Samples" value={String(status.n_samples ?? "—")} />
          <Stat label="Viral" value={String(status.n_viral ?? "—")} />
          <Stat label="Labeled" value={String(status.n_labeled_products)} />
        </div>
      ) : (
        <p className="text-[12px] text-[#5a5a80]">
          {training
            ? `Auto-labeling ${status.n_labeled_products} products and training…`
            : `${status.n_labeled_products} products ready for auto-labeling. Click "Train Model" to start.`}
        </p>
      )}

      {error && (
        <p className="text-[12px] text-red-400 mt-3 bg-red-500/[0.08] rounded-md px-3 py-1.5">
          {error}
        </p>
      )}

      {status.trained && status.trained_at && (
        <p className="text-[11px] text-[#3a3a55] mt-4 border-t border-white/[0.04] pt-3">
          Last trained{" "}
          {new Date(status.trained_at).toLocaleString("en-US", {
            month: "short", day: "numeric", year: "numeric",
            hour: "2-digit", minute: "2-digit",
          })}
        </p>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xl font-bold text-white tabular-nums">{value}</p>
      <p className="text-[10px] tracking-[0.12em] uppercase text-[#3a3a55] mt-0.5">{label}</p>
    </div>
  );
}
