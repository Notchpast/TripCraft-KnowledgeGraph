import csv
from neo4j import GraphDatabase

# Step 1: Read CSV
with open("../data/cleaned_attractions_final.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Read {len(rows)} attractions")

# Step 2: Connect to Neo4j
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "anish2006"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Step 3: Load data into Neo4j
with driver.session() as session:
    for i, row in enumerate(rows):
        session.run("""
            MERGE (c:City {name: $city, state: $state})
            MERGE (a:Attraction {id: $id})
            SET a.name = $name,
                a.rating = $rating,
                a.latitude = $latitude,
                a.longitude = $longitude,
                a.visit_duration = $duration
            MERGE (c)-[:HAS_ATTRACTION]->(a)
        """, {
            "city": row["City"],
            "state": row["State"],
            "id": row["id"],
            "name": row["name"],
            "rating": row.get("rating", ""),
            "latitude": row.get("latitude", ""),
            "longitude": row.get("longitude", ""),
            "duration": row.get("visit_duration", "")
        })

        if (i + 1) % 500 == 0:
            print(f"Loaded {i + 1} / {len(rows)}")

print("Done loading attractions!")
driver.close()