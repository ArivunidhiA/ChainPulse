'use client';

import { useEffect, useState } from 'react';
import { fetchTokenFlows } from '@/lib/api';
import { Download } from 'lucide-react';

type Row = {
  hour_bucket: string;
  token_address: string;
  inflow_usd: number;
  outflow_usd: number;
  net_flow_usd: number;
  flow_direction: string;
};

export default function TokenFlowHeatmap() {
  const [data, setData] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchTokenFlows({ limit: 168 })
      .then((res) => { if (!cancelled) setData(res?.data || []); })
      .catch(() => { if (!cancelled) setData([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const byToken = data.reduce((acc, r) => {
    const t = r.token_address?.slice(0, 10) ?? '';
    if (!acc[t]) acc[t] = [];
    acc[t].push(r);
    return acc;
  }, {} as Record<string, Row[]>);

  const exportCsv = () => {
    const headers = ['hour_bucket', 'token_address', 'inflow_usd', 'outflow_usd', 'net_flow_usd', 'flow_direction'];
    const rows = data.map((r) => headers.map((h) => (r as Record<string, unknown>)[h] ?? '').join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'token_flows.csv';
    a.click();
  };

  return (
    <div className="rounded-2xl border border-border/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm transition-all duration-200 ease-out hover:-translate-y-[2px] hover:shadow-[0_6px_20px_rgba(0,0,0,0.06)]">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-body-mix text-sm font-semibold tracking-tight">Token Flow</h3>
        <button
          onClick={exportCsv}
          className="rounded-full border border-border/80 p-1.5 text-muted-foreground transition hover:border-foreground hover:text-foreground"
          aria-label="Export CSV"
        >
          <Download className="size-3.5" strokeWidth={1.6} />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border/60 text-muted-foreground">
              <th className="pb-2 pr-4 text-left font-medium">Token</th>
              <th className="pb-2 pr-4 text-left font-medium">Hour</th>
              <th className="pb-2 pr-4 text-right font-medium">Inflow</th>
              <th className="pb-2 pr-4 text-right font-medium">Outflow</th>
              <th className="pb-2 pr-6 text-right font-medium">Net</th>
              <th className="pb-2 pl-2 text-left font-medium">Direction</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="py-6 text-center text-muted-foreground">Loading...</td></tr>
            ) : Object.keys(byToken).length === 0 ? (
              <tr><td colSpan={6} className="py-6 text-center text-muted-foreground">No token flow data yet.</td></tr>
            ) : (
              Object.entries(byToken).flatMap(([tok, rows]) =>
                rows.slice(0, 5).map((r) => (
                  <tr key={`${tok}-${r.hour_bucket}`} className="border-b border-border/40 last:border-0">
                    <td className="py-2 pr-4 font-mono text-[11px] text-muted-foreground">{tok}</td>
                    <td className="py-2 pr-4 text-muted-foreground/60">{r.hour_bucket?.slice(11, 16)}</td>
                    <td className="py-2 pr-4 text-right tabular-nums text-emerald-600">
                      ${(Number(r.inflow_usd) || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2 pr-4 text-right tabular-nums text-red-500">
                      ${(Number(r.outflow_usd) || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2 pr-6 text-right tabular-nums font-medium">
                      ${(Number(r.net_flow_usd) || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2 pl-2">
                      <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-medium ${
                        r.flow_direction === 'accumulation'
                          ? 'border-emerald-300 bg-emerald-50 text-emerald-700'
                          : 'border-red-200 bg-red-50 text-red-600'
                      }`}>
                        {r.flow_direction || 'neutral'}
                      </span>
                    </td>
                  </tr>
                ))
              )
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
