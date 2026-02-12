// All API routes are same-origin (Next.js route handlers).

function apiPath(path: string, params?: Record<string, string | number | undefined>): string {
  if (!params || Object.keys(params).length === 0) return path;
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== '') search.set(k, String(v));
  }
  const q = search.toString();
  return q ? `${path}?${q}` : path;
}

export async function fetchStats() {
  const r = await fetch('/api/stats');
  if (!r.ok) throw new Error('Failed to fetch stats');
  return r.json();
}

export async function fetchVolume(params?: { limit?: number; token_address?: string }) {
  const path = apiPath('/api/volume', params as Record<string, string | number | undefined>);
  const r = await fetch(path);
  if (!r.ok) throw new Error('Failed to fetch volume');
  return r.json();
}

export async function fetchWhales(params?: { limit?: number; offset?: number; segment?: string }) {
  const path = apiPath('/api/whales', params as Record<string, string | number | undefined>);
  const r = await fetch(path);
  if (!r.ok) throw new Error('Failed to fetch whales');
  return r.json();
}

export async function fetchAnomalies(params?: { limit?: number; offset?: number; severity?: string }) {
  const path = apiPath('/api/anomalies', params as Record<string, string | number | undefined>);
  const r = await fetch(path);
  if (!r.ok) throw new Error('Failed to fetch anomalies');
  return r.json();
}

export async function fetchTokenFlows(params?: { limit?: number; token_address?: string }) {
  const path = apiPath('/api/token-flows', params as Record<string, string | number | undefined>);
  const r = await fetch(path);
  if (!r.ok) throw new Error('Failed to fetch token flows');
  return r.json();
}

export async function fetchProtocolHealth(params?: { limit?: number }) {
  const path = apiPath('/api/protocol-health', params as Record<string, string | number | undefined>);
  const r = await fetch(path);
  if (!r.ok) throw new Error('Failed to fetch protocol health');
  return r.json();
}

export async function fetchDataFreshness() {
  const r = await fetch('/api/data-freshness');
  if (!r.ok) return { seconds_since_last_event: null };
  return r.json();
}

export async function fetchHealth() {
  const r = await fetch('/api/health');
  return r.json();
}
