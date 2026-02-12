import { neon } from '@neondatabase/serverless';

function getDbUrl(): string {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
  if (!url) throw new Error('DATABASE_URL or POSTGRES_URL is required');
  return url;
}

export function getSql() {
  return neon(getDbUrl());
}

function serializeValue(v: unknown): unknown {
  if (v instanceof Date) return v.toISOString();
  if (typeof v === 'bigint') return Number(v);
  if (v !== null && typeof v === 'object' && 'toNumber' in (v as object)) return Number((v as { toNumber: () => number }).toNumber());
  return v;
}

export function serializeRow(row: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(row)) out[k] = serializeValue(v);
  return out;
}
