'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import ProtocolHealthCards from '@/components/ProtocolHealthCards';
import VolumeChart from '@/components/VolumeChart';
import WhaleTracker from '@/components/WhaleTracker';
import AnomalyFeed from '@/components/AnomalyFeed';
import TokenFlowHeatmap from '@/components/TokenFlowHeatmap';
import { fetchDataFreshness } from '@/lib/api';

export default function DashboardPage() {
  const [freshness, setFreshness] = useState<{ seconds_since_last_event?: number | null } | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchDataFreshness()
      .then((d) => { if (!cancelled) setFreshness(d); })
      .catch(() => {});
    const t = setInterval(() => {
      fetchDataFreshness().then((d) => { if (!cancelled) setFreshness(d); });
    }, 30000);
    return () => { cancelled = true; clearInterval(t); };
  }, []);

  const lagLabel =
    freshness?.seconds_since_last_event != null
      ? freshness.seconds_since_last_event < 60
        ? `${freshness.seconds_since_last_event}s ago`
        : `${Math.round(freshness.seconds_since_last_event / 60)}m ago`
      : '—';

  return (
    <main className="mx-auto max-w-7xl px-4 pb-14 pt-8 md:px-6 md:pt-12">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 rounded-full border border-border/80 px-3 py-1.5 text-xs font-medium text-muted-foreground transition hover:border-foreground hover:text-foreground"
          >
            <ArrowLeft className="size-3" />
            Home
          </Link>
          <div>
            <h1 className="font-body-mix text-xl font-semibold tracking-tight">Dashboard</h1>
            <p className="text-xs text-muted-foreground">Real-time protocol &amp; whale monitoring</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="relative flex size-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex size-1.5 rounded-full bg-emerald-500" />
          </span>
          <span className="text-xs text-muted-foreground">Last sync: {lagLabel}</span>
        </div>
      </header>

      {/* KPI Cards */}
      <section className="mb-8">
        <ProtocolHealthCards />
      </section>

      {/* Volume Chart */}
      <section className="mb-8">
        <VolumeChart />
      </section>

      {/* Two-column: Whales + Anomalies */}
      <div className="mb-8 grid gap-8 lg:grid-cols-2">
        <WhaleTracker />
        <AnomalyFeed />
      </div>

      {/* Token Flows */}
      <section>
        <TokenFlowHeatmap />
      </section>
    </main>
  );
}
