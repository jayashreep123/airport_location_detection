import psycopg2
import numpy as np
from geopy.distance import geodesic

# ✅ Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="airline_db",
    user="postgres",
    password="Jaya2005",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# ✅ Fetch all random points
cursor.execute("SELECT id, latitude, longitude, nearest_city FROM random_points;")
random_points = cursor.fetchall()

# ✅ Fetch all airports
cursor.execute("SELECT id, name, latitude, longitude FROM airports;")
airports = cursor.fetchall()

if not random_points or not airports:
    print("❌ No data found in random_points or airports table!")
    conn.close()
    exit()

# ✅ Function to calculate distance
def find_nearest_airport(city_point):
    city_id, city_lat, city_lon, city_name = city_point
    nearest_airport = None
    min_distance = float('inf')

    for airport in airports:
        airport_id, airport_name, airport_lat, airport_lon = airport
        distance = geodesic((city_lat, city_lon), (airport_lat, airport_lon)).km
        if distance < min_distance:
            min_distance = distance
            nearest_airport = (airport_id, airport_name, min_distance)

    return city_id, city_name, nearest_airport

# ✅ Estimate CO₂ emissions (150g/km = 0.024 metric tons per mile)
def calculate_co2_emission(distance_km):
    return round(distance_km * 0.024, 4)

# ✅ Find multiple best cities
best_cities = []
for city in random_points:
    city_id, city_name, nearest_airport = find_nearest_airport(city)
    if nearest_airport and nearest_airport[2] <= 500:  # Only consider cities within 500 km
        co2_emission = calculate_co2_emission(nearest_airport[2])
        best_cities.append((city_id, city_name, nearest_airport[1], nearest_airport[2], co2_emission))

# ✅ Sort by lowest distance and highest priority
best_cities = sorted(best_cities, key=lambda x: (x[3], -x[4]))[:10]  # Take Top 10

# ✅ Create Table if Not Exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS best_airline_cities (
        id SERIAL PRIMARY KEY,
        city TEXT,
        nearest_airport TEXT,
        distance_km FLOAT,
        co2_emission FLOAT
    );
""")

# ✅ Insert multiple best cities into the database
for city in best_cities:
    cursor.execute("""
        INSERT INTO best_airline_cities (city, nearest_airport, distance_km, co2_emission)
        VALUES (%s, %s, %s, %s);
    """, (city[1], city[2], city[3], city[4]))

# ✅ Commit and close connection
conn.commit()
cursor.close()
conn.close()

# ✅ Print results
print("🏆 Top Cities for Airline Operations:")
for city in best_cities:
    print(f"   🌍 City: {city[1]}")
    print(f"   ✈️  Nearest Airport: {city[2]}")
    print(f"   📏 Distance: {city[3]:.2f} km")
    print(f"   🌱 Estimated CO₂ Emissions: {city[4]} metric tons\n")

print("✅ Best cities stored in database!")
