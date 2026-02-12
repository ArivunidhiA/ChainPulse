'use client';

import { useEffect, useState } from 'react';
import { fetchAnomalies } from '@/lib/api';
import { Download } from 'lucide-react';

type Row = {
  anomaly_id: string;
  hour_bucket: string;
  token_address: string;
  actual_volume: number;
  expected_volume: number;
  z_score: number;
  severity: string;
};

const SEV_STYLE: Record<string, string> = {
  critical: 'border-red-300 bg-red-50 text-red-700',
  high: 'border-orange-300 bg-orange-50 text-orange-700',
  medium: 'border-amber-300 bg-amber-50 text-amber-700',
  low: 'border-border bg-muted text-muted-foreground',
};

export default function AnomalyFeed() {
  const [data, setData] = useState<Row[]>([]);
  const [severity, setSeverity] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchAnomalies({ limit: 50, severity: severity || undefined })
      .then((res) => { if (!cancelled) setData(res?.data || []); })
      .catch(() => { if (!cancelled) setData([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [severity]);

  const exportCsv = () => {
    const headers = ['hour_bucket', 'token_address', 'actual_volume', 'expected_volume', 'z_score', 'severity'];
    const rows = data.map((r) => headers.map((h) => (r as Record<string, unknown>)[h] ?? '').join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'anomalies.csv';
    a.click();
  };

  return (
    <div className="rounded-2xl border border-border/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm transition-all duration-200 ease-out hover:-translate-y-[2px] hover:shadow-[0_6px_20px_rgba(0,0,0,0.06)]">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-body-mix text-sm font-semibold tracking-tight">Anomaly Feed</h3>
        <div className="flex items-center gap-2">
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="rounded-full border border-border/80 bg-transparent px-3 py-1 text-xs text-foreground focus:border-foreground focus:outline-none"
          >
            <option value="">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
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
              <th className="pb-2 pr-3 text-left font-medium">Severity</th>
              <th className="pb-2 pr-3 text-left font-medium">Token</th>
              <th className="pb-2 pr-3 text-left font-medium">Time</th>
              <th className="pb-2 pr-3 text-right font-medium">Z-Score</th>
              <th className="pb-2 text-right font-medium">Volume</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="py-6 text-center text-muted-foreground">Loading...</td></tr>
            ) : data.length === 0 ? (
              <tr><td colSpan={5} className="py-6 text-center text-muted-foreground">No anomalies detected.</td></tr>
            ) : (
              data.slice(0, 15).map((r) => (
                <tr key={r.anomaly_id} className="border-b border-border/40 last:border-0">
                  <td className="py-2 pr-3">
                    <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-medium ${SEV_STYLE[r.severity] ?? SEV_STYLE.low}`}>
                      {r.severity}
                    </span>
                  </td>
                  <td className="py-2 pr-3 font-mono text-[11px] text-muted-foreground">{r.token_address?.slice(0, 10)}...</td>
                  <td className="py-2 pr-3 text-muted-foreground/60">{r.hour_bucket?.slice(0, 16)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{Number(r.z_score)?.toFixed(2)}</td>
                  <td className="py-2 text-right tabular-nums font-medium">${(Number(r.actual_volume) ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
