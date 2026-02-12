'use client';

import { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { fetchVolume } from '@/lib/api';

const RANGES = [
  { label: '6h', limit: 6 },
  { label: '24h', limit: 24 },
  { label: '7d', limit: 168 },
];

export default function VolumeChart() {
  const [data, setData] = useState<{ hour_bucket: string; volume_usd?: number }[]>([]);
  const [range, setRange] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchVolume({ limit: range })
      .then((res) => {
        if (!cancelled) {
          const list = (res?.data || []).slice().reverse();
          const byHour: Record<string, number> = {};
          list.forEach((r: { hour_bucket?: string; volume_usd?: number }) => {
            const h = r.hour_bucket?.slice(0, 16) ?? '';
            byHour[h] = (byHour[h] || 0) + Number(r.volume_usd ?? 0);
          });
          setData(Object.entries(byHour).map(([hour_bucket, volume_usd]) => ({ hour_bucket, volume_usd })));
        }
      })
      .catch(() => { if (!cancelled) setData([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [range]);

  return (
    <div className="rounded-2xl border border-border/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm transition-all duration-200 ease-out hover:-translate-y-[2px] hover:shadow-[0_6px_20px_rgba(0,0,0,0.06)]">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-body-mix text-sm font-semibold tracking-tight">Volume Trend</h3>
        <div className="flex gap-1">
          {RANGES.map((r) => (
            <button
              key={r.label}
              onClick={() => setRange(r.limit)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                range === r.limit
                  ? 'border border-foreground bg-foreground text-white'
                  : 'border border-border/80 text-muted-foreground hover:border-foreground hover:text-foreground'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>
      <div className="h-64">
        {loading ? (
          <div className="flex h-full items-center justify-center text-xs text-muted-foreground">Loading...</div>
        ) : data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
            No volume data yet. Run the indexer to start collecting swap data.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="vol" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(222,47%,11%)" stopOpacity={0.12} />
                  <stop offset="100%" stopColor="hsl(222,47%,11%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,22%,87%)" strokeOpacity={0.6} />
              <XAxis
                dataKey="hour_bucket"
                tick={{ fill: 'hsl(215,16%,47%)', fontSize: 10 }}
                axisLine={{ stroke: 'hsl(214,22%,87%)' }}
                tickLine={false}
                tickFormatter={(v: string) => v.slice(11, 16)}
              />
              <YAxis
                tick={{ fill: 'hsl(215,16%,47%)', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) =>
                  v >= 1e6 ? `$${(v / 1e6).toFixed(1)}M` : `$${(v / 1e3).toFixed(0)}K`
                }
              />
              <Tooltip
                contentStyle={{
                  background: 'white',
                  border: '1px solid hsl(214,22%,87%)',
                  borderRadius: '12px',
                  fontSize: '12px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.06)',
                }}
                formatter={(v: number) => [`$${v.toLocaleString()}`, 'Volume']}
                labelFormatter={(l: string) => l.slice(0, 16)}
              />
              <Area
                type="monotone"
                dataKey="volume_usd"
                stroke="hsl(222,47%,11%)"
                strokeWidth={1.5}
                fill="url(#vol)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
