import { NextRequest, NextResponse } from 'next/server';
import { getSql, serializeRow } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const limit = Math.min(1000, Math.max(1, Number(searchParams.get('limit')) || 100));
  const offset = Math.max(0, Number(searchParams.get('offset')) || 0);
  const token_address = searchParams.get('token_address')?.toLowerCase().trim() || null;
  const wallet_address = searchParams.get('wallet_address')?.toLowerCase().trim() || null;
  try {
    const sql = getSql();
    let rows: Record<string, unknown>[];
    if (token_address && wallet_address) {
      rows = await sql`SELECT block_number, tx_hash, sender_address AS wallet_address, token0_address AS token_in_address, token1_address AS token_out_address, amount0 AS amount_in, amount1 AS amount_out, usd_value AS amount_usd, pool_address, event_timestamp, size_bucket FROM raw_swaps WHERE (token0_address = ${token_address} OR token1_address = ${token_address}) AND sender_address = ${wallet_address} ORDER BY event_timestamp DESC LIMIT ${limit} OFFSET ${offset}`;
    } else if (token_address) {
      rows = await sql`SELECT block_number, tx_hash, sender_address AS wallet_address, token0_address AS token_in_address, token1_address AS token_out_address, amount0 AS amount_in, amount1 AS amount_out, usd_value AS amount_usd, pool_address, event_timestamp, size_bucket FROM raw_swaps WHERE token0_address = ${token_address} OR token1_address = ${token_address} ORDER BY event_timestamp DESC LIMIT ${limit} OFFSET ${offset}`;
    } else if (wallet_address) {
      rows = await sql`SELECT block_number, tx_hash, sender_address AS wallet_address, token0_address AS token_in_address, token1_address AS token_out_address, amount0 AS amount_in, amount1 AS amount_out, usd_value AS amount_usd, pool_address, event_timestamp, size_bucket FROM raw_swaps WHERE sender_address = ${wallet_address} ORDER BY event_timestamp DESC LIMIT ${limit} OFFSET ${offset}`;
    } else {
      rows = await sql`SELECT block_number, tx_hash, sender_address AS wallet_address, token0_address AS token_in_address, token1_address AS token_out_address, amount0 AS amount_in, amount1 AS amount_out, usd_value AS amount_usd, pool_address, event_timestamp, size_bucket FROM raw_swaps ORDER BY event_timestamp DESC LIMIT ${limit} OFFSET ${offset}`;
    }
    return NextResponse.json({ data: rows.map(serializeRow), limit, offset });
  } catch {
    return NextResponse.json({ data: [], limit, offset });
  }
}
