# Data Dictionary

## fact_vulnerabilities
One row = one vulnerability finding.

| Column | Type | Meaning |
|---|---|---|
| finding_id | integer | unique ID for the finding |
| asset_id | integer | links to dim_asset |
| severity_id | integer | links to dim_severity |
| owasp_category_id | integer | links to dim_owasp_category |
| date_found | date | when the scan found this |
| sla_due_date | date | when it's supposed to be fixed by, based on severity |
| date_closed | date | when it was actually fixed (blank if still open) |
| status | text | "Open" or "Remediated" |
| owner | text | who's responsible for fixing it |
| cvss_score | number | severity score, 0-10 (real CVE score if one applies, otherwise a baseline for that severity) |
| cve_id | text | real CVE reference, only filled in for findings tied to a known dependency vulnerability |
| description | text | what the finding actually is |

## dim_asset
| Column | Meaning |
|---|---|
| asset_id | unique ID |
| asset_name | system/app name |
| business_unit | which part of the org owns it |
| criticality_tier | how important this asset is to the business (Low/Medium/High/Critical) |

## dim_severity
| Column | Meaning |
|---|---|
| severity_id | unique ID |
| severity | Critical / High / Medium / Low |
| sla_days | how many days this severity is allowed before it's overdue |
| sort_order | forces charts to sort Critical -> Low instead of alphabetically |

## dim_owasp_category
| Column | Meaning |
|---|---|
| owasp_category_id | unique ID |
| owasp_category | which OWASP Top 10-style category this finding falls under |

## dim_date
Standard date table, one row per calendar day covering the span of the data.
| Column | Meaning |
|---|---|
| date | ISO date, primary key |
| year / month / month_name / quarter | standard date parts for grouping charts |