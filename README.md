# TripCraft Knowledge Graph

A knowledge graph for travel planning built with **Neo4j** and **Python**. This project transforms raw travel datasets (attractions, restaurants, flights, city distances) into an interconnected graph database, enabling complex multi-entity queries that would be difficult to achieve with traditional relational databases.

## What is a Knowledge Graph?

A knowledge graph organizes information as **nodes** (entities) connected by **relationships** (edges), rather than flat tables. This lets you ask questions like "Find cities reachable from Denver under $100 that also have highly-rated Italian restaurants" by simply traversing the graph, instead of writing complex multi-table SQL joins.

## Architecture

```
CSV Data Files
     │
     ▼
Python Ingestion Scripts (csv + neo4j driver)
     │
     ▼
Neo4j Graph Database
     │
     ▼
Flask REST API
     │
     ▼
JSON Responses
```

## Graph Schema

**Node Types:**
| Node | Properties | Count |
|------|-----------|-------|
| City | name, state | 313 |
| Attraction | name, rating, latitude, longitude, visit_duration | 5,038 |
| Restaurant | name, rating, cuisines, priceRange, avg_cost, latitude, longitude | 3,867 |
| Flight | flight_number, price, dep_time, arr_time, distance | 10,000 |

**Relationship Types:**
| Relationship | From | To | Description |
|-------------|------|-----|-------------|
| HAS_ATTRACTION | City | Attraction | City contains this attraction |
| HAS_RESTAURANT | City | Restaurant | City contains this restaurant |
| HAS_FLIGHT | City | Flight | Flight departs from this city |
| FLIES_TO | Flight | City | Flight arrives at this city |
| DRIVING_DISTANCE | City | City | Driving distance and time between cities |

## Setup

### Prerequisites
- Python 3.12+
- Neo4j Desktop (Community Edition)

### Installation

```bash
pip install neo4j flask
```

1. Install and start Neo4j Desktop
2. Create a new database instance
3. Update the password in the scripts

### Load Data

Run the scripts in this order from the `scripts/` directory:

```bash
python load_attractions.py
python load_restaurants.py
python load_flights.py
python load_distances.py
```

### Start the API

```bash
python api.py
```

The server runs at `http://127.0.0.1:5000`

## API Endpoints

| Endpoint | Description | Example |
|----------|------------|---------|
| `/attractions/<city>` | Top 10 attractions in a city | `/attractions/San Diego` |
| `/restaurants/<city>` | Top 10 restaurants in a city | `/restaurants/Houston` |
| `/flights/<origin>/<dest>` | Cheapest flights between cities | `/flights/Denver/Houston` |
| `/plan/<city>` | Trip overview with attractions + restaurants | `/plan/San Diego` |

### Sample Response: `/plan/San Diego`

```json
{
  "city": "San Diego",
  "top_attractions": [
    {"name": "USS Midway Museum", "rating": "5"},
    {"name": "La Jolla Cove", "rating": "4.5"},
    {"name": "Balboa Park", "rating": "4.5"}
  ],
  "top_restaurants": [
    {"name": "Covewood Restaurant", "rating": "5.0", "cuisines": "['American', 'Healthy']"},
    {"name": "Cowboy Star", "rating": "4.5", "cuisines": "['American', 'Steakhouse']"}
  ]
}
```

## Sample Cypher Queries

**Cities reachable from Denver under $100:**
```cypher
MATCH (denver:City {name: "Denver"})-[:HAS_FLIGHT]->(f:Flight)-[:FLIES_TO]->(dest:City)
WHERE toInteger(f.price) < 100
RETURN DISTINCT dest.name, min(toInteger(f.price)) AS cheapest
ORDER BY cheapest
```

**Cities with direct flights from Denver AND good restaurants:**
```cypher
MATCH (denver:City {name: "Denver"})-[:HAS_FLIGHT]->(f:Flight)-[:FLIES_TO]->(dest:City)
MATCH (dest)-[:HAS_RESTAURANT]->(r:Restaurant)
WHERE toFloat(r.rating) > 4.0
RETURN dest.name, count(DISTINCT r) AS good_restaurants, min(f.price) AS cheapest_flight
ORDER BY good_restaurants DESC
LIMIT 10
```

## Tech Stack

- **Python** - Data ingestion and API
- **Neo4j** - Graph database
- **Cypher** - Graph query language
- **Flask** - REST API framework

## Dataset

Based on the TripCraft travel planning dataset covering 313 US cities with data on attractions, restaurants, flights, and intercity distances.

## License

MIT License
