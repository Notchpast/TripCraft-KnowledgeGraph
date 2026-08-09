from flask import Flask, jsonify, request
from neo4j import GraphDatabase

app = Flask(__name__)

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "anish2006"
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


if __name__ == "__main__":
    app.run(debug=True)