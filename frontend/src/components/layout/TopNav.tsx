"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Upload, User } from "lucide-react";
import { cn } from "@/lib/utils";

const CENTER_LINKS = [
  { href: "/products", label: "Portfolio" },
  { href: "/analyze",  label: "Analyze"   },
];

export function TopNav() {
  const pathname = usePathname();

  const isActive = (href: string) =>
    href === "/products"
      ? pathname === "/products" || pathname.startsWith("/products/")
      : pathname === href || pathname.startsWith(href + "/");

  return (
    <div className="sticky top-0 z-50 px-6 pt-4 pb-3 pointer-events-none">
      {/* Thin purple glow line at very top */}
      <div
        className="fixed top-0 left-0 right-0 pointer-events-none"
        style={{
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(124,58,237,0.5) 30%, rgba(91,140,255,0.5) 70%, transparent 100%)",
        }}
      />

      <nav
        className="relative max-w-[1200px] mx-auto flex items-center justify-between px-5 h-14 pointer-events-auto"
        style={{
          background: "rgba(255,255,255,0.88)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          border: "1px solid rgba(0,0,0,0.07)",
          borderRadius: "16px",
          boxShadow: "0 2px 16px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.04)",
        }}
      >
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group shrink-0">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center transition-transform duration-200 group-hover:scale-105"
            style={{
              background: "linear-gradient(135deg, #7C3AED 0%, #5B8CFF 100%)",
              boxShadow: "0 2px 8px rgba(124,58,237,0.3)",
            }}
          >
            <span
              className="text-white text-[12px]"
              style={{ fontFamily: "var(--font-playfair)", fontWeight: 700 }}
            >
              V
            </span>
          </div>
          <span
            style={{
              fontFamily: "var(--font-playfair)",
              fontWeight: 700,
              fontSize: "15px",
              color: "#0A0A0A",
              letterSpacing: "0.02em",
            }}
          >
            VIBE
          </span>
        </Link>

        {/* Center links */}
        <div className="flex items-center gap-1">
          {CENTER_LINKS.map(({ href, label }) => {
            const active = isActive(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "relative px-4 py-2 text-[13px] font-medium rounded-xl transition-all duration-150",
                  active
                    ? "text-[#0A0A0A] bg-black/[0.05]"
                    : "text-[#6B6B6B] hover:text-[#0A0A0A] hover:bg-black/[0.03]",
                )}
              >
                {label}
                {active && (
                  <span
                    className="absolute bottom-1.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full"
                    style={{ background: "#7C3AED" }}
                  />
                )}
              </Link>
            );
          })}
        </div>

        {/* Right: Upload + User */}
        <div className="flex items-center gap-2 shrink-0">
          <Link
            href="/upload"
            className={cn(
              "flex items-center gap-1.5 px-3.5 py-2 text-[12px] font-medium rounded-xl transition-all duration-150",
              isActive("/upload")
                ? "text-[#0A0A0A] bg-black/[0.05]"
                : "text-[#6B6B6B] hover:text-[#0A0A0A] hover:bg-black/[0.03]",
            )}
          >
            <Upload className="w-3.5 h-3.5" />
            Upload
          </Link>
          <button className="w-8 h-8 rounded-full flex items-center justify-center text-[#6B6B6B] hover:text-[#0A0A0A] transition-colors" style={{ background: "rgba(0,0,0,0.04)" }}>
            <User className="w-3.5 h-3.5" />
          </button>
        </div>
      </nav>
    </div>
  );
}
