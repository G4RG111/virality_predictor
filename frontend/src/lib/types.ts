// ── Core domain types ────────────────────────────────────────────────────────

export type ScoreBand = "low" | "moderate" | "high" | "viral";
export type ConfidenceLevel = "low" | "medium" | "high";
export type SignalDirection = "positive" | "negative" | "neutral";

export interface Product {
  id: string;
  name: string;
  sku: string | null;
  category: string | null;
  launch_date: string | null;
  market: string | null;
  price_usd: number | null;
  msrp_usd: number | null;
  description: string | null;
  asin: string | null;
  created_at: string;
  current_vibe_score?: number | null;
  score_band?: ScoreBand | null;
  confidence?: ConfidenceLevel | null;
}

export interface DimensionScore {
  dimension: string;
  normalized_score: number;     // 0–100
  weight: number;               // 0.0–1.0
  weighted_contribution: number;
  top_signals: SignalEntry[] | null;
  feature_vector: Record<string, number> | null;
  evidence_texts: string[] | null;
}

export interface VibeScore {
  id: string;
  product_id: string;
  vibe_score: number;
  score_band: ScoreBand;
  confidence: ConfidenceLevel;
  confidence_value: number;
  baseline_score: number | null;
  model_version: string;
  ml_score: number | null;
  ml_model_version: string | null;
  computed_at: string;
  is_current: boolean;
  dimension_scores: DimensionScore[];
}

export interface ModelStatus {
  trained: boolean;
  model_version?: string;
  trained_at?: string;
  auc?: number;
  n_samples?: number;
  n_viral?: number;
  n_labeled_products: number;
  error?: string;
}

export interface SignalEntry {
  type: string;
  value: string;
  confidence: number;
}

// ── Explainability types ──────────────────────────────────────────────────────

export interface ShapContribution {
  dimension: string;
  display_name: string;
  shap_value: number;
  feature_value: number;
  feature_value_display: string;
  direction: SignalDirection;
  rank: number;
}

export interface ShapExplanation {
  product_id: string;
  vibe_score: number;
  baseline_score: number;
  narrative: string;
  top_positive_drivers: string[];
  top_negative_drivers: string[];
  model_version: string;
  contributions: ShapContribution[];
}

export interface WaterfallEntry {
  label: string;
  value: number;
  start?: number;
  end?: number;
  cumulative: number;
  type: "baseline" | "positive" | "negative" | "neutral" | "total";
  feature_display?: string;
}

export interface KeyDriver {
  rank: number;
  dimension: string;
  impact: string;
  reason: string;
  strength: "strong" | "moderate" | "slight";
}

export interface KeyDriversResponse {
  positive_drivers: KeyDriver[];
  negative_drivers: KeyDriver[];
  narrative: string;
}

// ── Review types ──────────────────────────────────────────────────────────────

export interface ReviewRow {
  id: string;
  source: string;
  review_text: string;
  rating: number | null;
  review_date: string | null;
  market: string | null;
  verified_purchase: boolean;
  helpful_votes: number;
  reviewer_type: string | null;
  has_embedding: boolean;
}

export interface SearchResult {
  review_id: string;
  text: string;
  score: number;
  source: string;
  rating: number | null;
  review_date: string | null;
}

// ── Ingestion types ───────────────────────────────────────────────────────────

