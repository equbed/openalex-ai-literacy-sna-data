
import csv
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import quote

# -----------------------------------------
# 1. File locations
# -----------------------------------------

data_folder = Path("data")

audit_file = data_folder / "reference_audit.csv"

if not audit_file.exists():
    raise FileNotFoundError("reference_audit.csv not found.")

# -----------------------------------------
# 2. Identify the 209 missing records
# -----------------------------------------

with open(audit_file, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    missing_records = [
        row for row in reader
        if row["has_references"].lower() == "false"
    ]

print("Records to investigate:", len(missing_records))

# -----------------------------------------
# 3. Retrieve updated OpenAlex records
# -----------------------------------------

retrieved_records = []
errors = []

fields = (
    "id,title,publication_year,type,"
    "referenced_works,referenced_works_count,"
    "cited_by_count,doi"
)

for number, row in enumerate(missing_records, start=1):

    work_id = row["id"]

    url = (
        f"https://api.openalex.org/works/{quote(work_id)}"
        f"?select={fields}"
    )

    print(f"Checking {number}/{len(missing_records)}: {work_id}")

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "AILiteracyCitationAudit/1.0"}
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            record = json.loads(response.read().decode("utf-8"))

        references = record.get("referenced_works") or []

        retrieved_records.append(record)

        print("   References found:", len(references))

    except urllib.error.HTTPError as error:
        print("   HTTP error:", error.code)

        errors.append({
            "id": work_id,
            "error": f"HTTP {error.code}"
        })

    except Exception as error:
        print("   Error:", str(error))

        errors.append({
            "id": work_id,
            "error": str(error)
        })

    # Be gentle with the API
    time.sleep(0.2)

# -----------------------------------------
# 4. Summarize results
# -----------------------------------------

with_references = sum(
    len(record.get("referenced_works") or []) > 0
    for record in retrieved_records
)

without_references = len(retrieved_records) - with_references

print("\n========== RETRIEVAL RESULTS ==========")
print("Records requested:", len(missing_records))
print("Records retrieved:", len(retrieved_records))
print("Records with references:", with_references)
print("Records still without references:", without_references)
print("Retrieval errors:", len(errors))
print("======================================")

# -----------------------------------------
# 5. Save updated OpenAlex records
# -----------------------------------------

json_output = data_folder / "retrieved_missing_records.json"

with open(json_output, "w", encoding="utf-8") as f:
    json.dump(retrieved_records, f, indent=2)

# -----------------------------------------
# 6. Save a detailed comparison report
# -----------------------------------------

report_output = data_folder / "retrieved_reference_report.csv"

with open(report_output, "w", encoding="utf-8", newline="") as f:

    fieldnames = [
        "id",
        "title",
        "year",
        "type",
        "reference_count",
        "cited_by_count"
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for record in retrieved_records:
        writer.writerow({
            "id": record.get("id", "").split("/")[-1],
            "title": record.get("title"),
            "year": record.get("publication_year"),
            "type": record.get("type"),
            "reference_count": len(
                record.get("referenced_works") or []
            ),
            "cited_by_count": record.get("cited_by_count")
        })

# -----------------------------------------
# 7. Save any errors separately
# -----------------------------------------

with open(
    data_folder / "retrieval_errors.csv",
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=["id", "error"]
    )

    writer.writeheader()
    writer.writerows(errors)

print("\nFiles saved:")
print(json_output)
print(report_output)
print(data_folder / "retrieval_errors.csv")
