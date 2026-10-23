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
# Must ensure that the whole of SG is visible in the map. So, zoom level = 11.
# Decimal values for zoom_level are not allowed. Can only take in whole numbers.
sgMap = folium.Map(location=[1.3521, 103.8198], zoom_start=11)

# URL of the CSV file
csv_url = os.path.join(os.path.dirname(__file__), "..", "data", "PivotTable_PopDen.csv")

# Reads the population density values + subzone names from the CSV file.
popData_2022 = pd.read_csv(csv_url)

# Define the low, medium, and high population density thresholds.
low_threshold = 7000  
medium_threshold = 25000
high_threshold = float('inf')

# Create the function to color code the subzones based on their population density level (Low, Medium, High).
# Function takes the population_density as an input parameter. 
# This is a numerical value representing how many people live in the subzone.

def color_code(population_density):

    # It checks if the population density is 0. If it is, the function returns None, which means no color will be assigned. 
    # This is done to exclude areas with no population, 0 values.
    if population_density == 0:
        return None  # Exclude subzones with 0 population density. 
    

    # If the population density is not 0, it compares the density to the thresholds:
    # If the density is less than or equal to a low_threshold, it returns "yellow".
    # If the density is greater than low_threshold but less than or equal to a medium_threshold, it returns "orange".
    # Otherwise, if the density is higher than both the low_threshold and medium_threshold, it returns the "red".

    elif population_density <= low_threshold:
        return "yellow"
    elif population_density <= medium_threshold:
        return "orange"
    else:
        return "red"

# Then, color code the subzones on the map and exclude subzones with 0 population density.

# It loops through each row in the popData_2022 dataset 
# (contains info about subzones & corresponding population data for the year 2022).
# Inside the loop, it extracts the subzone name + associated population density from the current row.

for _, row in popData_2022.iterrows():
    subzone = row["Row Labels"]
    population_density = row["Sum of Pop"]

    # Exclude subzones with 0 population density.
    # It then checks if the population density is 0. If it is, the code uses the continue statement to skip the current iteration of the loop and move on to the next row. This effectively excludes subzones with no population from further processing.
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

    # It checks if the location (latitude and longitude) is provided.
    # If the location is available, it calculates the latitude & longitude from the provided location.
    # Then, it determines a colour for the circle marker on the population density value.
    if location is not None:
        latitude = location.latitude
        longitude = location.longitude
        color = color_code(population_density)

    # If a valid color is chosen, it creates a circular marker (circle) on the map.
    # This marker has a specified radius (size), colour, and is filled with the same color.
    # The tooltip (a small pop-up information) for the circle contains the subzone name and population density.
    # Finally, it adds this circle marker to a map (sgMap) for visualization.    
        if color is not None:
            folium.CircleMarker(
                location=[latitude, longitude],

                # This marker has a specified radius (size), colour, and is filled with the same color.
                radius=5,
                color=color,

                # This fills the circle markers with the respective colours.
                fill=True,
                fill_color=color,
                fill_opacity=1,

                # The tooltip (a small pop-up information) for the circle contains the subzone name and population density.
                tooltip=f"Subzone: {subzone}<br>Population Density: {population_density}",

                # Finally, it adds this circle marker to a map (sgMap) for visualization. 
            ).add_to(sgMap)

# Define the boundaries of Singapore as latitude-longitude coordinates.
sg_boundaries = [
    [1.12, 103.57],  # South-West corner
    [1.48, 104.03]   # North-East corner
]


# Create a Rectangle using the boundaries and add it to the map.
# The rectangle is outlined in black color.
folium.Rectangle(
    bounds=sg_boundaries,
    color="black",

    # The weight parameter controls the thickness of the outline.
    weight=2,

    # The rectangle is not filled, meaning it's just an outline without any color inside.   
    fill=False,

    # It gives a name to this rectangle as "Singapore Outline".
    name="Singapore Outline",

    # Finally, it adds this rectangle to the existing map (sgMap) for visualization.
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
sgMap.save("population_density_normal.html")
print("Saved population_density_normal.html - open it in a browser.")


# FOR CALCULATION:
# 1. Calculate the quartiles (25th and 75th percentiles) of the population density data.
# 2. Determine the lower and upper limits for each category:
# 3. The lower limit for the "Low" category is 0 since it includes subzones with a population density of 0.
# 4. The upper limit for the "Medium" category can be set to a value that separates data approximately into thirds, 
# which is the population density at the 66.67th percentile. (7,001 to 25,000)
# 5. The upper limit for the "High" category can be set as any value > 66.67th percentile, 
# in this case, the maximum population density value is 25,001 >.


# Calculate the quartiles:

# Sort the population density values in ascending order.
# Find the 25th percentile (Q1) and 75th percentile (Q3) values.
# Determine the lower and upper limits for each category:

# "Low" category: Lower limit = 0, Upper limit = Q1 (25th percentile value).
# "Medium" category: Lower limit = Q1 (25th percentile value), Upper limit = Q2 (66.67th percentile value).
# "High" category: Lower limit = Q2 (66.67th percentile value), Upper limit = Maximum population density value.
