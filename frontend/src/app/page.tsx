"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Zap } from "lucide-react";

function useCountUp(target: number, duration: number, active: boolean) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!active) return;
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

const DIMS = [
  { label: "Hackability",      val: 94 },
  { label: "Creator Language", val: 88 },
  { label: "Shareability",     val: 91 },
  { label: "Emotional Pull",   val: 79 },
];

export default function LandingPage() {
  const demoRef = useRef<HTMLDivElement>(null);
  const inView = useInView(demoRef, { once: true, margin: "-100px" });
  const score = useCountUp(87, 1800, inView);

  return (
    <div className="min-h-screen bg-white text-[#0A0A0A]">

      {/* ── Nav ─────────────────────────────────────────────────────────────── */}
      <nav
        className="flex items-center justify-between px-10 py-5"
        style={{ borderBottom: "1px solid #E8E8E8" }}
      >
        <div className="flex items-center gap-4">
          <span
            style={{
              fontFamily: "var(--font-playfair)",
              fontWeight: 700,
              fontSize: "17px",
              letterSpacing: "0.06em",
              color: "#0A0A0A",
            }}
          >
            VIBE
          </span>
          <span style={{ color: "#D0D0D0" }}>·</span>
          <span style={{ fontSize: "11px", fontWeight: 500, color: "#A0A0A0", letterSpacing: "0.05em" }}>
            Viral Impact &amp; Buzz Estimation
          </span>
        </div>
        <Link
          href="/analyze"
          style={{ fontSize: "11px", fontWeight: 600, color: "#0A0A0A", letterSpacing: "0.12em", textTransform: "uppercase", display: "flex", alignItems: "center", gap: "6px", textDecoration: "none" }}
        >
          Open app <ArrowRight style={{ width: "12px", height: "12px" }} />
        </Link>
      </nav>

      {/* ── Hero ──────────────────────────────────────────────────────────────── */}
      <section className="px-10 pt-20 pb-20 max-w-7xl mx-auto">
        <p
          style={{
            fontSize: "10px",
            fontWeight: 600,
            letterSpacing: "0.24em",
            textTransform: "uppercase",
            color: "#A0A0A0",
            marginBottom: "40px",
          }}
        >
          AI-powered virality intelligence · Phase 1
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-20 items-start">

          {/* Left — headline */}
          <div>
            <h1
              style={{
                fontFamily: "var(--font-playfair)",
                fontSize: "clamp(56px, 9vw, 104px)",
                fontWeight: 900,
                lineHeight: 0.96,
                letterSpacing: "-0.025em",
                color: "#0A0A0A",
              }}
            >
              Predict<br />
              cultural<br />
              momentum<br />
              before launch.
            </h1>

            <p
              style={{
                marginTop: "40px",
                fontSize: "15px",
                color: "#6B6B6B",
                maxWidth: "24rem",
                lineHeight: 1.6,
              }}
            >
              VIBE scores products on virality before they ship — using iHUT data,
              Amazon reviews, and AI signal detection to find the next Ninja Creami.
            </p>

            <div style={{ marginTop: "40px", display: "flex", alignItems: "center", gap: "24px" }}>
              <Link
                href="/analyze"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "14px 28px",
                  fontSize: "11px",
                  fontWeight: 600,
                  color: "#FFFFFF",
                  background: "#0A0A0A",
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  textDecoration: "none",
                  borderRadius: 0,
                }}
              >
                <Zap style={{ width: "12px", height: "12px" }} />
                Analyze a product
              </Link>
              <Link
                href="/products"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  fontSize: "12px",
                  fontWeight: 500,
                  color: "#6B6B6B",
                  textDecoration: "none",
                  borderBottom: "1px solid #E8E8E8",
                }}
              >
                View portfolio
                <ArrowRight style={{ width: "12px", height: "12px" }} />
              </Link>
            </div>
          </div>

          {/* Right — demo score card */}
          <div ref={demoRef} className="lg:pt-2">
            <div style={{ border: "1px solid #E8E8E8" }}>
              {/* Card header */}
              <div className="px-6 py-5" style={{ borderBottom: "1px solid #E8E8E8" }}>
                <p style={{ fontSize: "9px", fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "6px" }}>
                  Sample Analysis
                </p>
                <p
                  style={{
                    fontFamily: "var(--font-playfair)",
                    fontWeight: 700,
                    fontSize: "15px",
                    color: "#0A0A0A",
                  }}
                >
                  Ninja Creami Deluxe
                </p>
                <p style={{ fontSize: "11px", color: "#A0A0A0", marginTop: "2px" }}>
                  Ice Cream Maker · North America · $199
                </p>
              </div>

              {/* Score */}
              <div className="px-6 py-6" style={{ borderBottom: "1px solid #E8E8E8" }}>
                <p style={{ fontSize: "9px", fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "8px" }}>
                  VIBE Score
                </p>
                <div style={{ display: "flex", alignItems: "flex-end", gap: "16px" }}>
                  <span
                    style={{
                      fontFamily: "var(--font-playfair)",
                      fontSize: "76px",
                      fontWeight: 900,
                      lineHeight: 1,
                      letterSpacing: "-0.04em",
                      color: "#0A0A0A",
                    }}
                  >
                    {score}
                  </span>
                  <div style={{ paddingBottom: "8px" }}>
                    <span
                      style={{
                        fontSize: "9px",
                        fontWeight: 700,
                        letterSpacing: "0.14em",
                        textTransform: "uppercase",
                        color: "#0A0A0A",
                        padding: "4px 10px",
                        border: "1px solid #0A0A0A",
                      }}
                    >
                      Viral Ready
                    </span>
                  </div>
                </div>
                {/* Score bar */}
                <div style={{ marginTop: "16px", height: "1px", background: "#F0F0F0", overflow: "hidden" }}>
                  <motion.div
                    style={{ height: "100%", background: "#0A0A0A" }}
                    initial={{ width: "0%" }}
                    animate={inView ? { width: "87%" } : { width: "0%" }}
                    transition={{ duration: 1.6, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>
              </div>

              {/* Dimension bars */}
              <div className="px-6 py-5 space-y-3.5">
                {DIMS.map(({ label, val }, i) => (
                  <div key={label} style={{ marginBottom: "14px" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                      <span style={{ fontSize: "11px", color: "#6B6B6B" }}>{label}</span>
                      <span style={{ fontSize: "11px", fontWeight: 600, color: "#0A0A0A", fontVariantNumeric: "tabular-nums" }}>
                        {inView ? val : 0}
                      </span>
                    </div>
                    <div style={{ height: "1px", background: "#F0F0F0", overflow: "hidden" }}>
                      <motion.div
                        style={{ height: "100%", background: "#0A0A0A" }}
                        initial={{ width: "2%" }}
                        animate={inView ? { width: `${val}%` } : { width: "2%" }}
                        transition={{ delay: 0.3 + i * 0.07, duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Card footer */}
              <div className="px-6 py-4" style={{ borderTop: "1px solid #E8E8E8" }}>
                <Link
                  href="/analyze"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    width: "100%",
                    fontSize: "11px",
                    fontWeight: 500,
                    color: "#6B6B6B",
                    textDecoration: "none",
                  }}
                >
                  Analyze your product
                  <ArrowRight style={{ width: "14px", height: "14px" }} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Divider ────────────────────────────────────────────────────────── */}
      <div style={{ borderTop: "1px solid #E8E8E8" }} />

      {/* ── Philosophy ────────────────────────────────────────────────────── */}
      <section className="px-10 py-24 max-w-7xl mx-auto">
        <div style={{ marginBottom: "64px" }}>
          <p style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.24em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "20px" }}>
            The Insight
          </p>
          <h2
            style={{
              fontFamily: "var(--font-playfair)",
              fontSize: "clamp(40px, 6vw, 72px)",
              fontWeight: 900,
              lineHeight: 0.98,
              letterSpacing: "-0.025em",
              color: "#0A0A0A",
            }}
          >
            Virality ≠ Satisfaction.
          </h2>
          <p style={{ color: "#6B6B6B", fontSize: "14px", marginTop: "20px", maxWidth: "18rem", lineHeight: 1.6 }}>
            The highest-rated products don&apos;t always win cultural moments.
          </p>
        </div>

        {/* Two-column comparison grid */}
        <div
          className="grid grid-cols-1 md:grid-cols-2"
          style={{ border: "1px solid #E8E8E8" }}
        >
          <div
            className="bg-white p-8 md:p-10"
            style={{ borderRight: "1px solid #E8E8E8" }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "32px" }}>
              <span style={{ fontSize: "11px", color: "#A0A0A0" }}>★ 4.9 · 12,400 reviews</span>
              <span
                style={{
                  fontSize: "9px",
                  fontWeight: 700,
                  letterSpacing: "0.18em",
                  textTransform: "uppercase",
                  color: "#A0A0A0",
                  padding: "4px 8px",
                  border: "1px solid #E0E0E0",
                }}
              >
                Low Vibe · 34
              </span>
            </div>
            <h3
              style={{
                fontFamily: "var(--font-playfair)",
                fontWeight: 700,
                fontSize: "22px",
                color: "#0A0A0A",
                marginBottom: "10px",
                lineHeight: 1.2,
              }}
            >
              Premium Kitchen Scale
            </h3>
            <p style={{ color: "#6B6B6B", fontSize: "13px", lineHeight: 1.6 }}>
              Reliably useful. Functionally perfect. Measures things accurately, every time.
            </p>
            <p style={{ color: "#C0C0C0", fontSize: "12px", marginTop: "32px", fontStyle: "italic" }}>Culturally invisible.</p>
          </div>

          <div className="bg-white p-8 md:p-10" style={{ position: "relative" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "3px", background: "#0A0A0A" }} />
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "32px" }}>
              <span style={{ fontSize: "11px", color: "#A0A0A0" }}>★ 3.8 · 89,200 reviews</span>
              <span
                style={{
                  fontSize: "9px",
                  fontWeight: 700,
                  letterSpacing: "0.18em",
                  textTransform: "uppercase",
                  color: "#0A0A0A",
                  padding: "4px 8px",
                  border: "1px solid #0A0A0A",
                }}
              >
                Viral Ready · 91
              </span>
            </div>
            <h3
              style={{
                fontFamily: "var(--font-playfair)",
                fontWeight: 700,
                fontSize: "22px",
                color: "#0A0A0A",
                marginBottom: "10px",
                lineHeight: 1.2,
              }}
            >
              Ninja Creami
            </h3>
            <p style={{ color: "#3A3A3A", fontSize: "13px", lineHeight: 1.6 }}>
              People show it off. Recipes spread. TikTok made it a cultural moment.
            </p>
            <p style={{ color: "#0A0A0A", fontSize: "12px", marginTop: "32px", fontStyle: "italic", fontWeight: 600 }}>
              Performative utility. Community-born hacks. Unstoppable.
            </p>
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────────── */}
      <section
        className="px-10 py-28 max-w-7xl mx-auto"
        style={{ borderTop: "1px solid #E8E8E8" }}
      >
        <p style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.24em", textTransform: "uppercase", color: "#A0A0A0", marginBottom: "28px" }}>
          SharkNinja Internal Tool
        </p>
        <h2
          style={{
            fontFamily: "var(--font-playfair)",
            fontSize: "clamp(44px, 7vw, 88px)",
            fontWeight: 900,
            lineHeight: 0.96,
            letterSpacing: "-0.025em",
            color: "#0A0A0A",
            marginBottom: "44px",
          }}
        >
          Find your next<br />viral product.
        </h2>
        <Link
          href="/analyze"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "16px 32px",
            fontSize: "11px",
            fontWeight: 600,
            color: "#FFFFFF",
            background: "#0A0A0A",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            textDecoration: "none",
            borderRadius: 0,
          }}
        >
          <Zap style={{ width: "14px", height: "14px" }} />
          Analyze Product
        </Link>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <div
        className="px-10 py-6 flex items-center justify-between max-w-7xl mx-auto"
        style={{ borderTop: "1px solid #E8E8E8" }}
      >
        <span style={{ fontSize: "11px", color: "#A0A0A0" }}>VIBE · Viral Impact &amp; Buzz Estimation · Phase 1 v1.0</span>
        <span style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "11px", color: "#A0A0A0" }}>
          <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#22C55E", display: "inline-block" }} />
          All systems operational
        </span>
      </div>
    </div>
  );
}
