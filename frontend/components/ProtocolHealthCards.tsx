'use client';

import { useEffect, useState } from 'react';
import { fetchStats, fetchProtocolHealth } from '@/lib/api';
import { Activity, Users, ArrowLeftRight, AlertTriangle } from 'lucide-react';
import { ExpandableCard } from '@/components/ui/expandable-card';

function formatUsd(n: number) {
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(2)}K`;
  return `$${n.toFixed(0)}`;
}

type HealthRow = {
  date_bucket: string;
  unique_active_wallets: number;
  total_swaps: number;
  total_volume_usd: string;
  median_swap_size: string;
  gini_coefficient: string;
  whale_share_pct: string;
  health_score: string;
};

const CARD_META = [
  { key: 'total_volume_usd', label: 'Total Volume', icon: Activity, format: formatUsd, desc: 'Cumulative swap volume across all tracked pools.' },
  { key: 'active_wallets', label: 'Active Wallets', icon: Users, format: (v: number) => v.toLocaleString(), desc: 'Unique wallets that executed at least one swap.' },
  { key: 'total_swaps', label: 'Total Swaps', icon: ArrowLeftRight, format: (v: number) => v.toLocaleString(), desc: 'Total number of swap transactions recorded.' },
  { key: 'anomalies_count', label: 'Anomalies', icon: AlertTriangle, format: (v: number) => v.toLocaleString(), desc: 'Volume anomalies detected via Z-score analysis.' },
];

export default function ProtocolHealthCards() {
  const [stats, setStats] = useState<Record<string, number>>({});
  const [health, setHealth] = useState<HealthRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchStats(), fetchProtocolHealth({ limit: 7 })])
      .then(([s, h]) => {
        if (!cancelled) {
          setStats(s ?? {});
          setHealth(h?.data ?? []);
        }
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    const t = setInterval(() => {
      fetchStats().then((s) => { if (!cancelled) setStats(s ?? {}); });
    }, 60000);
    return () => { cancelled = true; clearInterval(t); };
  }, []);

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {CARD_META.map((c) => {
        const Icon = c.icon;
        const value = stats[c.key] ?? 0;

        return (
          <ExpandableCard
            key={c.key}
            title={c.label}
            preview={
              <div className="flex items-center gap-2">
                <Icon className="size-4 text-muted-foreground/50" strokeWidth={1.6} />
                <span className={`font-body-mix text-2xl font-semibold tracking-tight ${loading ? 'animate-pulse text-muted-foreground/40' : ''}`}>
                  {loading ? '—' : c.format(value)}
                </span>
              </div>
            }
          >
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">{c.desc}</p>
              <div className="flex items-center gap-2">
                <Icon className="size-5 text-muted-foreground/50" strokeWidth={1.6} />
                <span className="font-body-mix text-3xl font-semibold tracking-tight">
                  {loading ? '—' : c.format(value)}
                </span>
              </div>

              {health.length > 0 && (
                <>
                  <h4 className="mt-2 text-xs font-medium uppercase tracking-widest text-muted-foreground">Last 7 days</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-border/60 text-muted-foreground">
                          <th className="pb-1 text-left font-medium">Date</th>
                          <th className="pb-1 text-right font-medium">Wallets</th>
                          <th className="pb-1 text-right font-medium">Swaps</th>
                          <th className="pb-1 text-right font-medium">Volume</th>
                          <th className="pb-1 text-right font-medium">Health</th>
                        </tr>
                      </thead>
                      <tbody>
                        {health.map((r) => (
                          <tr key={r.date_bucket} className="border-b border-border/30 last:border-0">
                            <td className="py-1.5 text-muted-foreground">{r.date_bucket?.slice(0, 10)}</td>
                            <td className="py-1.5 text-right tabular-nums">{r.unique_active_wallets}</td>
                            <td className="py-1.5 text-right tabular-nums">{r.total_swaps}</td>
                            <td className="py-1.5 text-right tabular-nums">{formatUsd(Number(r.total_volume_usd))}</td>
                            <td className="py-1.5 text-right tabular-nums font-medium">{Number(r.health_score).toFixed(1)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          </ExpandableCard>
        );
      })}
    </div>
  );
}
