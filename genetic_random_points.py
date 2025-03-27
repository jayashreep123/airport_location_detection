import numpy as np
import psycopg2
import random
from geopy.distance import geodesic

# Database Connection
DB_PARAMS = {
    "dbname": "airline_db",
    "user": "postgres",
    "password": "Jaya2005",
    "host": "localhost",
    "port": "5432"
}

# Connect to DB
conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

# Fetch Airports
cursor.execute("SELECT id, name, latitude, longitude FROM airports")
airports = cursor.fetchall()

# Fetch Population Centers
cursor.execute("SELECT city, state, population, latitude, longitude FROM population_data WHERE population > 1500")
population_centers = cursor.fetchall()

# PSO Parameters
NUM_PARTICLES = 10  # Reduced for faster execution
ITERATIONS = 10  # Lowered for quick completion

# Function to find nearest airport
def find_nearest_airport(point):
    lat, lon = point
    nearest_airport = min(airports, key=lambda air: geodesic((lat, lon), (air[2], air[3])).km)
    distance = geodesic((lat, lon), (nearest_airport[2], nearest_airport[3])).km
    return nearest_airport, distance

# Function to find nearest population center
def find_nearest_city(point):
    lat, lon = point
    nearest_city = min(population_centers, key=lambda pop: geodesic((lat, lon), (pop[3], pop[4])).km)
    distance = geodesic((lat, lon), (nearest_city[3], nearest_city[4])).km
    return nearest_city, distance

# Fitness function
def fitness(point):
    nearest_airport, airport_distance = find_nearest_airport(point)
    nearest_city, city_distance = find_nearest_city(point)
    
    if airport_distance > 500:
        return 0  # Invalid if too far from airport
    
    return (1000 - airport_distance) + (nearest_city[2] / 100)

# Particle Swarm Optimization (PSO)
def pso():
    particles = [(random.uniform(25, 50), random.uniform(-125, -65)) for _ in range(NUM_PARTICLES)]  # Generate initial random points
    best_positions = particles[:]
    best_scores = [fitness(p) for p in particles]

    for iteration in range(ITERATIONS):
        print(f"Iteration {iteration}: Running optimization...")

        for i in range(NUM_PARTICLES):
            new_lat = particles[i][0] + random.uniform(-0.5, 0.5)
            new_lon = particles[i][1] + random.uniform(-0.5, 0.5)
            new_point = (new_lat, new_lon)
            new_score = fitness(new_point)

            if new_score > best_scores[i]:
                best_positions[i] = new_point
                best_scores[i] = new_score

        particles = best_positions[:]

    return best_positions

# Run PSO and Validate Points
valid_points = []
for point in pso():
    nearest_airport, airport_distance = find_nearest_airport(point)
    nearest_city, city_distance = find_nearest_city(point)

    is_valid = airport_distance <= 500
    valid_points.append((point[0], point[1], is_valid, nearest_city[0], nearest_airport[1], airport_distance))

# Store results in DB
for lat, lon, is_valid, nearest_city, nearest_airport, airport_distance in valid_points:
    cursor.execute("""
        INSERT INTO random_points (latitude, longitude, is_valid, nearest_city, nearest_airport, airport_distance_km)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (lat, lon, is_valid, nearest_city, nearest_airport, airport_distance))

conn.commit()
cursor.close()
conn.close()

print("✅ Random Points Generated, Validated, and Stored Successfully!")
