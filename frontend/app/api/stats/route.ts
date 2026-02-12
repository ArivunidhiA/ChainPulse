import { NextResponse } from 'next/server';
import { getSql } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  const out = { total_volume_usd: 0, active_wallets: 0, total_swaps: 0, anomalies_count: 0 };
  try {
    const sql = getSql();
    // Volume
    try {
      const r = await sql`SELECT coalesce(sum(total_volume_usd), 0) AS v FROM analytics_protocol_health`;
      if (r[0]) out.total_volume_usd = Number(r[0].v ?? 0);
    } catch {
      try {
        const r = await sql`SELECT coalesce(sum(usd_value), 0) AS v FROM raw_swaps`;
        if (r[0]) out.total_volume_usd = Number(r[0].v ?? 0);
      } catch {}
    }
    // Active wallets
    try {
      const r = await sql`SELECT unique_active_wallets AS v FROM analytics_protocol_health ORDER BY date_bucket DESC LIMIT 1`;
      if (r[0]) out.active_wallets = Number(r[0].v ?? 0);
    } catch {
      try {
        const r = await sql`SELECT count(DISTINCT sender_address) AS v FROM raw_swaps`;
        if (r[0]) out.active_wallets = Number(r[0].v ?? 0);
      } catch {}
    }
    // Total swaps
    try {
      const r = await sql`SELECT coalesce(sum(total_swaps), 0) AS v FROM analytics_protocol_health`;
      if (r[0]) out.total_swaps = Number(r[0].v ?? 0);
    } catch {
      try {
        const r = await sql`SELECT count(*) AS v FROM raw_swaps`;
        if (r[0]) out.total_swaps = Number(r[0].v ?? 0);
      } catch {}
    }
    // Anomalies
    try {
      const r = await sql`SELECT count(*) AS v FROM analytics_anomalies`;
      if (r[0]) out.anomalies_count = Number(r[0].v ?? 0);
    } catch {}
  } catch {
    // DB not available at all — return zeros
  }
  return NextResponse.json(out);
}
