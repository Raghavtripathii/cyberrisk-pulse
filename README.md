# CyberRisk Pulse

A Power BI dashboard that turns vulnerability scan findings into the kind
of risk report a security manager actually uses — what's overdue, what's
riskiest, and whether the team is getting better or worse at fixing
things.

Built on top of my own security tooling ([VulnScan](#) and
[Vault Notes](#) — link your repos here), enriched with real CVE data
from the public NVD database, and modeled as a proper star schema
instead of one flat spreadsheet.

---

## 1. What problem this solves (read this first)

Imagine you're the security manager at a company. Scans keep finding
vulnerabilities. Tickets pile up. You have three questions and no easy
way to answer any of them:

1. **What's actually urgent right now** — not just "Critical," but
   Critical *and* already past its deadline?
2. **Is my team keeping its promises?** We say we'll fix Critical
   issues in 7 days — are we actually doing that?
3. **Are things getting better?** Is our overall risk going up or down
   month over month?

This project builds the dashboard that answers all three.

---

## 2. How the whole thing fits together

```
Your VulnScan output  ──┐
                         │
Real CVE data (NVD API) ─┼──►  Python scripts  ──►  Clean tables (star schema)  ──►  Power BI Dashboard
                         │        (scripts/)          (data/*.csv + cyberrisk.db)
Remediation tracker ─────┘
  (synthetic, documented)
```

In short: three small Python scripts create the raw data, one Python
script cleans and joins it into a proper data model, and then Power BI
just visualizes tables that are already clean. That order matters — a
lot of beginner projects skip straight to Power Query and end up doing
all their transformation logic inside the BI tool, which gets messy
fast and is hard to explain in an interview.

---

## 3. Folder structure

```
cyberrisk-pulse/
├── README.md                  <- you are here
├── requirements.txt            <- Python packages needed
├── scripts/                    <- run these in order, 01 -> 04
│   ├── 01_generate_vulnscan_data.py
│   ├── 02_fetch_nvd_cve_data.py
│   ├── 03_generate_remediation_tracker.py
│   └── 04_etl_build_star_schema.py
├── sql/
│   └── schema.sql               <- the star schema, written as plain SQL
├── dax/
│   └── measures.md               <- every DAX formula, explained in plain English
├── docs/
│   ├── data_dictionary.md        <- what every column means
│   ├── design_decisions.md       <- why I built it this way (interview prep)
│   └── executive_memo_template.md
└── data/                          <- generated CSVs + the SQLite DB land here (not committed to git)
```

---

## 4. Step-by-step: how to build this yourself

### Step 0 — set up
```bash
git clone <your-repo-url>
cd cyberrisk-pulse
pip install -r requirements.txt
```

### Step 1 — generate the raw findings
```bash
python scripts/01_generate_vulnscan_data.py
```
This writes `data/raw_findings.csv`. If you already have a real export
from your VulnScan tool, put it at that exact path instead and skip
this script — the rest of the pipeline doesn't care where the file
came from, only that it has the right columns (see the data dictionary).

### Step 2 — pull real CVE data
```bash
python scripts/02_fetch_nvd_cve_data.py
```
This hits the public NVD API and writes `data/cve_enrichment.csv`. It's
a free public API with no key needed, but it asks you to go slow, so
this script pauses a few seconds between requests — it'll take about
30 seconds to finish, that's expected.

*Note: if you're running this from a restricted network (like a
sandboxed environment) and the NVD API isn't reachable, that's fine —
step 4 is written to skip this gracefully and fall back to baseline
severity scores instead.*

### Step 3 — build the remediation tracker
```bash
python scripts/03_generate_remediation_tracker.py
```
Writes `data/remediation_tracker.csv` — assigns an owner, a due date
based on the SLA policy, and a status to every finding.

### Step 4 — run the ETL
```bash
python scripts/04_etl_build_star_schema.py
```
This is the important one. It joins all three sources together and
writes out five clean tables — `fact_vulnerabilities`, `dim_asset`,
`dim_severity`, `dim_owasp_category`, `dim_date` — both as CSVs and as
a SQLite database (`data/cyberrisk.db`).

### Step 5 — bring it into Power BI Desktop
1. Open Power BI Desktop → **Get Data** → **Text/CSV** → import all
   five CSVs from the `data/` folder (or use **Get Data → ODBC/SQLite**
   to connect directly to `cyberrisk.db` if you'd rather work from one
   file).
2. Go to **Model view**. Power BI will likely auto-detect the
   relationships — check that each one matches `sql/schema.sql`:
   `fact_vulnerabilities[asset_id] → dim_asset[asset_id]`, and the same
   pattern for severity, owasp_category, and both date columns to
   `dim_date[date]`.
3. Mark `dim_date` as a **Date Table** (Model view → click dim_date →
   "Mark as date table" in the ribbon). This unlocks proper time
   intelligence for the DAX measures that use `DATEADD`.

### Step 6 — add the DAX measures
Open `dax/measures.md` and add each measure exactly as described there
— it explains what each one means before giving you the formula, so
you can explain it in your own words later.

### Step 7 — build the five report pages
1. **Executive Summary** — Risk Score card with a trend arrow, SLA
   Compliance % card, Overdue Critical Count card, and a bar chart of
   top 3 riskiest assets by weighted risk.
2. **Vulnerability Deep-Dive** — a filterable table of findings, a
   donut chart of CVSS score distribution, slicers for severity and
   OWASP category.
3. **Remediation & SLA Tracking** — a bar chart of the Aging Bucket
   column, a line chart of SLA Compliance % over time, a table of
   overdue findings by owner.
4. **Trend & Historical View** — a line chart of Risk Score over time,
   and a combo chart of findings opened vs. findings closed per month.
5. **Asset Risk Heatmap** — a matrix visual with business unit on rows,
   severity on columns, and count of open findings as the values,
   conditional-formatted red/amber/green.

Keep to 2-3 colors plus a red/amber/green risk scale. Title every visual
with the business question it answers, not just the field names in it.

### Step 8 — write the executive memo
Fill in `docs/executive_memo_template.md` using the actual numbers your
dashboard produces. This is what you talk through first in an
interview — the dashboard is the evidence, the memo is the conclusion.

### Step 9 — publish
- Push this repo to GitHub (commit history is already there from
  building it — each script and doc is its own commit).
- Export the Power BI report pages as images or a short screen
  recording for your portfolio site, since a `.pbix` file itself isn't
  easily embedded on the web.
- Link back to your VulnScan and Vault Notes repos in this README so
  the whole story reads as one connected body of work.

---

## 5. What this project demonstrates

- **SQL & Python ETL** — real joins, cleaning, and transformation logic
- **Proper data modeling** — a real star schema, not a flat table
- **DAX including time intelligence** — not just SUM() and COUNT()
- **A real external API integration** — live data from NVD, not just a
  downloaded Kaggle CSV
- **A custom-designed KPI** — the weighted Risk Score, with the
  reasoning behind it written down
- **Documentation** — data dictionary, design decisions, executive memo
- **Domain expertise** — tied directly into real security tooling I
  built myself, not a generic retail/HR dataset everyone else uses

---

## 6. Assumptions made (be upfront about these in interviews)

- SLA policy (7/30/90/180 days by severity) is a reasonable industry
  default, not a specific company's actual policy.
- Remediation tracking data (owners, statuses, close dates) is
  synthetically generated — the vulnerability findings and CVE data are
  real, the "who fixed it and when" layer is simulated because it would
  normally live in a ticketing system I don't have access to.
- The weighted Risk Score formula (10/5/2/1) is my own design choice,
  documented in `docs/design_decisions.md`.