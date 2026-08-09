import csv
from neo4j import GraphDatabase

# Step 1: Read CSV
with open("../data/cleaned_flights_november_2024.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Read {len(rows)} flights")

# Step 2: Connect
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "anish2006"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Step 3: Load (only first 10000 for prototype)
with driver.session() as session:
    for i, row in enumerate(rows):
        if i >= 10000:
            break

        session.run("""
            MERGE (origin:City {name: $origin_city})
            MERGE (dest:City {name: $dest_city})
            CREATE (f:Flight {
                flight_number: $flight_number,
                price: $price,
                dep_time: $dep_time,
                arr_time: $arr_time,
                distance: $distance
            })
            CREATE (origin)-[:HAS_FLIGHT]->(f)
            CREATE (f)-[:FLIES_TO]->(dest)
        """, {
            "origin_city": row["OriginCityName"],
            "dest_city": row["DestCityName"],
            "flight_number": row["Flight Number"],
            "price": row["Price"],
            "dep_time": row["DepTime"],
            "arr_time": row["ArrTime"],
            "distance": row.get("Distance", "")
        })

        if (i + 1) % 1000 == 0:
            print(f"Loaded {i + 1} / 10000")

print("Done loading flights!")
driver.close()