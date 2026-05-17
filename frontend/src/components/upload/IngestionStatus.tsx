"use client";

import { useEffect, useState } from "react";
import { CheckCircle, XCircle, Loader2, Clock } from "lucide-react";
import type { IngestionJob } from "@/lib/types";
import { ingestion } from "@/lib/api-client";

interface Props {
  jobId: string;
  onComplete?: (job: IngestionJob) => void;
}

export function IngestionStatus({ jobId, onComplete }: Props) {
  const [job, setJob] = useState<IngestionJob | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const j = await ingestion.getJob(jobId);
        setJob(j);
        if (j.status === "completed" || j.status === "failed") {
          onComplete?.(j);
          return;
        }
        timeout = setTimeout(poll, 2000);
      } catch {
        setError("Failed to fetch job status");
      }
    };
    poll();
    return () => clearTimeout(timeout);
  }, [jobId, onComplete]);

  if (error) return (
    <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-[13px] text-red-600">{error}</div>
  );

  if (!job) return (
    <div className="rounded border border-[#E5E5E5] bg-[#F9F9F9] p-4 text-[12px] text-[#BBBBBB] animate-pulse">Loading…</div>
  );

  const status = job.status as "queued" | "processing" | "completed" | "failed";
  const icons = {
    queued: <Clock className="w-4 h-4 text-[#BBBBBB] animate-pulse" />,
    processing: <Loader2 className="w-4 h-4 text-[#E41E26] animate-spin" />,
    completed: <CheckCircle className="w-4 h-4 text-emerald-500" />,
    failed: <XCircle className="w-4 h-4 text-red-500" />,
  };
  const labels = {
    queued: "Queued — waiting to start",
    processing: "Processing data…",
    completed: "Ingestion complete",
    failed: "Ingestion failed",
  };
  const borders = {
    queued: "border-[#E5E5E5]",
    processing: "border-[#E41E26]/20",
    completed: "border-emerald-200",
    failed: "border-red-200",
  };

  return (
    <div className={`rounded border ${borders[status]} bg-white p-4 space-y-1.5`}>
      <div className="flex items-center gap-2.5">
        {icons[status]}
        <span className="text-[13px] font-medium text-[#111111]">{labels[status]}</span>
        {job.record_count != null && status === "completed" && (
          <span className="ml-auto text-[12px] text-emerald-600 font-semibold">
            {job.record_count} records
          </span>
        )}
      </div>
      {job.source_file_name && (
        <p className="text-[11px] text-[#BBBBBB] pl-6 truncate">{job.source_file_name}</p>
      )}
      {job.error_message && (
        <p className="text-[11px] text-red-600 bg-red-50 rounded px-3 py-1.5 ml-6">{job.error_message}</p>
      )}
    </div>
  );
}
