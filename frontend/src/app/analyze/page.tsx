"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Zap, TrendingUp, AlertTriangle, MessageSquare, Users, ArrowRight } from "lucide-react";
import { briefAnalysis } from "@/lib/api-client";
import type { BriefAnalysisResult, BriefFormData, BriefSignalDimensions, ViralClassification } from "@/lib/types";
import { FEATURE_TAGS, BRIEF_CATEGORIES } from "@/lib/types";

// ─── Constants ────────────────────────────────────────────────────────────────

const CLASSIFICATION: Record<
  ViralClassification,
  { label: string; sublabel: string; ringColor: string; badgeColor: string }
> = {
  VIRAL_READY: {
    label: "Viral Ready",
    sublabel: "High cultural momentum detected",
    ringColor: "#7C3AED",
    badgeColor: "#7C3AED",
  },
  VIRAL_POSSIBLE: {
    label: "Viral Possible",
    sublabel: "Cultural signals emerging",
    ringColor: "#5B8CFF",
    badgeColor: "#5B8CFF",
  },
  NON_VIRAL: {
    label: "Non-Viral",
    sublabel: "Low cultural velocity",
    ringColor: "#D0D0D0",
    badgeColor: "#A0A0A0",
  },
};

const SIGNALS: Array<{ key: keyof BriefSignalDimensions; label: string }> = [
  { key: "emotional_pull",         label: "Emotional Pull" },
  { key: "creator_magnetism",      label: "Creator Magnetism" },
  { key: "novelty",                label: "Novelty" },
  { key: "social_currency",        label: "Social Currency" },
  { key: "visual_demonstrability", label: "Visual Demonstrability" },
];

const SIGNAL_KEYWORDS: Record<keyof BriefSignalDimensions, string[]> = {
  emotional_pull:         ["love","obsessed","amazing","incredible","addicted","excited","passionate"],
  creator_magnetism:      ["video","share","content","post","tiktok","aesthetic","visual","creator","reel"],
  novelty:                ["new","never","first","revolutionary","unique","innovative","game-changing"],
  social_currency:        ["everyone","show","impress","status","viral","trending","reaction"],
  visual_demonstrability: ["beautiful","aesthetic","design","look","color","sleek","visual","stunning"],
  friction:               ["complicated","difficult","confusing","hard","frustrating","setup"],
  performative_utility:   ["hack","trick","also use","community","recipe","creative","unexpected"],
  recommendation_energy:  ["must have","need","buy","gift","recommend","worth","get this"],
};

const DEFAULT_SIGNALS: BriefSignalDimensions = {
  emotional_pull: 0.10, creator_magnetism: 0.10, novelty: 0.10,
  social_currency: 0.10, visual_demonstrability: 0.10,
  friction: 0.80, performative_utility: 0.10, recommendation_energy: 0.10,
};

const DEMO: BriefFormData = {
  product_name: "Ninja Matcha Machine",
  category: "Beverage",
  description:
    "A sleek electric matcha frother that creates café-quality lattes at home. " +
    "The aesthetic design photographs beautifully, creators love the visual of the froth forming. " +
    "Community has discovered dozens of alternative recipes — from iced matchas to matcha smoothies. " +
    "People are obsessed and share their morning ritual content constantly.",
  price: "149",
  target_audience: "Aesthetic wellness creators, matcha enthusiasts, morning ritual adopters",
  tags: ["aesthetic", "ritual-based", "creator-friendly", "luxury-coded"],
  demo_mode: true,
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function useCountUp(target: number, duration: number, active: boolean) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!active) { setCount(0); return; }
    let start: number | null = null;
    const raf = requestAnimationFrame(function step(ts) {
      if (start === null) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      setCount(Math.floor((1 - Math.pow(1 - p, 3)) * target));
      if (p < 1) requestAnimationFrame(step);
    });
    return () => cancelAnimationFrame(raf);
  }, [target, duration, active]);
  return count;
}

