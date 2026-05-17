"use client";

import { use, useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { PageShell } from "@/components/layout/PageShell";
import { VibeExplainPanel } from "@/components/vibe/VibeExplainPanel";
import type { WaterfallEntry, KeyDriversResponse } from "@/lib/types";
import { explain } from "@/lib/api-client";

export default function ExplainabilityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [waterfall, setWaterfall] = useState<WaterfallEntry[] | null>(null);
  const [drivers, setDrivers] = useState<KeyDriversResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([explain.waterfall(id), explain.keyDrivers(id)])
      .then(([wf, kd]) => { setWaterfall(wf); setDrivers(kd); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <PageShell title="SHAP Explainability">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
        </div>
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell title="SHAP Explainability">
        <div className="rounded-lg bg-red-500/[0.08] border border-red-500/20 p-5 text-[13px] text-red-400">
          {error === "no_score_computed"
            ? "No VIBE score computed yet. Go to the product page and click 'Compute VIBE' first."
            : error}
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell
      title="SHAP Explainability"
      subtitle="Why this product scores the way it does — feature contribution breakdown"
    >
      <div className="grid grid-cols-3 gap-6">
        {/* Waterfall + narrative */}
        <div className="col-span-2">
          {waterfall && drivers && (
            <VibeExplainPanel waterfall={waterfall} narrative={drivers.narrative} />
          )}
        </div>

        {/* Key drivers sidebar */}
        <div className="space-y-3">
          {drivers && (
            <>
              <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/[0.05] p-4">
                <h3 className="text-[10px] font-semibold tracking-[0.15em] uppercase text-emerald-500 mb-3">
                  Positive Drivers
                </h3>
                <div className="space-y-3">
                  {drivers.positive_drivers.map((d) => (
                    <div key={d.dimension} className="flex items-start gap-2.5">
                      <span className="text-emerald-400 text-[12px] font-mono mt-0.5 flex-shrink-0">{d.impact}</span>
                      <div>
                        <div className="text-[12px] font-medium text-[#c0c0e0]">{d.dimension}</div>
                        <div className="text-[11px] text-[#5a5a80]">{d.reason}</div>
                      </div>
                    </div>
                  ))}
                  {drivers.positive_drivers.length === 0 && (
                    <p className="text-[12px] text-[#4a4a70]">No significant positive drivers.</p>
                  )}
                </div>
              </div>
              <div className="rounded-lg border border-red-500/20 bg-red-500/[0.05] p-4">
                <h3 className="text-[10px] font-semibold tracking-[0.15em] uppercase text-red-400 mb-3">
                  Limiting Factors
                </h3>
                <div className="space-y-3">
                  {drivers.negative_drivers.map((d) => (
                    <div key={d.dimension} className="flex items-start gap-2.5">
                      <span className="text-red-400 text-[12px] font-mono mt-0.5 flex-shrink-0">{d.impact}</span>
                      <div>
                        <div className="text-[12px] font-medium text-[#c0c0e0]">{d.dimension}</div>
                        <div className="text-[11px] text-[#5a5a80]">{d.reason}</div>
                      </div>
                    </div>
                  ))}
                  {drivers.negative_drivers.length === 0 && (
                    <p className="text-[12px] text-[#4a4a70]">No significant negative drivers.</p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </PageShell>
  );
}
