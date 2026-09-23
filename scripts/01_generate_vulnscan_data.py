import csv
import random
from datetime import date, timedelta

CHECKS = [
    ("SQL Injection", "Critical", "Injection"),
    ("Reflected XSS", "High", "Injection"),
    ("Missing Security Headers", "Low", "Security Misconfiguration"),
    ("Outdated TLS Version", "Medium", "Cryptographic Failures"),
    ("Broken Access Control on /admin", "Critical", "Broken Access Control"),
    ("Hardcoded API Key in Source", "High", "Cryptographic Failures"),
    ("Verbose Error Messages", "Low", "Security Misconfiguration"),
    ("Weak Password Policy", "Medium", "Identification and Authentication Failures"),
    ("Directory Listing Enabled", "Low", "Security Misconfiguration"),
    ("Unpatched Dependency (known CVE)", "High", "Vulnerable and Outdated Components"),
    ("CSRF on Password Change", "Medium", "Broken Access Control"),
    ("Session Token Not Invalidated on Logout", "Medium", "Identification and Authentication Failures"),
]

ASSETS = [
    ("vault-notes-web", "production"),
    ("vault-notes-api", "production"),
    ("internal-hr-portal", "staging"),
    ("customer-payments-gateway", "production"),
    ("marketing-cms", "production"),
    ("employee-vpn-endpoint", "production"),
]

random.seed(42)

rows = []
finding_id = 1000
start = date(2025, 1, 1)

for asset_name, environment in ASSETS:
    picked_checks = random.sample(CHECKS, k=random.randint(4, 8))
    for check_name, severity, owasp_category in picked_checks:
        finding_id += 1
        days_offset = random.randint(0, 240)
        date_found = start + timedelta(days=days_offset)
        rows.append({
            "finding_id": finding_id,
            "asset_name": asset_name,
            "environment": environment,
            "check_name": check_name,
            "severity": severity,
            "owasp_category": owasp_category,
            "description": f"{check_name} identified during automated scan of {asset_name}.",
            "date_found": date_found.isoformat(),
        })

with open("data/raw_findings.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote {len(rows)} findings to data/raw_findings.csv")