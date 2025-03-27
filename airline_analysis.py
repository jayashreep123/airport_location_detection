import psycopg2
import folium
from folium.plugins import HeatMap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim

# ✅ Database Connection
def connect_db():
    return psycopg2.connect(
        dbname="airline_db",
        user="postgres",
        password="Jaya2005",
        host="localhost",
        port="5432"
    )

# ✅ Fetch Data from PostgreSQL
def fetch_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT city, latitude, longitude, nearest_airport, distance_km, co2_emissions FROM airline_operations;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['City', 'Latitude', 'Longitude', 'Airport', 'Distance', 'CO2'])
    return df

# ✅ Generate Folium Map with Markers
def create_map(df):
    # Set initial location (USA Center)
    map_center = [39.8283, -98.5795]
    folium_map = folium.Map(location=map_center, zoom_start=5)

    for _, row in df.iterrows():
        popup_text = f"""
        🌍 <b>City:</b> {row['City']}<br>
        ✈️ <b>Nearest Airport:</b> {row['Airport']}<br>
        📏 <b>Distance:</b> {row['Distance']} km<br>
        🌱 <b>CO₂ Emissions:</b> {row['CO2']} metric tons
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="cloud")
        ).add_to(folium_map)

    # Save Map
    folium_map.save("airline_operations_map.html")
    print("✅ Map saved as 'airline_operations_map.html'")

# ✅ Generate Heatmap
def create_heatmap(df):
    folium_map = folium.Map(location=[39.8283, -98.5795], zoom_start=5)
    heat_data = df[['Latitude', 'Longitude']].values.tolist()
    HeatMap(heat_data).add_to(folium_map)

    folium_map.save("airline_operations_heatmap.html")
    print("✅ Heatmap saved as 'airline_operations_heatmap.html'")

# ✅ CO₂ Emissions Bar Chart
def plot_co2_emissions(df):
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='City', y='CO2', palette="coolwarm")
    plt.xticks(rotation=45)
    plt.xlabel("City")
    plt.ylabel("CO₂ Emissions (metric tons)")
    plt.title("CO₂ Emissions by City")
    plt.tight_layout()
    plt.savefig("co2_emissions_plot.png")
    print("✅ CO₂ emissions plot saved as 'co2_emissions_plot.png'")
    plt.show()

# ✅ Main Execution
if __name__ == "__main__":
    df = fetch_data()
    create_map(df)
    create_heatmap(df)
    plot_co2_emissions(df)
