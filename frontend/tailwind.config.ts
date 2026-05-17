import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // VIBE score band color system
        "band-low": "#64748b",       // slate-500
        "band-moderate": "#f59e0b",  // amber-500
        "band-high": "#3b82f6",      // blue-500
        "band-viral": "#8b5cf6",     // violet-500
        // Brand
        "vibe-dark": "#0f0f1a",
        "vibe-surface": "#1a1a2e",
        "vibe-border": "#2a2a45",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "score-fill": "scoreFill 1.2s ease-out forwards",
      },
      keyframes: {
        scoreFill: {
          "0%": { strokeDashoffset: "339" },
          "100%": { strokeDashoffset: "var(--target-offset)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
