'use client';

import { useEffect, useState } from 'react';
import { fetchWhales } from '@/lib/api';
import { Download } from 'lucide-react';

type Row = {
  wallet_address: string;
  segment: string;
  rfm_recency?: number;
  rfm_frequency?: number;
  rfm_volume?: number;
};

const SEG_STYLE: Record<string, string> = {
  whale: 'border-amber-300 bg-amber-50 text-amber-700',
  bot: 'border-violet-300 bg-violet-50 text-violet-700',
  active: 'border-emerald-300 bg-emerald-50 text-emerald-700',
  casual: 'border-sky-200 bg-sky-50 text-sky-600',
  dormant: 'border-border bg-muted text-muted-foreground',
};

export default function WhaleTracker() {
  const [data, setData] = useState<Row[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchWhales({ limit: 100 })
      .then((res) => { if (!cancelled) setData(res?.data || []); })
      .catch(() => { if (!cancelled) setData([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const filtered = search.trim()
    ? data.filter((r) => r.wallet_address?.toLowerCase().includes(search.trim().toLowerCase()))
    : data;

  const exportCsv = () => {
    const headers = ['wallet_address', 'segment', 'rfm_recency', 'rfm_frequency', 'rfm_volume'];
    const rows = filtered.map((r) => headers.map((h) => (r as Record<string, unknown>)[h] ?? '').join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'whales.csv';
    a.click();
  };

  return (
    <div className="rounded-2xl border border-border/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm transition-all duration-200 ease-out hover:-translate-y-[2px] hover:shadow-[0_6px_20px_rgba(0,0,0,0.06)]">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-body-mix text-sm font-semibold tracking-tight">Whale Activity</h3>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Search wallet..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="rounded-full border border-border/80 bg-transparent px-3 py-1 text-xs text-foreground placeholder:text-muted-foreground/50 focus:border-foreground focus:outline-none"
          />
          <button
            onClick={exportCsv}
            className="rounded-full border border-border/80 p-1.5 text-muted-foreground transition hover:border-foreground hover:text-foreground"
            aria-label="Export CSV"
          >
            <Download className="size-3.5" strokeWidth={1.6} />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border/60 text-muted-foreground">
              <th className="pb-2 text-left font-medium">Wallet</th>
              <th className="pb-2 text-left font-medium">Segment</th>
              <th className="pb-2 text-right font-medium">Recency (d)</th>
              <th className="pb-2 text-right font-medium">Frequency</th>
              <th className="pb-2 text-right font-medium">Volume (30d)</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="py-6 text-center text-muted-foreground">Loading...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={5} className="py-6 text-center text-muted-foreground">No whale data yet.</td></tr>
            ) : (
              filtered.slice(0, 15).map((r) => (
                <tr key={r.wallet_address} className="border-b border-border/40 last:border-0">
                  <td className="py-2 font-mono text-[11px] text-muted-foreground">{r.wallet_address?.slice(0, 10)}...</td>
                  <td className="py-2">
                    <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-medium ${SEG_STYLE[r.segment] ?? SEG_STYLE.dormant}`}>
                      {r.segment}
                    </span>
                  </td>
                  <td className="py-2 text-right tabular-nums">{r.rfm_recency != null ? Number(r.rfm_recency).toFixed(1) : '—'}</td>
                  <td className="py-2 text-right tabular-nums">{r.rfm_frequency ?? '—'}</td>
                  <td className="py-2 text-right tabular-nums font-medium">${(Number(r.rfm_volume) || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
