
import json
import pandas as pd
from pathlib import Path

# -----------------------------------------
# 1. Load the original OpenAlex records
# -----------------------------------------

with open("data/original_articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

if isinstance(data, list):
    records = data
elif isinstance(data, dict) and isinstance(data.get("results"), list):
    records = data["results"]
elif isinstance(data, dict) and isinstance(data.get("data"), list):
    records = data["data"]
elif isinstance(data, dict) and "id" in data:
    records = [data]
else:
    raise ValueError("Unexpected JSON structure.")

# -----------------------------------------
# 2. Extract publication information
# -----------------------------------------

rows = []

for record in records:

    pub_type = record.get("type") or "Unknown"

    year = record.get("publication_year") or "Unknown"

    references = record.get("referenced_works") or []

    rows.append({
        "id": record.get("id", "").split("/")[-1],
        "title": record.get("title") or "Missing title",
        "year": year,
        "work_type": pub_type,
        "reference_count": len(references),
        "has_references": len(references) > 0
    })

df = pd.DataFrame(rows)

# -----------------------------------------
# 3. Summarize by publication type
# -----------------------------------------

by_type = (
    df.groupby("work_type")
    .agg(
        total_publications=("id", "count"),
        with_references=("has_references", "sum"),
        average_references=("reference_count", "mean")
    )
    .reset_index()
)

by_type["without_references"] = (
    by_type["total_publications"] -
    by_type["with_references"]
)

by_type["percent_with_references"] = (
    by_type["with_references"] /
    by_type["total_publications"] * 100
).round(1)

# -----------------------------------------
# 4. Summarize by publication year
# -----------------------------------------

by_year = (
    df.groupby("year")
    .agg(
        total_publications=("id", "count"),
        with_references=("has_references", "sum"),
        average_references=("reference_count", "mean")
    )
    .reset_index()
)

by_year["without_references"] = (
    by_year["total_publications"] -
    by_year["with_references"]
)

by_year["percent_with_references"] = (
    by_year["with_references"] /
    by_year["total_publications"] * 100
).round(1)

# -----------------------------------------
# 5. Display results
# -----------------------------------------

print("\n===== REFERENCE AVAILABILITY BY TYPE =====")
print(by_type.to_string(index=False))

print("\n===== REFERENCE AVAILABILITY BY YEAR =====")
print(by_year.to_string(index=False))

# -----------------------------------------
# 6. Export reports
# -----------------------------------------

by_type.to_csv(
    "data/reference_availability_by_type.csv",
    index=False
)

by_year.to_csv(
    "data/reference_availability_by_year.csv",
    index=False
)

df.to_csv(
    "data/reference_availability_detail.csv",
    index=False
)

print("\nThree reports saved in your data folder.")
