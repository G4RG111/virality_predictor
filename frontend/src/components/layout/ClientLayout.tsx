"use client";

import { usePathname } from "next/navigation";
import { TopNav } from "./TopNav";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/") {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-white">
      <TopNav />
      <main>{children}</main>
    </div>
  );
}
