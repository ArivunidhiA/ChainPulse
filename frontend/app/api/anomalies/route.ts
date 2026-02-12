import { NextRequest, NextResponse } from 'next/server';
import { getSql, serializeRow } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const limit = Math.min(200, Math.max(1, Number(searchParams.get('limit')) || 50));
  const offset = Math.max(0, Number(searchParams.get('offset')) || 0);
  const severity = searchParams.get('severity')?.toLowerCase().trim() || null;
  const token_address = searchParams.get('token_address')?.toLowerCase().trim() || null;
  try {
    const sql = getSql();
    let rows: Record<string, unknown>[];
    if (severity && token_address) {
      rows = await sql`SELECT anomaly_id, hour_bucket, token_address, actual_volume, expected_volume, z_score, severity, detected_at FROM analytics_anomalies WHERE severity = ${severity} AND token_address = ${token_address} ORDER BY detected_at DESC LIMIT ${limit} OFFSET ${offset}`;
    } else if (severity) {
      rows = await sql`SELECT anomaly_id, hour_bucket, token_address, actual_volume, expected_volume, z_score, severity, detected_at FROM analytics_anomalies WHERE severity = ${severity} ORDER BY detected_at DESC LIMIT ${limit} OFFSET ${offset}`;
    } else if (token_address) {
      rows = await sql`SELECT anomaly_id, hour_bucket, token_address, actual_volume, expected_volume, z_score, severity, detected_at FROM analytics_anomalies WHERE token_address = ${token_address} ORDER BY detected_at DESC LIMIT ${limit} OFFSET ${offset}`;
    } else {
      rows = await sql`SELECT anomaly_id, hour_bucket, token_address, actual_volume, expected_volume, z_score, severity, detected_at FROM analytics_anomalies ORDER BY detected_at DESC LIMIT ${limit} OFFSET ${offset}`;
    }
    return NextResponse.json({ data: rows.map(serializeRow), limit, offset });
  } catch {
    return NextResponse.json({ data: [], limit, offset });
  }
}
