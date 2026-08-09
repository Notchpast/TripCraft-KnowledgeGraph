import csv
from neo4j import GraphDatabase


with open("../data/cleaned_restaurant_details_2024.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)


print(f"Read {len(rows)} restaurants")


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "anish2006"

driver = GraphDatabase.driver(URI, auth=(USERNAME,PASSWORD))


with driver.session() as session:
    for i,row in enumerate(rows):

        session.run("""
            MERGE (c:City {name: $city, state: $state})
            MERGE (r: Restaurant {id : $id})
            SET r.name = $name,
                r.rating = $rating,
                r.latitude = $latitude,
                r.longitude = $longitude,
                r.cuisines = $cuisines,
                r.priceRange = $priceRange,
                r.avg_cost = $avg_cost
            MERGE (c)-[ :HAS_RESTAURANT]->(r)
        """, {
            "city": row.get("City",""),
            "state": row.get("State",""),
            "id": row["id"],
            "name": row.get("localName", ""),
            "rating": row.get("rating", ""),
            "latitude": row.get("latitude", ""),
            "longitude": row.get("longitude", ""),
            "cuisines": row.get("cuisines", ""),
            "priceRange": row.get("priceRange", ""),
            "avg_cost": row.get("avg_cost", "")
        })

        if (i + 1) % 500 == 0:
            print(f"Loaded {i + 1} / {len(rows)}")

print("Done loading restaurants!")
driver.close()
        