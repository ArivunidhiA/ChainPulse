import { NextRequest, NextResponse } from 'next/server';
import { getSql, serializeRow } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const limit = Math.min(720, Math.max(1, Number(searchParams.get('limit')) || 168));
  const token_address = searchParams.get('token_address')?.toLowerCase().trim() || null;
  try {
    const sql = getSql();
    // Try raw_swaps first (always exists after schema.sql)
    const rows = token_address
      ? await sql`SELECT date_trunc('hour', event_timestamp) AS hour_bucket, token0_address AS token_address, count(*)::int AS swap_count, coalesce(sum(usd_value), 0) AS volume_usd, count(DISTINCT sender_address)::int AS unique_wallets FROM raw_swaps WHERE token0_address = ${token_address} OR token1_address = ${token_address} GROUP BY 1, 2 ORDER BY 1 DESC LIMIT ${limit}`
      : await sql`SELECT date_trunc('hour', event_timestamp) AS hour_bucket, token0_address AS token_address, count(*)::int AS swap_count, coalesce(sum(usd_value), 0) AS volume_usd, count(DISTINCT sender_address)::int AS unique_wallets FROM raw_swaps GROUP BY 1, 2 ORDER BY 1 DESC LIMIT ${limit}`;
    return NextResponse.json({ data: rows.map(serializeRow), limit });
  } catch {
    return NextResponse.json({ data: [], limit });
  }
}
