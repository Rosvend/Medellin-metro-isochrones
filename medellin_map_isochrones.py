import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import numpy as np

def create_metro_map(geojson_file, city_name):
    # Load the GeoJSON file
    gdf = gpd.read_file(geojson_file)
    
    # Print information about the data
    print(f"Total features: {len(gdf)}")
    print(f"Geometry types: {gdf.geometry.type.value_counts()}")
    print(f"Columns: {gdf.columns}")

    # Remove rows with invalid geometries
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.is_valid]
    
    # Separate stations and lines
    stations = gdf[gdf.geometry.type == 'Point']
    lines = gdf[gdf.geometry.type.isin(['LineString', 'MultiLineString'])]
    
    # Check if we have valid data
    if len(stations) == 0 and len(lines) == 0:
        print("No valid station or line data found in the GeoJSON file.")
        return

    # Calculate the center of the map, handling potential NaN values
    valid_coords = stations[~stations.geometry.x.isna() & ~stations.geometry.y.isna()]
    if len(valid_coords) > 0:
        center_lat = valid_coords.geometry.y.mean()
        center_lon = valid_coords.geometry.x.mean()
    else:
        print("No valid coordinates found for stations. Using default center.")
        center_lat, center_lon = 0, 0  # Default center if no valid coordinates

    # Create a map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Add lines to the map
    for idx, row in lines.iterrows():
        if row.geometry.type == 'LineString':
            coords = [(coord[1], coord[0]) for coord in row.geometry.coords]
        elif row.geometry.type == 'MultiLineString':
            coords = [(coord[1], coord[0]) for line in row.geometry.geoms for coord in line.coords]
        else:
            continue  # Skip invalid geometries

        folium.PolyLine(
            locations=coords,
            color=row.get('color', 'blue'),
            weight=2,
            opacity=0.8
        ).add_to(m)
    
    # Create a MarkerCluster for stations
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add stations to the map
    for idx, row in stations.iterrows():
        if np.isnan(row.geometry.y) or np.isnan(row.geometry.x):
            print(f"Skipping station with invalid coordinates: {row.get('name', 'Unknown')}")
            continue

        folium.CircleMarker(
            location=(row.geometry.y, row.geometry.x),
            radius=5,
            popup=folium.Popup(f"Station: {row.get('name', 'Unknown')}<br>Line: {row.get('line', 'Unknown')}", max_width=300),
            color='black',
            fill=True,
            fillColor=row.get('color', 'red'),
            fillOpacity=0.7
        ).add_to(marker_cluster)
    
    # Save the map
    output_file = f"{city_name.lower().replace(' ', '_')}_metro_map.html"
    m.save(output_file)
    print(f"Map saved as {output_file}")

# Usage
geojson_file = r'C:\Users\royda\Downloads\geojson_estaciones_del_sistema_de\estaciones_del_sistema_de.geojson'
city_name = 'Medellin'
create_metro_map(geojson_file, city_name)