export interface IngestionJob {
  id: string;
  product_id: string;
  source_type: string;
  source_file_name: string | null;
  status: "queued" | "processing" | "completed" | "failed";
  record_count: number | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface UploadResponse {
  job_id: string;
  product_id: string;
  source_type: string;
  status: string;
  message: string;
}

// ── Hackability types ─────────────────────────────────────────────────────────

export interface HackCluster {
  cluster_id: number;
  quote_count: number;
  sample_quotes: string[];
  matched_phrases: string[];
}

export interface HackabilityFeedResponse {
  product_id: string;
  total_hack_mentions: number;
  total_reviews: number;
  hack_mention_rate: number;
  hack_clusters: HackCluster[];
}

export interface BreakoutHack {
  phrase: string;
  mention_count: number;
  mention_rate: number;
  sample_quotes: string[];
  is_breakout: boolean;
}

// ── Trends ───────────────────────────────────────────────────────────────────

export interface TrendPoint {
  computed_at: string;
  vibe_score: number;
  score_band: ScoreBand;
  confidence: ConfidenceLevel;
}

export interface LeaderboardEntry {
  rank: number;
  product_id: string;
  product_name: string;
  market: string | null;
  vibe_score: number;
  score_band: ScoreBand;
  confidence: ConfidenceLevel;
}

// ── UI utility types ──────────────────────────────────────────────────────────

export interface SocialSignalResponse {
  product_id: string;
  trend_score: number;
  reddit_score: number;
  reddit_sentiment: number;
  mention_count: number;
  top_posts: string[];
  cached: boolean;
  fetched_at: string | null;
}

export const DIMENSION_LABELS: Record<string, string> = {
  hackability: "Performative Utility",
  emotional_intensity: "Emotional Pull",
  shareability: "Social Currency",
  novelty: "Novelty Density",
  creator_friendliness: "Creator Magnetism",
  review_momentum: "Momentum",
  recommendation_intent: "Recommendation Energy",
  price_wow: "Value Surprise",
  social_buzz: "Social Buzz",
};

export const DIMENSION_DESCRIPTIONS: Record<string, string> = {
  hackability: "Community-discovered alternative uses — people doing unexpected things publicly",
  emotional_intensity: "Obsession language, intensity signals, emotional peak moments",
  shareability: "Platform mentions, show-others intent, social sharing behaviour",
  novelty: "First-of-its-kind signals, semantic distance from category norms",
  creator_friendliness: "Content creation intent, visual appeal, demo-worthy moments",
  review_momentum: "Review velocity and rating trajectory over time",
  recommendation_intent: "Word-of-mouth energy, gifting intent, explicit recommendations",
  price_wow: "Value-surprise signals — 'worth every penny' moments",
  social_buzz: "External social signal: Google Trends + Reddit mentions",
};

export const BAND_COLORS: Record<ScoreBand, string> = {
  low: "#9CA3AF",
  moderate: "#D97706",
  high: "#059669",
  viral: "#7C3AED",
};

export const BAND_BG: Record<ScoreBand, string> = {
  low: "#F3F4F6",
  moderate: "#FFFBEB",
  high: "#ECFDF5",
  viral: "#F5F3FF",
};

export const BAND_LABELS: Record<ScoreBand, string> = {
  low: "Low Potential",
  moderate: "Moderate",
  high: "High Potential",
  viral: "Viral",
};

// ── Brief Analysis types ──────────────────────────────────────────────────────

export type ViralClassification = "VIRAL_READY" | "VIRAL_POSSIBLE" | "NON_VIRAL";

export interface BriefSignalDimensions {
  emotional_pull: number;
  creator_magnetism: number;
  novelty: number;
  social_currency: number;
  visual_demonstrability: number;
  friction: number;
  performative_utility: number;
  recommendation_energy: number;
}

export interface BriefAnalysisResult {
  vibe_score: number;
  classification: ViralClassification;
  culture_score: number;
  memory_score: number;
  top_matching_clusters: string[];
  trend_alignment_reason: string;
  closest_viral_archetype: string;
  why_viral: string[];
  why_fail: string[];
  consumer_narrative: string;
  consumer_language: string[];
  signal_dimensions: BriefSignalDimensions;
}

export interface BriefFormData {
  product_name: string;
  category: string;
  description: string;
  price: string;
  target_audience: string;
  tags: string[];
  demo_mode: boolean;
}

export const FEATURE_TAGS = [
  "aesthetic",
  "portable",
  "creator-friendly",
  "ritual-based",
  "compact",
  "luxury-coded",
  "giftable",
  "productivity",
  "novelty-driven",
] as const;

export type FeatureTag = (typeof FEATURE_TAGS)[number];

export const BRIEF_CATEGORIES = [
  "Blender", "Air Purifier", "Vacuum", "Hair Care", "Food Processor",
  "Coffee", "Kitchen", "Beverage", "Personal Care", "Other",
] as const;