function computeLiveSignals(text: string): BriefSignalDimensions {
  const t = text.toLowerCase();
  const score = (kws: string[]) => Math.min(0.10 + (kws.filter(k => t.includes(k)).length / Math.max(kws.length * 0.30, 1)) * 0.90, 1.0);
  const inv = (v: number) => Math.min(1.0 - v + 0.10, 1.0);
  return {
    emotional_pull: score(SIGNAL_KEYWORDS.emotional_pull),
    creator_magnetism: score(SIGNAL_KEYWORDS.creator_magnetism),
    novelty: score(SIGNAL_KEYWORDS.novelty),
    social_currency: score(SIGNAL_KEYWORDS.social_currency),
    visual_demonstrability: score(SIGNAL_KEYWORDS.visual_demonstrability),
    friction: inv(score(SIGNAL_KEYWORDS.friction)),
    performative_utility: score(SIGNAL_KEYWORDS.performative_utility),
    recommendation_energy: score(SIGNAL_KEYWORDS.recommendation_energy),
  };
}

// ─── Layout container ─────────────────────────────────────────────────────────

function Container({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={className}
      style={{ maxWidth: "1200px", margin: "0 auto", paddingLeft: "48px", paddingRight: "48px" }}
    >
      {children}
    </div>
  );
}

// ─── Form primitives ──────────────────────────────────────────────────────────

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.2em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "8px" }}>
      {children}
    </p>
  );
}

