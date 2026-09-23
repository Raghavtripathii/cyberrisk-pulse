import csv
import random
from datetime import datetime, timedelta

SLA_DAYS = {
    "Critical": 7,
    "High": 30,
    "Medium": 90,
    "Low": 180,
}

OWNERS = ["Priya S.", "Arjun K.", "Dev Ops Team", "AppSec Team", "Raghvendra"]

random.seed(7)

with open("data/raw_findings.csv") as f:
    findings = list(csv.DictReader(f))

rows = []
for finding in findings:
    date_found = datetime.fromisoformat(finding["date_found"])
    sla_days = SLA_DAYS[finding["severity"]]
    sla_due_date = date_found + timedelta(days=sla_days)

    is_closed = random.random() < 0.7

    if is_closed:
        status = "Remediated"
        days_to_fix = random.randint(1, sla_days + 20)
        date_closed = (date_found + timedelta(days=days_to_fix)).date().isoformat()
    else:
        status = "Open"
        date_closed = ""

    rows.append({
        "finding_id": finding["finding_id"],
        "owner": random.choice(OWNERS),
        "status": status,
        "sla_due_date": sla_due_date.date().isoformat(),
        "date_closed": date_closed,
    })

with open("data/remediation_tracker.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote remediation tracking for {len(rows)} findings to data/remediation_tracker.csv")