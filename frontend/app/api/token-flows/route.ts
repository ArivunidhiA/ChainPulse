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
    const rows = token_address
      ? await sql`SELECT hour_bucket, token_address, inflow_usd, outflow_usd, net_flow_usd, unique_senders, unique_receivers, flow_direction FROM analytics_token_flows WHERE token_address = ${token_address} ORDER BY hour_bucket DESC LIMIT ${limit}`
      : await sql`SELECT hour_bucket, token_address, inflow_usd, outflow_usd, net_flow_usd, unique_senders, unique_receivers, flow_direction FROM analytics_token_flows ORDER BY hour_bucket DESC LIMIT ${limit}`;
    return NextResponse.json({ data: rows.map(serializeRow), limit });
  } catch {
    return NextResponse.json({ data: [], limit });
  }
}
