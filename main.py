
import pandas as pd

nodes = pd.read_csv("data/AI_Literacy_Nodes.csv")
edges = pd.read_csv("data/AI_Literacy_Edges.csv")

# Find self-referencing edges
self_loops = edges[
    edges["source"] == edges["target"]
]

print("SELF-REFERENCING ARTICLES")
print("----------------------------")

for _, edge in self_loops.iterrows():

    article = nodes[nodes["id"] == edge["source"]]

    if not article.empty:
        print("Article:", article.iloc[0]["title"])
        print("OpenAlex ID:", edge["source"])

# Create two separate edge datasets

# 1. All citation relationships
edges.to_csv(
    "data/Gephi_Expanded_Edges.csv",
    index=False
)

# 2. Only relationships within original collection
original_edges = edges[
    (edges["source_type"] == "Original Collection") &
    (edges["target_type"] == "Original Collection")
]

original_edges.to_csv(
    "data/Gephi_Original_Collection_Edges.csv",
    index=False
)

print("\nOriginal collection edges:", len(original_edges))
print("Expanded network edges:", len(edges))


# Prepare nodes for Gephi

gephi_nodes = nodes.rename(columns={
    "id": "Id",
    "title": "Label"
})

gephi_nodes.to_csv(
    "data/Gephi_Nodes.csv",
    index=False
)

print("Gephi node file created!")
print("Total nodes:", len(gephi_nodes))
