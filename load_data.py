import pandas as pd
import psycopg2

# PostgreSQL Connection Parameters
DB_PARAMS = {
    "dbname": "airline_db",
    "user": "postgres",
    "password": "Jaya2005",  # Replace with actual password
    "host": "localhost",
    "port": "5432"
}

# Connect to PostgreSQL
conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

# Load and Insert Airports Data
df_airports = pd.read_csv("airports.csv")

# Drop rows with missing 'iata' values
df_airports = df_airports.dropna(subset=['iata'])

# Convert 'iata' to string to avoid scientific notation issue
df_airports['iata'] = df_airports['iata'].astype(str)

# Ensure unique 'id' values
df_airports = df_airports.drop_duplicates(subset=['iata'])

for _, row in df_airports.iterrows():
    cursor.execute("""
        INSERT INTO airports (id, name, city, state, latitude, longitude) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING  -- Avoids duplicate key error
    """, (row['iata'], row['name'], row['city'], row['state'], row['latitude'], row['longitude']))

# Load and Insert Population Data
df_population = pd.read_csv("uscities.csv")

df_population = df_population.dropna(subset=['city', 'state_id'])  # Remove missing city/state
df_population = df_population.drop_duplicates(subset=['city', 'state_id'])  # Ensure unique cities

for _, row in df_population.iterrows():
    cursor.execute("""
        INSERT INTO population_data (city, state, population, latitude, longitude) 
        VALUES (%s, %s, %s, %s, %s)
    """, (row['city'], row['state_id'], row['population'], row['lat'], row['lng']))

# Commit and Close Connection
conn.commit()
cursor.close()
conn.close()
print("✅ Data successfully loaded into PostgreSQL.")