function TextInput({ value, onChange, placeholder, type = "text" }: {
  value: string; onChange: (v: string) => void; placeholder?: string; type?: string;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full bg-white text-[14px] text-[#0A0A0A] placeholder-[#C0C0C0] focus:outline-none transition-all"
      style={{ border: "1.5px solid #E8E8E8", padding: "14px 16px", borderRadius: "12px", height: "52px" }}
      onFocus={e => { e.currentTarget.style.borderColor = "#7C3AED"; e.currentTarget.style.boxShadow = "0 0 0 3px rgba(124,58,237,0.08)"; }}
      onBlur={e => { e.currentTarget.style.borderColor = "#E8E8E8"; e.currentTarget.style.boxShadow = "none"; }}
    />
  );
}

function SelectInput({ value, onChange, children }: {
  value: string; onChange: (v: string) => void; children: React.ReactNode;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full bg-white text-[14px] text-[#3A3A3A] focus:outline-none cursor-pointer appearance-none transition-all"
      style={{ border: "1.5px solid #E8E8E8", padding: "14px 16px", borderRadius: "12px", height: "52px" }}
      onFocus={e => { e.currentTarget.style.borderColor = "#7C3AED"; e.currentTarget.style.boxShadow = "0 0 0 3px rgba(124,58,237,0.08)"; }}
      onBlur={e => { e.currentTarget.style.borderColor = "#E8E8E8"; e.currentTarget.style.boxShadow = "none"; }}
    >
      {children}
    </select>
  );
}

// ─── Signal Pill ──────────────────────────────────────────────────────────────

function SignalPill({ label, score }: { label: string; score: number }) {
  const level = score < 0.38 ? "low" : score < 0.65 ? "mid" : "high";
  const levelLabel = level === "high" ? "HIGH" : level === "mid" ? "MED" : "LOW";
  const styles = {
    high: { bg: "#F0FDF4", text: "#16A34A", border: "#BBF7D0" },
    mid:  { bg: "#FFFBEB", text: "#D97706", border: "#FDE68A" },
    low:  { bg: "#F9FAFB", text: "#9CA3AF", border: "#E5E7EB" },
  }[level];

  return (
    <div
      className="flex items-center gap-2"
      style={{ background: styles.bg, border: `1px solid ${styles.border}`, borderRadius: "100px", padding: "6px 14px" }}
    >
      <span style={{ fontSize: "12px", fontWeight: 500, color: "#3A3A3A" }}>{label}</span>
      <span style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.1em", color: styles.text }}>{levelLabel}</span>
    </div>
  );
}

// ─── Dimension Row ────────────────────────────────────────────────────────────

function DimensionRow({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
        <span style={{ fontSize: "14px", fontWeight: 500, color: "#3A3A3A" }}>{label}</span>
        <span style={{ fontSize: "16px", fontWeight: 700, color: "#0A0A0A", fontVariantNumeric: "tabular-nums" }}>{pct}</span>
      </div>
      <div style={{ height: "5px", background: "#F0F0F0", borderRadius: "999px", overflow: "hidden" }}>
        <motion.div
          style={{ height: "100%", background: "linear-gradient(90deg, #7C3AED 0%, #5B8CFF 100%)", borderRadius: "999px" }}
          initial={{ width: "0%" }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
    </div>
  );
}

// ─── Radial Score Ring ────────────────────────────────────────────────────────

function RadialScore({
  displayNumber,
  percent,
  active,
  color = "#7C3AED",
}: {
  displayNumber: number | null;
  percent: number;
  active: boolean;
  color?: string;
}) {
  const SIZE = 260;
  const SW = 12;
  const R = (SIZE - SW * 2) / 2;
  const C = 2 * Math.PI * R;

  return (
    <div style={{ position: "relative", width: SIZE, height: SIZE, display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
      <svg width={SIZE} height={SIZE} style={{ position: "absolute", top: 0, left: 0, transform: "rotate(-90deg)" }}>
        <circle cx={SIZE / 2} cy={SIZE / 2} r={R} fill="none" stroke="#F0F0F0" strokeWidth={SW} />
        <motion.circle
          cx={SIZE / 2} cy={SIZE / 2} r={R}
          fill="none"
          stroke={color}
          strokeWidth={SW}
          strokeLinecap="round"
          strokeDasharray={C}
          initial={{ strokeDashoffset: C }}
          animate={{ strokeDashoffset: active ? C * (1 - percent / 100) : C }}
          transition={{ duration: 1.8, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
          style={{ filter: `drop-shadow(0 0 10px ${color}80)` }}
        />
      </svg>
      <div style={{ position: "relative", zIndex: 10, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <AnimatePresence mode="wait">
          <motion.span
            key={String(displayNumber)}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.35 }}
            style={{
              fontFamily: "var(--font-playfair)",
              fontSize: "80px",
              fontWeight: 900,
              lineHeight: 1,
              letterSpacing: "-0.04em",
              color: displayNumber !== null ? "#0A0A0A" : "#E0E0E0",
            }}
          >
            {displayNumber !== null ? displayNumber : "—"}
          </motion.span>
        </AnimatePresence>
        <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.28em", textTransform: "uppercase", color: "#A0A0A0", marginTop: "4px" }}>
          VIBE
        </p>
      </div>
    </div>
  );
}

// ─── Stat Card ────────────────────────────────────────────────────────────────

function StatCard({ label, value, desc }: { label: string; value: number; desc: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      style={{
        background: "white",
        border: "1px solid #E8E8E8",
        borderRadius: "20px",
        boxShadow: "0 2px 16px rgba(0,0,0,0.04)",
        padding: "40px 32px",
        textAlign: "center",
      }}
    >
      <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.2em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "16px" }}>
        {label}
      </p>
      <motion.p
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        style={{
          fontFamily: "var(--font-playfair)",
          fontSize: "56px",
          fontWeight: 900,
          color: "#0A0A0A",
          lineHeight: 1,
          letterSpacing: "-0.03em",
        }}
      >
        {value}
      </motion.p>
      <p style={{ fontSize: "13px", color: "#6B6B6B", marginTop: "12px", lineHeight: 1.5 }}>{desc}</p>
    </motion.div>
  );
}

// ─── Insight Item ─────────────────────────────────────────────────────────────

function InsightItem({ text, type, delay = 0 }: { text: string; type: "viral" | "fail"; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      whileHover={{ y: -1 }}
      style={{
        display: "flex",
        gap: "12px",
        padding: "14px",
        fontSize: "13px",
        lineHeight: 1.6,
        color: "#3A3A3A",
        borderRadius: "10px",
        border: "1px solid #E8E8E8",
        background: type === "viral" ? "white" : "#FAFAFA",
        marginBottom: "8px",
        cursor: "default",
      }}
    >
      <div
        style={{
          flexShrink: 0,
          width: "3px",
          alignSelf: "stretch",
          borderRadius: "999px",
          background: type === "viral" ? "#7C3AED" : "#D0D0D0",
          marginTop: "2px",
        }}
      />
      <span>{text}</span>
    </motion.div>
  );
}

// ─── Quote Card ───────────────────────────────────────────────────────────────

function QuoteCard({ quote, index }: { quote: string; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 + index * 0.08, duration: 0.35 }}
      whileHover={{ y: -3, boxShadow: "0 10px 28px rgba(0,0,0,0.08)" }}
      style={{
        background: "white",
        border: "1px solid #F0F0F0",
        borderRadius: "16px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.04)",
        padding: "24px",
        position: "relative",
        overflow: "hidden",
        cursor: "default",
        transition: "all 0.2s ease",
      }}
    >
      <span
        style={{
          position: "absolute",
          top: "6px",
          left: "16px",
          fontFamily: "var(--font-playfair)",
          fontSize: "52px",
          fontWeight: 900,
          color: "#F0F0F0",
          lineHeight: 1,
          userSelect: "none",
          pointerEvents: "none",
        }}
      >
        &ldquo;
      </span>
      <p
        style={{
          fontSize: "13px",
          color: "#3A3A3A",
          lineHeight: 1.7,
          position: "relative",
          zIndex: 10,
          paddingTop: "16px",
          paddingLeft: "8px",
          fontStyle: "italic",
        }}
      >
        {quote}
      </p>
    </motion.div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function AnalyzePage() {
  const [form, setForm] = useState<BriefFormData>({
    product_name: "", category: "", description: "",
    price: "", target_audience: "", tags: [], demo_mode: false,
  });
  const [result, setResult] = useState<BriefAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState<BriefSignalDimensions>(DEFAULT_SIGNALS);
  const debounce = useRef<ReturnType<typeof setTimeout> | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (debounce.current) clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      setLive(computeLiveSignals(`${form.product_name} ${form.description} ${form.tags.join(" ")}`));
    }, 300);
    return () => { if (debounce.current) clearTimeout(debounce.current); };
  }, [form.product_name, form.description, form.tags]);

  const signals = result ? result.signal_dimensions : live;
  const displayScore = result?.vibe_score ?? 0;
  const active = !!result && !analyzing;
  const animated = useCountUp(Math.round(displayScore), 1600, active);
  const score = active ? animated : result ? Math.round(displayScore) : null;
  const cls = result?.classification ? CLASSIFICATION[result.classification] : null;

  const set = useCallback(<K extends keyof BriefFormData>(k: K, v: BriefFormData[K]) => {
    setForm((f) => ({ ...f, [k]: v }));
  }, []);

  const toggleTag = useCallback((tag: string) => {
    setForm((f) => ({
      ...f,
      tags: f.tags.includes(tag) ? f.tags.filter(t => t !== tag) : f.tags.length < 5 ? [...f.tags, tag] : f.tags,
    }));
  }, []);

  const loadDemo = useCallback(() => {
    setForm(DEMO); setResult(null); setError(null);
    setTimeout(() => document.getElementById("analyze-btn")?.click(), 600);
  }, []);

  const analyze = useCallback(async () => {
    if (!form.product_name.trim()) { setError("Product name is required."); return; }
    setError(null); setResult(null); setAnalyzing(true);
    try {
      const res = await briefAnalysis.analyze({
        product_name: form.product_name,
        description: form.description,
        category: form.category || undefined,
        price: form.price || undefined,
        target_audience: form.target_audience || undefined,
        tags: form.tags,
        demo_mode: form.demo_mode,
      });
      setResult(res);
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 300);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Is the backend running?");
    } finally {
      setAnalyzing(false);
    }
  }, [form]);

  return (
    <div className="min-h-screen bg-white text-[#0A0A0A]">

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <Container className="pt-16 pb-14 text-center">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.28em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "20px" }}>
            AI-Powered Virality Forecasting
          </p>
          <h1
            style={{
              fontFamily: "var(--font-playfair)",
              fontSize: "clamp(36px, 5vw, 64px)",
              fontWeight: 900,
              color: "#0A0A0A",
              letterSpacing: "-0.03em",
              lineHeight: 1.05,
              marginBottom: "16px",
            }}
          >
            Product Intelligence Brief
          </h1>
          <p style={{ fontSize: "16px", color: "#6B6B6B", lineHeight: 1.6, marginBottom: "32px" }}>
            Predict cultural momentum before launch.
          </p>
          <motion.button
            onClick={loadDemo}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center gap-2 text-[12px] font-medium text-[#6B6B6B] hover:text-[#0A0A0A] bg-white transition-all"
            style={{ border: "1px dashed #D0D0D0", borderRadius: "100px", padding: "10px 20px" }}
          >
            <Sparkles className="w-3.5 h-3.5 text-[#A0A0A0]" />
            Try Demo: Ninja Matcha Machine
          </motion.button>
        </motion.div>
      </Container>

      {/* ── Form Card ─────────────────────────────────────────────────────── */}
      <Container className="pb-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          style={{
            background: "white",
            borderRadius: "28px",
            border: "1px solid #E8E8E8",
            boxShadow: "0 8px 40px rgba(0,0,0,0.06), 0 1px 6px rgba(0,0,0,0.04)",
            padding: "40px",
          }}
        >
          {/* Card header */}
          <div style={{ marginBottom: "32px" }}>
            <h2
              style={{
                fontFamily: "var(--font-playfair)",
                fontSize: "22px",
                fontWeight: 700,
                color: "#0A0A0A",
                marginBottom: "6px",
              }}
            >
              Product Details
            </h2>
            <p style={{ fontSize: "13px", color: "#A0A0A0", lineHeight: 1.5 }}>
              Tell us what makes this product culturally interesting.
            </p>
          </div>

          {/* 2-column grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* LEFT: Name, Category, Price */}
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div>
                <FieldLabel>Product Name</FieldLabel>
                <TextInput
                  value={form.product_name}
                  onChange={(v) => set("product_name", v)}
                  placeholder="e.g. Ninja Matcha Machine *"
                />
              </div>
              <div>
                <FieldLabel>Category</FieldLabel>
                <SelectInput value={form.category} onChange={(v) => set("category", v)}>
                  <option value="">Select a category…</option>
                  {BRIEF_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </SelectInput>
              </div>
              <div>
                <FieldLabel>Price (USD)</FieldLabel>
                <TextInput value={form.price} onChange={(v) => set("price", v)} placeholder="149" type="number" />
              </div>
            </div>

            {/* RIGHT: Audience, Tags */}
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div>
                <FieldLabel>Target Audience</FieldLabel>
                <TextInput
                  value={form.target_audience}
                  onChange={(v) => set("target_audience", v)}
                  placeholder="Aesthetic creators, wellness fans…"
                />
              </div>
              <div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                  <FieldLabel>Feature Tags</FieldLabel>
                  <span style={{ fontSize: "10px", fontWeight: 600, color: "#A0A0A0", marginTop: "-8px" }}>{form.tags.length}/5</span>
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                  {FEATURE_TAGS.map((tag) => {
                    const sel = form.tags.includes(tag);
                    return (
                      <motion.button
                        key={tag}
                        onClick={() => toggleTag(tag)}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        style={{
                          padding: "8px 14px",
                          fontSize: "12px",
                          fontWeight: 500,
                          borderRadius: "100px",
                          border: `1px solid ${sel ? "#7C3AED" : "#E8E8E8"}`,
                          background: sel ? "#7C3AED" : "white",
                          color: sel ? "white" : "#6B6B6B",
                          cursor: "pointer",
                          transition: "all 0.15s ease",
                        }}
                      >
                        {tag}
                      </motion.button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Full-width: Product Brief */}
          <div style={{ marginBottom: "24px" }}>
            <FieldLabel>Product Brief</FieldLabel>
            <textarea
              rows={6}
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
              placeholder="Describe the product — how people use it, what makes it shareable, what consumers say, any viral moments observed…"
              className="w-full bg-white text-[14px] text-[#0A0A0A] placeholder-[#C0C0C0] focus:outline-none resize-none transition-all"
              style={{
                border: "1.5px solid #E8E8E8",
                padding: "16px",
                borderRadius: "16px",
                lineHeight: 1.7,
                minHeight: "180px",
              }}
              onFocus={e => { e.currentTarget.style.borderColor = "#7C3AED"; e.currentTarget.style.boxShadow = "0 0 0 3px rgba(124,58,237,0.08)"; }}
              onBlur={e => { e.currentTarget.style.borderColor = "#E8E8E8"; e.currentTarget.style.boxShadow = "none"; }}
            />
          </div>

          {/* Live Signal Pills */}
          <AnimatePresence>
            {form.description.length > 10 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                style={{ overflow: "hidden", marginBottom: "24px" }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                  <span style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.16em", textTransform: "uppercase", color: "#A0A0A0" }}>
                    Live Signals
                  </span>
                  <SignalPill label="Emotional Pull" score={live.emotional_pull} />
                  <SignalPill label="Creator Magnetism" score={live.creator_magnetism} />
                  <SignalPill label="Novelty" score={live.novelty} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                style={{
                  marginBottom: "20px",
                  padding: "12px 16px",
                  fontSize: "13px",
                  color: "#6B6B6B",
                  border: "1px solid #E8E8E8",
                  borderLeft: "3px solid #7C3AED",
                  borderRadius: "8px",
                  background: "#FAFAFA",
                }}
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* CTA Button */}
          <motion.button
            id="analyze-btn"
            onClick={analyze}
            disabled={analyzing || !form.product_name.trim()}
            whileHover={!analyzing && !!form.product_name.trim() ? { scale: 1.005, y: -1 } : {}}
            whileTap={!analyzing && !!form.product_name.trim() ? { scale: 0.995 } : {}}
            className="w-full text-[13px] font-semibold text-white tracking-wide uppercase transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              height: "56px",
              background: analyzing ? "#9CA3AF" : "linear-gradient(135deg, #7C3AED 0%, #5B8CFF 100%)",
              borderRadius: "14px",
              boxShadow: analyzing || !form.product_name.trim()
                ? "none"
                : "0 4px 20px rgba(124,58,237,0.35), 0 1px 6px rgba(0,0,0,0.08)",
            }}
          >
            <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "12px" }}>
              {analyzing ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Analyzing cultural momentum…
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Analyze Viral Potential
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </span>
          </motion.button>
        </motion.div>
      </Container>

      {/* ── Results ───────────────────────────────────────────────────────── */}
      <div ref={resultsRef}>
        <AnimatePresence>
          {result && !analyzing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            >

              {/* ── VIBE Score — Cinematic ───────────────────────────────── */}
              <div style={{ borderTop: "1px solid #F0F0F0" }}>
                <Container className="py-20 text-center">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
                  >
                    <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.32em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "32px" }}>
                      VIBE Score
                    </p>
                    <RadialScore
                      displayNumber={score}
                      percent={Math.round(displayScore)}
                      active={active}
                      color={cls?.ringColor ?? "#7C3AED"}
                    />
                    <AnimatePresence>
                      {cls && (
                        <motion.div
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.6, duration: 0.35 }}
                          style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "10px", marginTop: "24px" }}
                        >
                          <span
                            style={{
                              padding: "8px 24px",
                              fontSize: "11px",
                              fontWeight: 700,
                              letterSpacing: "0.2em",
                              textTransform: "uppercase",
                              color: cls.badgeColor,
                              border: `1.5px solid ${cls.badgeColor}`,
                              borderRadius: "100px",
                            }}
                          >
                            {cls.label}
                          </span>
                          <p style={{ fontSize: "14px", color: "#6B6B6B" }}>{cls.sublabel}</p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                </Container>
              </div>

              {/* ── Signal Dimensions ───────────────────────────────────── */}
              <Container className="pb-24">
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.2 }}
                  style={{
                    background: "white",
                    border: "1px solid #E8E8E8",
                    borderRadius: "24px",
                    boxShadow: "0 4px 24px rgba(0,0,0,0.04)",
                    padding: "40px",
                  }}
                >
                  <h2
                    style={{
                      fontFamily: "var(--font-playfair)",
                      fontSize: "22px",
                      fontWeight: 700,
                      color: "#0A0A0A",
                      marginBottom: "32px",
                      letterSpacing: "-0.01em",
                    }}
                  >
                    Signal Dimensions
                  </h2>
                  <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                    {SIGNALS.map(({ key, label }) => (
                      <DimensionRow key={key} label={label} value={signals[key]} />
                    ))}
                  </div>
                </motion.div>
              </Container>

              {/* ── Culture + Memory ────────────────────────────────────── */}
              <Container className="pb-24">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <StatCard
                    label="Culture Score"
                    value={Math.round(result.culture_score * 100)}
                    desc="Strong creator alignment"
                  />
                  <StatCard
                    label="Memory Score"
                    value={Math.round(result.memory_score * 100)}
                    desc="High retention potential"
                  />
                </div>
              </Container>

              {/* ── Intelligence Report ─────────────────────────────────── */}
              <Container className="pb-24">
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.25 }}
                >
                  <div style={{ marginBottom: "32px" }}>
                    <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.24em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "8px" }}>
                      Analysis
                    </p>
                    <h2
                      style={{
                        fontFamily: "var(--font-playfair)",
                        fontSize: "36px",
                        fontWeight: 900,
                        color: "#0A0A0A",
                        letterSpacing: "-0.02em",
                      }}
                    >
                      Intelligence Report
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* Viral Archetype */}
                    <div
                      style={{
                        padding: "28px",
                        borderRadius: "20px",
                        border: "1px solid #EDE9FE",
                        background: "linear-gradient(145deg, #FAFAFA 0%, #F5F3FF 100%)",
                        boxShadow: "0 2px 12px rgba(124,58,237,0.06)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px" }}>
                        <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#EDE9FE", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <TrendingUp className="w-4 h-4 text-violet-600" />
                        </div>
                        <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase", color: "#7C3AED" }}>
                          Viral Archetype
                        </p>
                      </div>
                      <p
                        style={{
                          fontFamily: "var(--font-playfair)",
                          fontSize: "16px",
                          fontWeight: 700,
                          color: "#0A0A0A",
                          lineHeight: 1.3,
                          marginBottom: "10px",
                        }}
                      >
                        {result.closest_viral_archetype}
                      </p>
                      <p style={{ fontSize: "13px", color: "#6B6B6B", lineHeight: 1.6 }}>{result.trend_alignment_reason}</p>
                    </div>

                    {/* Why It Could Go Viral */}
                    <div
                      style={{
                        padding: "28px",
                        borderRadius: "20px",
                        border: "1px solid #E8E8E8",
                        background: "white",
                        boxShadow: "0 2px 12px rgba(0,0,0,0.04)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px" }}>
                        <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#F0FDF4", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <Zap className="w-4 h-4 text-green-600" />
                        </div>
                        <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase", color: "#16A34A" }}>
                          Why It Could Go Viral
                        </p>
                      </div>
                      <div>
                        {result.why_viral.map((item, i) => (
                          <InsightItem key={i} text={item} type="viral" delay={i * 0.06} />
                        ))}
                      </div>
                    </div>

                    {/* Risk Factors */}
                    <div
                      style={{
                        padding: "28px",
                        borderRadius: "20px",
                        border: "1px solid #FEF3C7",
                        background: "#FFFBEB",
                        boxShadow: "0 2px 12px rgba(0,0,0,0.04)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px" }}>
                        <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#FEF3C7", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <AlertTriangle className="w-4 h-4 text-amber-500" />
                        </div>
                        <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase", color: "#D97706" }}>
                          Risk Factors
                        </p>
                      </div>
                      <div>
                        {result.why_fail.map((item, i) => (
                          <InsightItem key={i} text={item} type="fail" delay={0.12 + i * 0.06} />
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </Container>

              {/* ── Consumer Narrative ──────────────────────────────────── */}
              <Container className="pb-24">
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.3 }}
                  style={{
                    position: "relative",
                    padding: "64px 80px",
                    textAlign: "center",
                    borderRadius: "24px",
                    border: "1px solid #E8E8E8",
                    background: "white",
                    boxShadow: "0 4px 24px rgba(0,0,0,0.04)",
                    overflow: "hidden",
                  }}
                >
                  {/* Giant decorative quote */}
                  <span
                    style={{
                      position: "absolute",
                      top: "-10px",
                      left: "32px",
                      fontFamily: "var(--font-playfair)",
                      fontSize: "180px",
                      fontWeight: 900,
                      color: "#F0F0F0",
                      lineHeight: 1,
                      userSelect: "none",
                      pointerEvents: "none",
                    }}
                  >
                    &ldquo;
                  </span>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", marginBottom: "32px" }}>
                    <MessageSquare className="w-4 h-4 text-[#A0A0A0]" />
                    <p style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.24em", textTransform: "uppercase", color: "#A0A0A0" }}>
                      Consumer Narrative
                    </p>
                  </div>
                  <p
                    style={{
                      fontFamily: "var(--font-playfair)",
                      fontSize: "22px",
                      lineHeight: 1.7,
                      color: "#3A3A3A",
                      fontStyle: "italic",
                      maxWidth: "660px",
                      margin: "0 auto",
                      letterSpacing: "0.01em",
                      position: "relative",
                      zIndex: 10,
                    }}
                  >
                    &ldquo;{result.consumer_narrative}&rdquo;
                  </p>
                </motion.div>
              </Container>

              {/* ── Consumer Voice ───────────────────────────────────────── */}
              <Container className="pb-32">
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.35 }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "32px" }}>
                    <Users className="w-5 h-5 text-[#A0A0A0]" />
                    <h2
                      style={{
                        fontFamily: "var(--font-playfair)",
                        fontSize: "22px",
                        fontWeight: 700,
                        color: "#0A0A0A",
                      }}
                    >
                      Consumer Voice
                    </h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.consumer_language.map((quote, i) => (
                      <QuoteCard key={i} quote={quote} index={i} />
                    ))}
                  </div>
                </motion.div>
              </Container>

            </motion.div>
          )}
        </AnimatePresence>
      </div>

    </div>
  );
}
