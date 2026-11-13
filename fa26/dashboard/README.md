# FOIA dashboard (Vercel + Supabase)

Interactive dashboard for MuckRock's FOIA annual report data (foia.gov, FY2008–2025).
The site is a static Vite app hosted on **Vercel**. It reads its data directly from a **Supabase** (Postgres) database
through Supabase's built-in REST API, so there is no separate backend server.

```
foia.gov ─► fa26/dataset/component_level (Tianqi's component master)
          ─► supabase/build_tables.py  ─► Supabase tables (read-only for the public)
                                          ─► this site on Vercel (anon key, SELECT only)
```

## Folder

| Path | What it is |
|---|---|
| `index.html`, `src/main.js` | the dashboard (period selector, agency / component dropdowns, 32 data types in 6 topics, Chart.js) |
| `src/db.js` | read-only calls to the Supabase REST API (paged, CSV for the big table) |
| `supabase/schema.sql` | tables + row-level security (public can only read) |
| `supabase/build_tables.py` | builds the tables from the component master and loads them |
| `.env.example` | the two settings the site needs |

## Tables

| Table | Rows | What |
|---|---|---|
| `foia_rows` | ~8,100 | one row per agency / component per year; one numeric column per metric (115) |
| `metrics` | 115 | metric key, column name, and how to combine it (`sum` counts, `avg` days → median, `max` oldest item) |
| `agencies` | 128 | id, name, abbreviation |
| `components` | ~450 | components of each agency |
| `statutes_top` | ~2,300 | top 3 Exemption 3 statutes per agency and year |

The whole database is about 15 MB, well under the Supabase free plan's 500 MB.
The site only downloads the columns of the data type on screen (as CSV), so each view is a few hundred KB.

## Setup (one time)

### 1. Supabase
1. Create a free project at https://supabase.com (save the database password).
2. **SQL Editor** → paste `supabase/schema.sql` → Run.
3. Load the data (from this folder):
   ```bash
   pip install pandas numpy "psycopg[binary]"
   export DATABASE_URL="<Project Settings > Database > Connection string > Session pooler (URI)>"
   python supabase/build_tables.py \
     --master   ../dataset/component_level/component_master_no_03_06_11.csv \
     --statutes ../dataset/component_level/exemption_statutes_06.csv \
     --load
   ```
   Use the **Session pooler** string (IPv4). The direct connection string is IPv6-only on the free plan.
4. **Project Settings → API**: copy the *Project URL* and the *anon public* key.

### 2. Run locally
```bash
cp .env.example .env.local      # paste the URL and anon key
npm install
npm run dev                     # http://localhost:5173
```

### 3. Vercel
1. https://vercel.com → **Add New → Project** → import `BU-Spark/ds-muckrock-liberation`.
2. **Root Directory**: `fa26/dashboard`. Framework preset: **Vite** (build `npm run build`, output `dist`).
3. **Environment Variables**: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
4. Under **Settings → Git**, set the production branch to the branch that holds this folder.
5. Deploy. Every push to that branch redeploys.

## Updating the data
Re-run `build_tables.py --load` with the new component master. It empties the tables and reloads them; the site needs no change.
If schema columns change (new metrics), regenerate the schema with `--schema-out supabase/schema.sql` and run it again first.

## Free-plan notes
- Supabase pauses a free project after 7 days with no activity. A scheduled ping (GitHub Actions or an uptime monitor)
  or regular visits keep it awake; a paused project can be restored from the dashboard without losing data.
- Free egress is 5 GB/month. The site loads only what each view needs.
- Vercel's free Hobby plan is for personal, non-commercial use. Check with MuckRock before production, or host under their account.

## Security
- The anon key is public by design. Row-level security allows only `SELECT` on these tables.
- Never put the database password or the `service_role` key in the site or in git. `.env.local` is git-ignored.
