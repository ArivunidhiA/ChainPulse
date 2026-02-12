import { NextResponse } from 'next/server';
import { getSql } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  try {
    const sql = getSql();
    const rows = await sql`SELECT max(event_timestamp) AS ts FROM raw_events`;
    const ts = rows[0]?.ts;
    if (ts == null) return NextResponse.json({ seconds_since_last_event: null, message: 'No events yet' });
    const last = typeof ts === 'string' ? new Date(ts) : ts instanceof Date ? ts : new Date();
    const delta = Math.floor((Date.now() - last.getTime()) / 1000);
    return NextResponse.json({
      seconds_since_last_event: delta,
      last_event_at: last.toISOString(),
    });
  } catch {
    return NextResponse.json({ seconds_since_last_event: null, message: 'Error' });
  }
}
