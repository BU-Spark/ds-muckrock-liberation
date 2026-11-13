// Read-only access to the Supabase REST API (PostgREST). No library needed.
// The anon key is public by design: the tables only allow SELECT (see supabase/schema.sql).
const BASE = (import.meta.env.VITE_SUPABASE_URL || "").replace(/\/$/, "");
const KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || "";
const PAGE = 1000; // Supabase returns at most 1000 rows per request by default

export const configured = Boolean(BASE && KEY);

function headers(extra = {}) {
  return { apikey: KEY, Authorization: `Bearer ${KEY}`, ...extra };
}

async function request(path, { accept = "application/json", from = 0, count = false } = {}) {
  const res = await fetch(`${BASE}/rest/v1/${path}`, {
    headers: headers({
      Accept: accept,
      "Range-Unit": "items",
      Range: `${from}-${from + PAGE - 1}`,
      ...(count ? { Prefer: "count=exact" } : {}),
    }),
  });
  if (!res.ok && res.status !== 206) throw new Error(`${res.status} ${await res.text()}`);
  const total = Number((res.headers.get("Content-Range") || "").split("/")[1]);
  return { body: accept === "text/csv" ? await res.text() : await res.json(), total };
}

// All pages of a query, fetched in parallel after the first one tells us the total.
async function pages(path, accept) {
  const first = await request(path, { accept, count: true });
  const total = Number.isFinite(first.total) ? first.total : 0;
  const rest = [];
  for (let from = PAGE; from < total; from += PAGE) rest.push(request(path, { accept, from }));
  return [first.body, ...(await Promise.all(rest)).map((r) => r.body)];
}

// JSON rows of a small table
export async function getJson(table, select = "*", order = "") {
  const q = `${table}?select=${select}${order ? `&order=${order}` : ""}`;
  return (await pages(q, "application/json")).flat();
}

// Numeric columns of foia_rows as CSV (much smaller than JSON). Returns {header, rows: string[][]}
export async function getRowsCsv(cols) {
  const q = `foia_rows?select=${["id", ...cols].join(",")}&order=id`;
  const parts = await pages(q, "text/csv");
  let header = null;
  const rows = [];
  for (const txt of parts) {
    const lines = txt.split("\n").filter(Boolean);
    if (!lines.length) continue;
    header = lines[0].split(",");
    for (let i = 1; i < lines.length; i++) rows.push(lines[i].split(","));
  }
  return { header: header || ["id", ...cols], rows };
}
