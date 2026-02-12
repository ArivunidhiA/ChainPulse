import { NextRequest, NextResponse } from 'next/server';
import { getSql, serializeRow } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const limit = Math.min(500, Math.max(1, Number(searchParams.get('limit')) || 100));
  const offset = Math.max(0, Number(searchParams.get('offset')) || 0);
  const segment = searchParams.get('segment')?.toLowerCase().trim() || null;
  try {
    const sql = getSql();
    const rows = segment
      ? await sql`SELECT wallet_address, segment, cluster_id, rfm_recency, rfm_frequency, rfm_volume, computed_at FROM analytics_wallet_segments WHERE segment = ${segment} ORDER BY rfm_volume DESC NULLS LAST LIMIT ${limit} OFFSET ${offset}`
      : await sql`SELECT wallet_address, segment, cluster_id, rfm_recency, rfm_frequency, rfm_volume, computed_at FROM analytics_wallet_segments ORDER BY rfm_volume DESC NULLS LAST LIMIT ${limit} OFFSET ${offset}`;
    return NextResponse.json({ data: rows.map(serializeRow), limit, offset });
  } catch {
    return NextResponse.json({ data: [], limit, offset });
  }
}
