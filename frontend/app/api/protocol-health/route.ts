import { NextRequest, NextResponse } from 'next/server';
import { getSql, serializeRow } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const limit = Math.min(90, Math.max(1, Number(searchParams.get('limit')) || 30));
  try {
    const sql = getSql();
    const rows = await sql`SELECT date_bucket, unique_active_wallets, total_swaps, total_volume_usd, median_swap_size, gini_coefficient, whale_share_pct, health_score FROM analytics_protocol_health ORDER BY date_bucket DESC LIMIT ${limit}`;
    return NextResponse.json({ data: rows.map(serializeRow), limit });
  } catch {
    return NextResponse.json({ data: [], limit });
  }
}
