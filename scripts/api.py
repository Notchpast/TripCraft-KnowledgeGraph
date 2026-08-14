import os
from pathlib import Path
from flask import Flask, jsonify, request
from neo4j import GraphDatabase
from google import genai
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

@app.route("/attractions/<city>")
def get_attractions(city):
    with driver.session() as session:
        result = session.run("""
            MATCH (c:City {name: $city})-[:HAS_ATTRACTION]->(a:Attraction)
            RETURN a.name AS name, a.rating AS rating
            ORDER BY a.rating DESC
            LIMIT 10
        """, {"city": city})
        attractions = [dict(record) for record in result]
    return jsonify(attractions)


@app.route("/restaurants/<city>")
def get_restaurants(city):
    with driver.session() as session:
        result = session.run("""
            MATCH (c:City {name: $city})-[:HAS_RESTAURANT]->(r:Restaurant)
            RETURN r.name AS name, r.rating AS rating, r.cuisines AS cuisines
            ORDER BY r.rating DESC
            LIMIT 10
        """, {"city": city})
        restaurants = [dict(record) for record in result]
    return jsonify(restaurants)


@app.route("/flights/<origin>/<destination>")
def get_flights(origin, destination):
    with driver.session() as session:
        result = session.run("""
            MATCH (o:City {name: $origin})-[:HAS_FLIGHT]->(f:Flight)-[:FLIES_TO]->(d:City {name: $destination})
            RETURN f.flight_number AS flight, f.price AS price, f.dep_time AS departure
            ORDER BY toInteger(f.price)
            LIMIT 10
        """, {"origin": origin, "destination": destination})
        flights = [dict(record) for record in result]
    return jsonify(flights)


@app.route("/plan/<city>")
def plan_trip(city):
    with driver.session() as session:
        attractions = session.run("""
            MATCH (c:City {name: $city})-[:HAS_ATTRACTION]->(a:Attraction)
            RETURN a.name AS name, a.rating AS rating
            ORDER BY a.rating DESC LIMIT 5
        """, {"city": city})

        restaurants = session.run("""
            MATCH (c:City {name: $city})-[:HAS_RESTAURANT]->(r:Restaurant)
            RETURN r.name AS name, r.rating AS rating, r.cuisines AS cuisines
            ORDER BY r.rating DESC LIMIT 5
        """, {"city": city})

        return jsonify({
            "city": city,
            "top_attractions": [dict(r) for r in attractions],
            "top_restaurants": [dict(r) for r in restaurants]
        })


@app.route("/ai-plan/<city>")
def ai_plan(city):
    # STEP 1: RETRIEVAL — pull real data from the knowledge graph
    with driver.session() as session:
        attractions = session.run("""
            MATCH (c:City {name: $city})-[:HAS_ATTRACTION]->(a:Attraction)
            RETURN a.name AS name, a.rating AS rating, a.visit_duration AS duration
            ORDER BY a.rating DESC LIMIT 8
        """, {"city": city})
        attraction_list = [dict(r) for r in attractions]

        restaurants = session.run("""
            MATCH (c:City {name: $city})-[:HAS_RESTAURANT]->(r:Restaurant)
            RETURN r.name AS name, r.rating AS rating, r.cuisines AS cuisines, r.avg_cost AS cost
            ORDER BY r.rating DESC LIMIT 8
        """, {"city": city})
        restaurant_list = [dict(r) for r in restaurants]

    if not attraction_list and not restaurant_list:
        return jsonify({"error": f"No data found for {city}"}), 404

    # STEP 2: AUGMENTATION — build a prompt with the retrieved data
    prompt = f"""You are a travel planner. Create a 2-day itinerary for {city}.

IMPORTANT: Use ONLY the attractions and restaurants listed below. Do not invent any places.

ATTRACTIONS AVAILABLE:
{attraction_list}

RESTAURANTS AVAILABLE:
{restaurant_list}

Create a day-by-day plan. For each day, suggest 2-3 attractions and 2 meals.
Consider visit durations when scheduling. Keep it concise and practical."""

    # STEP 3: GENERATION — let the LLM write the itinerary
    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return jsonify({
        "city": city,
        "itinerary": response.text,
        "data_source": {
            "attractions_used": len(attraction_list),
            "restaurants_used": len(restaurant_list)
        }
    })

if __name__ == "__main__":
    app.run(debug=True)