
import json
import csv
from pathlib import Path

# --------------------------------------------------
# 1. Locate the original OpenAlex data
# --------------------------------------------------

data_folder = Path("data")
json_file = data_folder / "original_articles.json"

if not json_file.exists():
    raise FileNotFoundError(
        "Cannot find data/original_articles.json. "
        "Check that you opened the correct Codespace."
    )

# Load the original OpenAlex records
with open(json_file, "r", encoding="utf-8") as file:
    raw_data = json.load(file)

# OpenAlex data may be stored as a list or
# inside a dictionary under 'results' or 'data'.
if isinstance(raw_data, list):
    records = raw_data
elif isinstance(raw_data, dict) and isinstance(raw_data.get("results"), list):
    records = raw_data["results"]
elif isinstance(raw_data, dict) and isinstance(raw_data.get("data"), list):
    records = raw_data["data"]
elif isinstance(raw_data, dict) and "id" in raw_data:
    records = [raw_data]
else:
    raise ValueError(
        "Could not identify the OpenAlex records in the JSON file."
    )

print("Original OpenAlex records found:", len(records))


# --------------------------------------------------
# 2. Prepare a function to standardize OpenAlex IDs
# --------------------------------------------------

def clean_id(value):
    if not value:
        return ""

    return str(value).rstrip("/").split("/")[-1]


# --------------------------------------------------
# 3. Check each publication's reference list
# --------------------------------------------------

audit_results = []

for record in records:

    article_id = clean_id(record.get("id"))
    title = record.get("title") or "Missing title"

    references = record.get("referenced_works") or []

    audit_results.append({
        "id": article_id,
        "title": title,
        "reference_count": len(references),
        "has_references": len(references) > 0
    })


# --------------------------------------------------
# 4. Compare against the existing citation edges
# --------------------------------------------------

edge_file = data_folder / "AI_Literacy_Edges.csv"

if not edge_file.exists():
    raise FileNotFoundError(
        "Cannot find data/AI_Literacy_Edges.csv."
    )

with open(edge_file, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    edge_sources = {
        clean_id(row["source"])
        for row in reader
        if row.get("source")
    }

for article in audit_results:
    article["appears_in_edges"] = (
        article["id"] in edge_sources
    )


# --------------------------------------------------
# 5. Calculate summary statistics
# --------------------------------------------------

total = len(audit_results)

with_references = sum(
    article["has_references"] for article in audit_results
)

without_references = total - with_references

with_edges = sum(
    article["appears_in_edges"] for article in audit_results
)

has_references_but_no_edges = sum(
    article["has_references"] and not article["appears_in_edges"]
    for article in audit_results
)

no_references_but_has_edges = sum(
    not article["has_references"] and article["appears_in_edges"]
    for article in audit_results
)

print("\n========== REFERENCE AUDIT ==========")
print("Total original publications:", total)
print("Publications with references:", with_references)
print("Publications without references:", without_references)
print("Publications appearing as edge sources:", with_edges)
print("Have references but missing from edges:", has_references_but_no_edges)
print("Have no references but appear in edges:", no_references_but_has_edges)


# --------------------------------------------------
# 6. Save the detailed audit report
# --------------------------------------------------

output_file = data_folder / "reference_audit.csv"

with open(output_file, "w", encoding="utf-8", newline="") as file:
    fieldnames = [
        "id",
        "title",
        "reference_count",
        "has_references",
        "appears_in_edges"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(audit_results)

print("\nAudit report saved to:", output_file)
print("====================================")
