import csv
from neo4j import GraphDatabase

with open("../data/city_distances_times_full.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)


print(f"Read {len(rows)} distance records")


URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "anish2006"


driver = GraphDatabase.driver(URI, auth=(USERNAME,PASSWORD))


with driver.session() as session:
    for i,row in enumerate(rows):
        distance = row.get("distance_km", "")
        duration = row.get("duration_min", "")

        if not distance and not duration:
            continue

        session.run("""
            MERGE (origin: City{name: $origin})
            MERGE (dest:City {name: $dest})
            MERGE (origin)-[d:DRIVING_DISTANCE]->(dest)
            SET d.distance_km = $distance,
                d.duration_min = $duration
        """,{
              "origin": row["origin"],
            "dest": row["destination"],
            "distance": distance,
            "duration": duration
        })

        if (i + 1) % 500 == 0:
            print(f"Loaded {i + 1} / {len(rows)}")

print("Done loading distances!")
driver.close()
