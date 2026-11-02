
import pandas as pd
import re

# --------------------------------------------------
# 1. Load the original Nodes CSV
# --------------------------------------------------

input_file = "data/AI_Literacy_Nodes.csv"
output_file = "data/AI_Literacy_Nodes_APA.csv"

nodes = pd.read_csv(input_file)

# --------------------------------------------------
# 2. Create an APA-style author name
# --------------------------------------------------

def get_surname(author):
    """Extract the last name from an author's full name."""

    parts = author.strip().split()

    if not parts:
        return ""

    return parts[-1]


# --------------------------------------------------
# 3. Create the author-date label
# --------------------------------------------------

def create_apa_label(row):

    authors = row["authors"]
    year = row["year"]
    title = row["title"]

    # Handle missing publication years
    if pd.isna(year):
        year_text = "n.d."
    else:
        year_text = str(int(float(year)))

    # Handle missing author information
    if pd.isna(authors) or str(authors).strip() == "":
        short_title = str(title)[:45].strip()
        return f'"{short_title}", {year_text}'

    # Split author names using semicolons
    author_list = [
        name.strip()
        for name in str(authors).split(";")
        if name.strip()
    ]

    surnames = [get_surname(name) for name in author_list]

    # One author
    if len(surnames) == 1:
        author_text = surnames[0]

    # Two authors
    elif len(surnames) == 2:
        author_text = f"{surnames[0]} & {surnames[1]}"

    # Three or more authors
    else:
        author_text = f"{surnames[0]} et al."

    return f"{author_text}, {year_text}"


# --------------------------------------------------
# 4. Add the Label column
# --------------------------------------------------

nodes["Label"] = nodes.apply(create_apa_label, axis=1)

# --------------------------------------------------
# 5. Save as a NEW CSV
# --------------------------------------------------

nodes.to_csv(output_file, index=False, encoding="utf-8-sig")

print("APA labels created successfully!")
print(f"Saved to: {output_file}")

print("\nExample labels:")
print(nodes[["title", "Label"]].head(10).to_string(index=False))

