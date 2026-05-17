"use client";

import { useState } from "react";
import { X, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { products as productsApi } from "@/lib/api-client";
import type { Product } from "@/lib/types";

interface Props {
  onClose: () => void;
  onCreated: (product: Product) => void;
}

const MARKETS = ["US", "UK", "DE", "AU", "FR", "JP", "Other"];
const CATEGORIES = ["Blender", "Air Purifier", "Vacuum", "Hair Care", "Food Processor", "Coffee", "Other"];

const inputCls =
  "w-full bg-white border border-[#E5E5E5] rounded px-3 py-2 text-[13px] text-[#111111] placeholder-[#BBBBBB] focus:outline-none focus:ring-2 focus:ring-[#E41E26]/20 focus:border-[#E41E26] transition-colors";

const selectCls =
  "w-full bg-white border border-[#E5E5E5] rounded px-3 py-2 text-[13px] text-[#111111] focus:outline-none focus:ring-2 focus:ring-[#E41E26]/20 focus:border-[#E41E26] transition-colors";

export function CreateProductModal({ onClose, onCreated }: Props) {
  const [name, setName] = useState("");
  const [asin, setAsin] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [advanced, setAdvanced] = useState({
    sku: "", category: "", market: "", price_usd: "", description: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setAdv = (key: string, val: string) =>
    setAdvanced((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      const payload: Record<string, unknown> = { name: name.trim() };
      if (asin.trim()) payload.asin = asin.trim().toUpperCase();
      if (advanced.sku.trim()) payload.sku = advanced.sku.trim();
      if (advanced.category) payload.category = advanced.category;
      if (advanced.market) payload.market = advanced.market;
      if (advanced.price_usd) payload.price_usd = parseFloat(advanced.price_usd);
      if (advanced.description.trim()) payload.description = advanced.description.trim();
      const created = await productsApi.create(payload as Parameters<typeof productsApi.create>[0]);
      onCreated(created);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create product");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white border border-[#E5E5E5] rounded-xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#E5E5E5]">
          <h2 className="text-[15px] font-bold text-[#111111]">Add Product</h2>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded text-[#999999] hover:text-[#111111] hover:bg-[#F5F5F5] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div>
            <label className="block text-[11px] font-semibold text-[#555555] uppercase tracking-wider mb-1.5">
              Product Name <span className="text-[#E41E26]">*</span>
            </label>
            <input
              required autoFocus type="text"
              placeholder="e.g. Ninja Slushi Machine"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={inputCls}
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-[#555555] uppercase tracking-wider mb-1.5">
              Amazon ASIN
              <span className="ml-1.5 text-[#BBBBBB] font-normal normal-case tracking-normal">optional</span>
            </label>
            <input
              type="text" placeholder="e.g. B09XH4G3XK" maxLength={10}
              value={asin}
              onChange={(e) => setAsin(e.target.value)}
              className={`font-mono uppercase ${inputCls}`}
            />
          </div>

          <button
            type="button"
            onClick={() => setShowAdvanced((v) => !v)}
            className="flex items-center gap-1.5 text-[12px] text-[#999999] hover:text-[#555555] transition-colors"
          >
            {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            {showAdvanced ? "Hide" : "Show"} details
          </button>

          {showAdvanced && (
            <div className="space-y-3 pt-1 border-t border-[#F0F0F0]">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-[#555555] uppercase tracking-wider mb-1.5">Market</label>
                  <select value={advanced.market} onChange={(e) => setAdv("market", e.target.value)} className={selectCls}>
                    <option value="">Select…</option>
                    {MARKETS.map((m) => <option key={m} value={m}>{m}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#555555] uppercase tracking-wider mb-1.5">Category</label>
                  <select value={advanced.category} onChange={(e) => setAdv("category", e.target.value)} className={selectCls}>
                    <option value="">Select…</option>
                    {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-[#555555] uppercase tracking-wider mb-1.5">SKU</label>
                  <input type="text" placeholder="NC301EU" value={advanced.sku}
                    onChange={(e) => setAdv("sku", e.target.value)} className={inputCls} />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#555555] uppercase tracking-wider mb-1.5">Price (USD)</label>
                  <input type="number" placeholder="99.99" min="0" step="0.01" value={advanced.price_usd}
                    onChange={(e) => setAdv("price_usd", e.target.value)} className={inputCls} />
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-[#555555] uppercase tracking-wider mb-1.5">Description</label>
                <textarea rows={2} placeholder="Brief product description…" value={advanced.description}
                  onChange={(e) => setAdv("description", e.target.value)}
                  className={`resize-none ${inputCls}`} />
              </div>
            </div>
          )}

          {error && (
            <div className="rounded bg-red-50 border border-red-200 px-3 py-2 text-[12px] text-red-600">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose}
              className="flex-1 px-4 py-2 text-[13px] font-medium text-[#555555] bg-[#F5F5F5] border border-[#E5E5E5] rounded hover:bg-[#EEEEEE] transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={!name.trim() || saving}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-[13px] font-semibold text-white bg-[#E41E26] hover:bg-[#C8151B] rounded transition-colors disabled:opacity-40 disabled:cursor-not-allowed">
              {saving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              {saving ? "Creating…" : "Create Product"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
