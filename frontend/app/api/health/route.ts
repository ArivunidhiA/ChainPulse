import { NextResponse } from 'next/server';
import { getSql } from '@/lib/db';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  try {
    const sql = getSql();
    await sql`SELECT 1`;
    return NextResponse.json({ status: 'ok', db: 'connected' });
  } catch (e) {
    return NextResponse.json({ status: 'error', db: String(e) }, { status: 503 });
  }
}
