import csv
import time
import requests

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

CVE_IDS = [
    "CVE-2021-44228",  # Log4Shell
    "CVE-2017-5638",   # Apache Struts RCE
    "CVE-2014-0160",   # Heartbleed
    "CVE-2019-0708",   # BlueKeep
    "CVE-2021-34527",  # PrintNightmare
]


def fetch_cve(cve_id):
    response = requests.get(NVD_URL, params={"cveId": cve_id}, timeout=15)
    response.raise_for_status()
    data = response.json()

    vuln = data["vulnerabilities"][0]["cve"]

    metrics = vuln.get("metrics", {})
    if "cvssMetricV31" in metrics:
        cvss_score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
    elif "cvssMetricV2" in metrics:
        cvss_score = metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]
    else:
        cvss_score = None

    description = next(
        (d["value"] for d in vuln["descriptions"] if d["lang"] == "en"),
        ""
    )

    return {
        "cve_id": vuln["id"],
        "cvss_score": cvss_score,
        "published_date": vuln["published"][:10],
        "description": description,
    }


rows = []
for cve_id in CVE_IDS:
    print(f"fetching {cve_id}...")
    rows.append(fetch_cve(cve_id))
    
    time.sleep(6)

with open("data/cve_enrichment.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote {len(rows)} CVE records to data/cve_enrichment.csv")