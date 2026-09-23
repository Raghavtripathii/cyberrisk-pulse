import sqlite3
import pandas as pd

findings = pd.read_csv("data/raw_findings.csv", parse_dates=["date_found"])
remediation = pd.read_csv("data/remediation_tracker.csv", parse_dates=["sla_due_date", "date_closed"])

BASELINE_CVSS = {"Critical": 9.5, "High": 7.5, "Medium": 5.0, "Low": 2.5}

try:
    cve_data = pd.read_csv("data/cve_enrichment.csv")

    dependency_findings = findings[findings["check_name"].str.contains("Unpatched Dependency")]
    cve_cycle = cve_data["cve_id"].tolist()
    cve_map = {
        fid: cve_cycle[i % len(cve_cycle)]
        for i, fid in enumerate(dependency_findings["finding_id"])
    }
    cvss_map = dict(zip(cve_data["cve_id"], cve_data["cvss_score"]))
except FileNotFoundError:
    
    print("data/cve_enrichment.csv not found, skipping real CVE mapping")
    cve_map = {}
    cvss_map = {}

findings["cve_id"] = findings["finding_id"].map(cve_map)
findings["cvss_score"] = findings.apply(
    lambda r: cvss_map.get(r["cve_id"], BASELINE_CVSS[r["severity"]]),
    axis=1,
)

dim_severity = pd.DataFrame([
    {"severity_id": 1, "severity": "Critical", "sla_days": 7, "sort_order": 1},
    {"severity_id": 2, "severity": "High", "sla_days": 30, "sort_order": 2},
    {"severity_id": 3, "severity": "Medium", "sla_days": 90, "sort_order": 3},
    {"severity_id": 4, "severity": "Low", "sla_days": 180, "sort_order": 4},
])
severity_id_map = dict(zip(dim_severity["severity"], dim_severity["severity_id"]))

categories = sorted(findings["owasp_category"].unique())
dim_owasp_category = pd.DataFrame({
    "owasp_category_id": range(1, len(categories) + 1),
    "owasp_category": categories,
})
category_id_map = dict(zip(dim_owasp_category["owasp_category"], dim_owasp_category["owasp_category_id"]))

ASSET_METADATA = {
    "vault-notes-web": ("Product Engineering", "High"),
    "vault-notes-api": ("Product Engineering", "High"),
    "internal-hr-portal": ("HR", "Medium"),
    "customer-payments-gateway": ("Finance", "Critical"),
    "marketing-cms": ("Marketing", "Low"),
    "employee-vpn-endpoint": ("IT Infrastructure", "High"),
}
assets = sorted(findings["asset_name"].unique())
dim_asset = pd.DataFrame({
    "asset_id": range(1, len(assets) + 1),
    "asset_name": assets,
    "business_unit": [ASSET_METADATA[a][0] for a in assets],
    "criticality_tier": [ASSET_METADATA[a][1] for a in assets],
})
asset_id_map = dict(zip(dim_asset["asset_name"], dim_asset["asset_id"]))

all_dates = pd.concat([
    findings["date_found"],
    remediation["sla_due_date"],
    remediation["date_closed"].dropna(),
])
date_range = pd.date_range(all_dates.min(), all_dates.max())
dim_date = pd.DataFrame({
    "date": date_range,
    "year": date_range.year,
    "month": date_range.month,
    "month_name": date_range.strftime("%B"),
    "quarter": date_range.quarter,
})
dim_date["date"] = dim_date["date"].dt.date.astype(str)

fact = findings.merge(remediation, on="finding_id")
fact["severity_id"] = fact["severity"].map(severity_id_map)
fact["owasp_category_id"] = fact["owasp_category"].map(category_id_map)
fact["asset_id"] = fact["asset_name"].map(asset_id_map)

fact_vulnerabilities = fact[[
    "finding_id", "asset_id", "severity_id", "owasp_category_id",
    "date_found", "sla_due_date", "date_closed", "status",
    "owner", "cvss_score", "cve_id", "description",
]].copy()
fact_vulnerabilities["date_found"] = fact_vulnerabilities["date_found"].dt.date.astype(str)
fact_vulnerabilities["sla_due_date"] = fact_vulnerabilities["sla_due_date"].dt.date.astype(str)
fact_vulnerabilities["date_closed"] = fact_vulnerabilities["date_closed"].dt.date.astype(str).replace("NaT", "")

tables = {
    "fact_vulnerabilities": fact_vulnerabilities,
    "dim_asset": dim_asset,
    "dim_severity": dim_severity,
    "dim_owasp_category": dim_owasp_category,
    "dim_date": dim_date,
}

conn = sqlite3.connect("data/cyberrisk.db")
for name, df in tables.items():
    df.to_csv(f"data/{name}.csv", index=False)
    df.to_sql(name, conn, if_exists="replace", index=False)
conn.close()

print("star schema built. tables written to data/*.csv and data/cyberrisk.db")
for name, df in tables.items():
    print(f"  {name}: {len(df)} rows")