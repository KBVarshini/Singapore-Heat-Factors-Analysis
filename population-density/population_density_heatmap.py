import os
import pandas as pd
import folium
import folium.plugins
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# This library is need since the CSV file is read from my S3 bucket. 
# So it handles all the binary data from this online source.
from io import BytesIO

# Create a map object using the folium.Map function.
# Need to specify the location and the zoom level.
# Must ensure that the whole of SG is visible on the map, so zoom level = 11.
# Coordinates = (latitude --> North & South, longitude --> East & West)
sgMap = folium.Map(location=[1.3521, 103.8198], zoom_start=11)

# URL of the CSV file
csv_url = os.path.join(os.path.dirname(__file__), "..", "data", "PivotTable_PopDen.csv")

# Reads the population density values + subzone names from the CSV file.
popData_2022 = pd.read_csv(csv_url)

# Create a list to store the data for the heat map
heat_data = []

# Iterate over each row of the DataFrame using the iterrows method.
# Get the subzone name, population density, latitude, and longitude from the current row.
# Use the geolocator to geocode the subzone name and obtain its location (lat. & long.)
# If a location is successfully obtained, add the latitude, longitude, and population density to the heat data list.
for _, row in popData_2022.iterrows():
    subzone = row["Row Labels"]
    population_density = row["Sum of Pop"]
    geolocator = Nominatim(user_agent="my_geocoder", timeout=30)
    location = geolocator.geocode(subzone + ", Singapore")
    if location is not None:
        latitude = location.latitude
        longitude = location.longitude
        heat_data.append([latitude, longitude, population_density])

# Create a colormap for the heat map based on population density
colormap = {
    'low': 'blue',
    'medium': 'yellow',
    'high': 'red'
}

# Calculate the population density quartiles
pop_quartiles = popData_2022["Sum of Pop"].quantile([0.25, 0.5, 0.75])
low_threshold = pop_quartiles[0.25]
medium_threshold = pop_quartiles[0.5]
high_threshold = pop_quartiles[0.75]

# Add the heat map layer to the map using the HeatMap function.
# Set the radius and gradient options to customize the appearance of the heat map.

# folium.plugins.HeatMap: This initiates the creation of a heatmap using the HeatMap plugin from the Folium library.
folium.plugins.HeatMap(

    # This variable likely holds the data points for creating the heatmap. 
    # It holds the list of coordinate pairs (latitude, longitude) representing various points on the map.
    heat_data,

    # This sets the radius of each data point. 
    # A larger radius will result in a smoother heatmap, while a smaller radius will create a more defined one.
    radius=10,

    # This defines the colour gradient for the heatmap. 
    # It assigns different colours to diff. intensity levels. 
    # The colourmap contains colour values associated with low, medium & high intensity levels. 
    # The numbers (0.4, 0.65, and 1) represent the normalized intensity levels at which the colors change.
    gradient={0.4: colormap['low'], 0.65: colormap['medium'], 1: colormap['high']},

    # This adjusts the opacity of the heatmap colours. 
    # A higher value makes the colours more opaque, while a lower value makes them more transparent.
    min_opacity=0.7  # Adjust the opacity value to make the colors darker
).add_to(sgMap)

# Define a function, assign_colour, to assign the appropriate colour based on population density.
def assign_color(population_density):
    if population_density <= low_threshold:
        return colormap['low']
    elif population_density <= medium_threshold:
        return colormap['medium']
    else:
        return colormap['high']

# Create a custom colourmap using Matplotlib.
# This creates the colour scale on the map.
cmap = LinearSegmentedColormap.from_list("custom_colormap", list(colormap.values()))

linear_color_map = folium.LinearColormap(

    # Specifies the colours for the colourmap. 
    # These colours correspond to low, medium & high population density levels.
    colors=[colormap['low'], colormap['medium'], colormap['high']],

    # Setting minimum value for the colourmap. 
    # This is the minimum population density value from the dataset.
    vmin=popData_2022['Sum of Pop'].min(),

    # Setting maximum value for the colourmap. 
    # This is the maximum population density value from the dataset.
    vmax=popData_2022['Sum of Pop'].max(),
    caption='Pop. Density Scale',
)

# Add the colorbar to the map using add_to
linear_color_map.add_to(sgMap)

# Create a Rectangle using the boundaries and add it to the map
sg_boundaries = [
    [1.55600, 103.61522],  # North-West
    [1.55600, 104.05045],  # North-East
    [1.16, 104.05045],     # South-East
    [1.16, 103.61522],     # South-West
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
            bottom: 20px; right: 50px; width: 200px; height: 120px; 
            border: 3px solid black; z-index: 9999; font-size: 12px;
            background-color: white; opacity: 0.9;">
    <p style="margin-top: 10px; margin-left: 10px;"><strong>Population Density Levels</strong></p>
    <p style="margin-left: 10px;"><span style="color: blue;">&#9679;</span> Low</p>
    <p style="margin-left: 10px;"><span style="color: yellow;">&#9679;</span> Medium</p>
    <p style="margin-left: 10px;"><span style="color: red;">&#9679;</span> High </p>
</div>
'''
# Add the legend to the map.
sgMap.get_root().html.add_child(folium.Element(legend_html))

# Lastly, display the map with the heat map layer, colorbar, and legend
sgMap.save("population_density_heatmap.html")
print("Saved population_density_heatmap.html - open it in a browser.")
