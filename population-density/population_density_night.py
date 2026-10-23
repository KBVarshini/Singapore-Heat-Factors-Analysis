import os
# pandas library is used for data manipulation & analysis. 
# It provides data structures like DataFrames to handle tabular data. 
# It can also read data from CSV files and perform calculations if needed.
import pandas as pd

# folium library is used to create interactive maps and for visualizations.
# So we can create different types of maps, add polygons, shapes, and many more using folium.
# IN THIS CODE, folium is used to create the base map & add the circle dots/markers.
import folium

# Nominatim is an OpenStreetMap API.
# Geocoding = Converting addresses or place names into geographic coordinates (lat. & long.)
# IN THIS CODE, Nominatim is used to geocode the subzone names & retrieve the corresponding lat. & long. coordinates.
# These coordinates are then used to place the circle dots/markers on the map.
from geopy.geocoders import Nominatim

# Create a map object using the folium.Map function.
# Need to specify the location and the zoom level.
# Must ensure that the whole of SG is visible in the map. So, zoom level = 10.
# Decimal values for zoom_level are not allowed. Can only take in whole numbers.
sgMap = folium.Map(location=[1.3521, 103.8198], zoom_start=11, tiles="CartoDB dark_matter") # Night view of the map.

# URL of the CSV file
csv_url = os.path.join(os.path.dirname(__file__), "..", "data", "PivotTable_PopDen.csv")

# Reads the population density values + subzone names from the CSV file.
popData_2022 = pd.read_csv(csv_url)

# Define the low, medium, and high population density thresholds.
low_threshold = 7000  
medium_threshold = 25000
high_threshold = float('inf')

# Create the function to color code the subzones based on their population density level (Low, Medium, High).
def color_code(population_density):
    if population_density == 0:
        return None  # Exclude subzones with 0 population density. 
    elif population_density <= low_threshold:
        return "yellow"
    elif population_density <= medium_threshold:
        return "orange"
    else:
        return "red"

# Then, color code the subzones on the map and exclude subzones with 0 population density.
for _, row in popData_2022.iterrows():
    subzone = row["Row Labels"]
    population_density = row["Sum of Pop"]

    # Exclude subzones with 0 population density
    if population_density == 0:
        continue

    # IN THIS CODE, geolocator name is my_geocoder.
    # The timeout is like a time limit set for geocoding requests. 
    # "If it takes more than 30 seconds to convert the address into coordinates, stop trying & let us know." 
    # This is helpful because sometimes the geocoding service might be slow or unresponsive & we don't want my program to wait indefinitely for a response.
    geolocator = Nominatim(user_agent="my_geocoder", timeout=30)
    location = geolocator.geocode(subzone + ", Singapore")

    # If a location is successfully obtained, create a CircleMarker using the lat. & long. coordinates. 
    # Set the marker's radius, color, fill color & fill opacity based on the population density & color code. 
    # Add a tooltip showing the population density value.
    if location is not None:
        latitude = location.latitude
        longitude = location.longitude
        color = color_code(population_density)
        if color is not None:
            folium.CircleMarker(
                location=[latitude, longitude],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=1,
                tooltip=f"Subzone: {subzone}<br>Population Density: {population_density}",
            ).add_to(sgMap)

# Define the boundaries of Singapore as latitude-longitude coordinates.
sg_boundaries = [
    [1.12, 103.57],  # South-West corner
    [1.48, 104.03]   # North-East corner
]


# Create a Rectangle using the boundaries and add it to the map
folium.Rectangle(
    bounds=sg_boundaries,
    color="black",
    weight=2,
    fill=False,
    name="Singapore Outline",
).add_to(sgMap)

# Create a legend to add to the map
legend_html = f'''
<div style="position: fixed; 
            bottom: 20px; right: 50px; width: 210px; height: 120px; 
            border: 3px solid black; z-index: 9999; font-size: 12px;
            background-color: white; opacity: 0.9;">
    <p style="margin-top: 10px; margin-left: 10px;"><strong>Population Density Levels</strong></p>
    <p style="margin-left: 10px;"><span style="color: yellow;">&#9679;</span> Low: 0 to 7,000</p>
    <p style="margin-left: 10px;"><span style="color: orange;">&#9679;</span> Medium: 7,001 to 25,000</p>
    <p style="margin-left: 10px;"><span style="color: red;">&#9679;</span> High: 25,001 > </p>
</div>
'''

# Add the legend to the map.
sgMap.get_root().html.add_child(folium.Element(legend_html))

# Lastly, display the map with the circle markers.
sgMap.save("population_density_night.html")
print("Saved population_density_night.html - open it in a browser.")
