// Анонімні лічильники Supabase. Без VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY
// сайт працює повністю — просто без бейджів популярності.
const URL = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

export const telemetryOn = Boolean(URL && KEY);

export type CopyKind =
  | "marketplace"
  | "plugin"
  | "skill-view"
  | "skill-prompt"
  | "all-terminal"
  | "all-prompt";

export function track(kind: CopyKind, item: string): void {
  if (!telemetryOn) return;
  fetch(`${URL}/rest/v1/copy_events`, {
    method: "POST",
    headers: {
      apikey: KEY!,
      Authorization: `Bearer ${KEY}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify({ kind, item: item.slice(0, 80) }),
  }).catch(() => undefined);
}

export interface Counts {
  bySkill: Record<string, number>;
}

export async function fetchCounts(): Promise<Counts> {
  if (!telemetryOn) return { bySkill: {} };
  try {
    const r = await fetch(
      `${URL}/rest/v1/copy_counts?select=kind,item,copies&kind=in.(skill-view,skill-prompt)`,
      { headers: { apikey: KEY!, Authorization: `Bearer ${KEY}` } },
    );
    if (!r.ok) return { bySkill: {} };
    const rows: { kind: string; item: string; copies: number }[] = await r.json();
    const bySkill: Record<string, number> = {};
    for (const row of rows) bySkill[row.item] = (bySkill[row.item] ?? 0) + row.copies;
    return { bySkill };
  } catch {
    return { bySkill: {} };
  }
}

export function topSkills(counts: Counts, n: number): Set<string> {
  const entries = Object.entries(counts.bySkill).sort((a, b) => b[1] - a[1]);
  return new Set(entries.slice(0, n).map(([name]) => name));
}
