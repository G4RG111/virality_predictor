/**
 * Typed API client for the VIBE FastAPI backend.
 * All API calls go through this module — never fetch directly in components.
 */

import type {
  Product,
  VibeScore,
  ShapExplanation,
  WaterfallEntry,
  KeyDriversResponse,
  IngestionJob,
  UploadResponse,
  LeaderboardEntry,
  HackabilityFeedResponse,
  BreakoutHack,
  ReviewRow,
  SearchResult,
  ModelStatus,
  SocialSignalResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const V1 = `${BASE}/api/v1`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${V1}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ error: "unknown" }));
    throw new Error(detail?.detail?.error || detail?.detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Products ─────────────────────────────────────────────────────────────────

export const products = {
  list: (params?: { market?: string; category?: string; score_band?: string }) =>
    request<Product[]>(`/products?${new URLSearchParams(params as Record<string, string>)}`),

  get: (id: string) => request<Product>(`/products/${id}`),

  create: (data: Partial<Product>) =>
    request<Product>("/products", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Product>) =>
    request<Product>(`/products/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  vibeHistory: (id: string) =>
    request<{ product_id: string; history: VibeScore[] }>(`/products/${id}/vibe-history`),
};

// ── Scoring ───────────────────────────────────────────────────────────────────

export const scoring = {
  compute: (productId: string) =>
    request<{ message: string; product_id: string; review_count: number }>(
      `/scoring/compute/${productId}`,
      { method: "POST" },
    ),

  leaderboard: () => request<LeaderboardEntry[]>("/scoring/leaderboard"),

  compare: (productIds: string[]) =>
    request<{ products: VibeScore[] }>("/scoring/compare", {
      method: "POST",
      body: JSON.stringify({ product_ids: productIds }),
    }),

  getModelStatus: () => request<ModelStatus>("/scoring/model-status"),

  triggerTraining: () =>
    request<{ message: string; status: string }>("/scoring/train", { method: "POST" }),
};

// ── Ingestion ─────────────────────────────────────────────────────────────────

export const ingestion = {
  uploadIhut: (productId: string, file: File): Promise<UploadResponse> => {
    const form = new FormData();
    form.append("product_id", productId);
    form.append("file", file);
    return fetch(`${V1}/ingestion/upload/ihut`, { method: "POST", body: form })
      .then((r) => r.json());
  },

  uploadReviews: (productId: string, file: File): Promise<UploadResponse> => {
    const form = new FormData();
    form.append("product_id", productId);
    form.append("file", file);
    return fetch(`${V1}/ingestion/upload/reviews`, { method: "POST", body: form })
      .then((r) => r.json());
  },

  getJob: (jobId: string) => request<IngestionJob>(`/ingestion/jobs/${jobId}`),

  listJobs: (productId?: string) =>
    request<IngestionJob[]>(`/ingestion/jobs${productId ? `?product_id=${productId}` : ""}`),

  fetchAmazon: (productId: string, asin?: string): Promise<UploadResponse> => {
    const qs = asin ? `?asin=${encodeURIComponent(asin)}` : "";
    return request<UploadResponse>(`/ingestion/fetch/amazon/${productId}${qs}`, { method: "POST" });
  },
};

// ── Explainability ────────────────────────────────────────────────────────────

export const explain = {
  shap: (productId: string) => request<ShapExplanation>(`/explain/${productId}/shap`),
  waterfall: (productId: string) => request<WaterfallEntry[]>(`/explain/${productId}/shap/waterfall`),
  keyDrivers: (productId: string) => request<KeyDriversResponse>(`/explain/${productId}/key-drivers`),
  evidence: (productId: string) =>
    request<Array<{ dimension: string; display_name: string; quotes: string[]; signal_count: number }>>(
      `/explain/${productId}/evidence`,
    ),
};

// ── Trends ────────────────────────────────────────────────────────────────────

export const trends = {
  product: (productId: string) =>
    request<{ product_id: string; trend: Array<{ computed_at: string; vibe_score: number; score_band: string }> }>(
      `/trends/${productId}`,
    ),
  market: (market: string) => request<unknown>(`/trends/market/${market}`),
  category: (category: string) => request<unknown>(`/trends/category/${category}`),
};

// ── Reviews ───────────────────────────────────────────────────────────────────

export const reviews = {
  list: (
    productId: string,
    params?: { source?: string; min_rating?: number; max_rating?: number; market?: string; limit?: number; offset?: number },
  ) => {
    const qs = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => v != null && qs.set(k, String(v)));
    return request<{ total: number; offset: number; limit: number; reviews: ReviewRow[] }>(
      `/reviews/${productId}?${qs}`,
    );
  },

  search: (productId: string, q: string, topK = 20) =>
    request<{ query: string; results: SearchResult[] }>(
      `/reviews/${productId}/search?q=${encodeURIComponent(q)}&top_k=${topK}`,
    ),

  stats: (productId: string) =>
    request<{ total: number; embedded: number; avg_rating: number | null; by_source: Record<string, number>; by_market: Record<string, number> }>(
      `/reviews/${productId}/stats`,
    ),
};

// ── Social Signals ────────────────────────────────────────────────────────────

export const social = {
  get: (productId: string) => request<SocialSignalResponse>(`/social/${productId}`),
  refresh: (productId: string) =>
    request<SocialSignalResponse>(`/social/${productId}/refresh`, { method: "POST" }),
};

// ── Hackability ───────────────────────────────────────────────────────────────

// ── Brief Analysis ────────────────────────────────────────────────────────────

export const briefAnalysis = {
  analyze: (data: {
    product_name: string;
    description?: string;
    category?: string;
    price?: string;
    target_audience?: string;
    tags?: string[];
    demo_mode?: boolean;
  }): Promise<import("./types").BriefAnalysisResult> => {
    const form = new FormData();
    form.append("product_name", data.product_name);
    form.append("description", data.description || "");
    if (data.category) form.append("category", data.category);
    if (data.price) form.append("price", data.price);
    if (data.target_audience) form.append("target_audience", data.target_audience);
    form.append("tags", JSON.stringify(data.tags || []));
    form.append("demo_mode", String(data.demo_mode ?? false));

    return fetch(`${V1}/analyze/brief`, { method: "POST", body: form }).then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    });
  },
};

// ── Hackability ───────────────────────────────────────────────────────────────

export const hackability = {
  feed: (productId: string) => request<HackabilityFeedResponse>(`/hackability/${productId}/feed`),
  velocity: (productId: string) => request<unknown>(`/hackability/${productId}/velocity`),
  breakout: (productId: string, threshold?: number) =>
    request<{ product_id: string; breakout_hacks: BreakoutHack[] }>(
      `/hackability/${productId}/breakout${threshold ? `?threshold=${threshold}` : ""}`,
    ),
  compare: (productIds: string[]) =>
    request<unknown>(`/hackability/compare?product_ids=${productIds.join(",")}`),
};
