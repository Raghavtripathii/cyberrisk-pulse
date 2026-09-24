
CREATE TABLE dim_severity (
    severity_id  INTEGER PRIMARY KEY,
    severity     TEXT NOT NULL,      -- Critical / High / Medium / Low
    sla_days     INTEGER NOT NULL,   -- how many days this severity gets before it's overdue
    sort_order   INTEGER NOT NULL    -- so charts sort Critical -> Low, not alphabetically
);

CREATE TABLE dim_owasp_category (
    owasp_category_id  INTEGER PRIMARY KEY,
    owasp_category      TEXT NOT NULL
);

CREATE TABLE dim_asset (
    asset_id          INTEGER PRIMARY KEY,
    asset_name        TEXT NOT NULL,
    business_unit     TEXT NOT NULL,
    criticality_tier  TEXT NOT NULL   -- how important this asset is to the business
);

CREATE TABLE dim_date (
    date        TEXT PRIMARY KEY,    -- ISO format YYYY-MM-DD
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    month_name  TEXT NOT NULL,
    quarter     INTEGER NOT NULL
);

CREATE TABLE fact_vulnerabilities (
    finding_id          INTEGER PRIMARY KEY,
    asset_id            INTEGER NOT NULL REFERENCES dim_asset(asset_id),
    severity_id         INTEGER NOT NULL REFERENCES dim_severity(severity_id),
    owasp_category_id   INTEGER NOT NULL REFERENCES dim_owasp_category(owasp_category_id),
    date_found          TEXT NOT NULL REFERENCES dim_date(date),
    sla_due_date         TEXT NOT NULL REFERENCES dim_date(date),
    date_closed         TEXT REFERENCES dim_date(date),   -- empty until the finding is remediated
    status               TEXT NOT NULL,   -- Open / Remediated
    owner                TEXT NOT NULL,
    cvss_score           REAL,
    cve_id               TEXT,            -- filled in only when a real CVE applies
    description           TEXT
);