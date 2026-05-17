"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Zap, TrendingUp, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/",        label: "Portfolio", icon: LayoutGrid, desc: "All products" },
  { href: "/analyze", label: "Analyze",   icon: Zap,         desc: "New brief"   },
  { href: "/trends",  label: "Trends",    icon: TrendingUp,  desc: "Leaderboard" },
  { href: "/upload",  label: "Upload",    icon: Upload,      desc: "iHUT data"   },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="fixed left-0 top-0 h-full w-56 bg-white flex flex-col z-40"
      style={{ borderRight: "1px solid rgba(0,0,0,0.06)", boxShadow: "2px 0 12px rgba(0,0,0,0.04)" }}
    >
      {/* Logo mark */}
      <div className="px-5 pt-6 pb-5">
        <Link href="/" className="block group">
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform duration-200 group-hover:scale-105"
              style={{ background: "linear-gradient(135deg, #7C3AED 0%, #5B8CFF 100%)", boxShadow: "0 2px 8px rgba(124,58,237,0.30)" }}
            >
              <span
                className="text-white text-[13px]"
                style={{ fontFamily: "var(--font-playfair)", fontWeight: 700 }}
              >
                V
              </span>
            </div>
            <div>
              <div
                className="text-gray-900 text-[15px] leading-none"
                style={{ fontFamily: "var(--font-playfair)", fontWeight: 700, letterSpacing: "0.01em" }}
              >
                VIBE
              </div>
              <div className="text-gray-400 text-[10px] mt-0.5 font-medium tracking-wide leading-none">
                SharkNinja Intel
              </div>
            </div>
          </div>
        </Link>
      </div>

      {/* Divider */}
      <div className="mx-5 mb-4 h-px bg-gray-100" />

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-0.5">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/"
              ? pathname === "/" || pathname === "/dashboard"
              : pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-[13px] font-medium transition-all duration-150 group",
                active
                  ? "bg-violet-50 text-violet-700"
                  : "text-gray-500 hover:text-gray-900 hover:bg-gray-50",
              )}
            >
              <Icon
                className={cn(
                  "w-4 h-4 flex-shrink-0 transition-colors",
                  active ? "text-violet-600" : "text-gray-400 group-hover:text-gray-600",
                )}
              />
              <span>{label}</span>
              {active && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-violet-500 shrink-0" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4" style={{ borderTop: "1px solid rgba(0,0,0,0.05)" }}>
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span className="text-[10px] text-gray-400 font-medium tracking-wide">Phase 1 · v1.0</span>
        </div>
      </div>
    </aside>
  );
}
