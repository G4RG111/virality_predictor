import { ReactNode } from "react";

interface Props {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function PageShell({ title, subtitle, actions, children }: Props) {
  return (
    <div className="min-h-screen bg-[#06060f] text-white">
      <div className="border-b border-white/[0.06] px-8 py-5">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[#4a4a70] mb-1.5">
              SharkNinja · VIBE Intelligence
            </p>
            <h1 className="text-[22px] font-semibold text-white leading-none tracking-tight">{title}</h1>
            {subtitle && (
              <p className="text-sm text-[#5a5a80] mt-1.5 leading-relaxed">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex items-center gap-3 pb-0.5">{actions}</div>}
        </div>
      </div>
      <main className="px-8 py-7">{children}</main>
    </div>
  );
}
