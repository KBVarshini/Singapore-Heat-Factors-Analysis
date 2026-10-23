/*--------------------------------------------------------------------------------------------------------------- */

// Define the boundary of Singapore using a Polygon Geometry.
// Polygon is a geometric shape consisting of a closed figure with straight sides. 
// It is defined by a set of vertices (points) connected by straight lines.

var singaporeBoundary = ee.Geometry.Polygon([
    [
      [103.5901, 1.1305],
      [104.0429, 1.1305],
      [104.0429, 1.4708],
      [103.5901, 1.4708],
      [103.5901, 1.1305]
    ]
  ]);
  
  // Filter the image collection using Landsat 8 imagery by date and location, which is Singapore.
  // So the time range is 1/1/2015 to 31/12/2022 for the data collection. This is the latest dataset.
  // The, sort by the cloud cover, to get accurate results.
  var collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')

  //Apply the filter .filterBounds(singaporeBoundary) to the collection of satellite pictures, 
  // it's like telling the satellite, "Show me only the pictures that cover the area inside the 
  // shape we drew around Singapore."
    .filterBounds(singaporeBoundary) 
    .filterDate('2015-01-01', '2022-12-31') // Filter the collection by date range
    .sort('CLOUD_COVER'); //Sort the collection to avoid Cloud Cover
  
  // Create a method/function to calculate NDVI, Normalized Difference Vegetation Index.
  // B5 & B4 are the band names and we are matching them to their corresponding images.
  // The image will be renamed to NDVI.

  //Bands = different channels of data, each representing specific portions of electromagnetic spectrum
  // & combining information from multiple bands allows us to analyze + extract valuable insights about the Earth's surface and its features in remote sensing.
  var calculateNDVI = function(image) {
    var ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI');
    return image.addBands(ndvi);
  };
  
  // Then, calculate NDVI for each image in the collection using the method above.
  // It is used in remote sensing to assess & monitor vegetation health and density. 
  // NDVI is calculated using near-infrared (NIR) & red (RED) bands of multispectral satellite or aerial imagery.
  var ndviCollection = collection.map(calculateNDVI);
  
  // Then, select only the NDVI bands from the collection.
  var ndviImages = ndviCollection.select('NDVI');
  
  // Define a water mask using the MNDWI (Modified Normalized Difference Water Index).
  // This is to exclude the water bodies when the map is displayed. 
  // Data collection should only be focused on the land area.
  var calculateMNDWI = function(image) {
    var mndwi = image.normalizedDifference(['B3', 'B6']).rename('MNDWI');
    return image.addBands(mndwi);
  };
  
// Calculate MNDWI for each image in the collection.
// MNDWI (Modified Normalized Difference Water Index) is used to identify water bodies in the imagery.
// It is calculated by taking the difference between the green (Band 3) and short-wave infrared (Band 6) reflectance,
// and then dividing it by the sum of green and short-wave infrared reflectance.
// A higher MNDWI value indicates a higher likelihood of water presence in the image.
var mndwiCollection = collection.map(calculateMNDWI);

// Select only the MNDWI bands from the collection.
var mndwiImages = mndwiCollection.select('MNDWI');

// Calculate the mean MNDWI across the collection.
// The mean MNDWI represents the average water presence across all the images in the collection.
var meanMNDWI = mndwiImages.mean();

// Define a threshold for the water mask.
// The water threshold is a value that helps differentiate water pixels from non-water pixels in the mean MNDWI image.
// Pixels with MNDWI values greater than the water threshold are classified as water, while those below are not.
var waterThreshold = 0;

// Create a water mask using the MNDWI threshold.
// The water mask is a binary image where pixels classified as water have a value of 1 (true) and non-water pixels have a value of 0 (false).
// This mask is useful for further analysis, like excluding water bodies from vegetation cover calculations.
var waterMask = meanMNDWI.gt(waterThreshold);

// Calculate the mean NDVI across the collection.
// The mean NDVI represents the average vegetation health and density across all the images in the collection.
var meanNDVI = ndviImages.mean();

// Clip the mean NDVI to Singapore's boundary.
var clippedNDVI = meanNDVI.clip(singaporeBoundary);
  
// Apply the water mask to the clipped NDVI.
var maskedNDVI = clippedNDVI.unmask(0).updateMask(waterMask.not());
  
// Define the levels of vegetation cover and their corresponding colors.
var levels = ['Low Vegetation', 'Medium Vegetation', 'High Vegetation'];
var colors = ['#FFFF00', '#0000FF', '#FFFFFF'];
  
// Create a map panel to add the map and chart later on.
var mapPanel = ui.Map();
  
// Add the vegetation cover layer to the map.
mapPanel.addLayer(maskedNDVI, { min: 0, max: 1, palette: colors }, 'Vegetation Cover');
  
// Create a feature representing the Singapore boundary.
var singaporeBoundaryFeature = ee.Feature(singaporeBoundary, {});
  
// Create an empty image to draw the boundary.
var boundaryImage = ee.Image().byte();

  // Paint the boundary feature on the empty image. 
  // This creates a black color border around the Singapore area.
  var boundaryLayer = boundaryImage.paint({
    featureCollection: ee.FeatureCollection([singaporeBoundaryFeature]),
    color: 1,
    width: 3
  });
  
  // Define the visualization parameters for the boundary layer.
  var boundaryVisParams = {
    palette: '000000',
    width: 3
  };
  
  // Add the boundary layer to the map.
  // If layer is not added to the map, there will be no output.
  mapPanel.addLayer(boundaryLayer, boundaryVisParams, 'Singapore Boundary');
  
  // Set the map center to Singapore and zoom level to 10.
  // The output will centralize singapore on the map.
  mapPanel.centerObject(singaporeBoundary, 10);
  
  // Then, create a time series chart.
  var chart = ui.Chart.image.series({
    imageCollection: ndviImages,
    region: singaporeBoundary,
    reducer: ee.Reducer.mean(),
    scale: 30
  }).setChartType('LineChart')  // Set the chart type to LineChart
  .setOptions({
    title: 'Changes of Vegetation Cover over 7 years',
    titleTextStyle: {
      fontSize: 16,
      bold: true,
      textAlign: 'center'
    },
    hAxis: {
      title: 'Years',
      ticks: ee.List.sequence(2015, 2022),
      format: 'YYYY',
      gridlines: {
        count: 8
      },
      minorGridlines: {
        count: 0
      }
    },
    vAxis: {
      title: 'NDVI'
    },
    lineWidth: 1,
    pointSize: 3,
    series: {
      0: { color: 'FF0000' },
    },
    chartArea: { width: '80%', height: '80%' }  
    // We can adjust these values to size the chart on the panel.
  });
  
  // Create a panel for the chart.
  var chartPanel = ui.Panel([chart], 'flow', { width: '100%', height: '50%' });
  
  // Create a vertical panel to hold the map(with legend) + chart panels.
  var mainPanel = ui.Panel([
    mapPanel,
    chartPanel
  ], 'flow', { 
    width: '100%', // Width & Height can be adjusted.
    height: '120%' // We can change these values based on how big or small the panel should be.
    
  });
  
  // Define the levels of vegetation cover and their corresponding colors
  var levels = ['Low Vegetation', 'Medium Vegetation', 'High Vegetation'];
  var colors = ['#FFFF00', '#0000FF', '#FFFFFF'];
  
  // Define the legend
  var legend = ui.Panel({
    style: {
      position: 'bottom-right',
      padding: '8px 15px'
    }
  });
  
  // Define the legend title
  var legendTitle = ui.Label({
    value: 'Vegetation Cover Levels',
    style: {
      fontWeight: 'bold',
      fontSize: '16px',
      margin: '0 0 4px 0',
      padding: '0'
    }
  });
  legend.add(legendTitle);
  
  // Add the legend items
  for (var i = 0; i < levels.length; i++) {
    var colorBox = ui.Label({
      style: {
        backgroundColor: colors[i],
        padding: '8px',
        margin: '0 0 4px 0',
        border: '1px solid black'
      }
    });
  
    var description = ui.Label({
      value: levels[i],
      style: { margin: '0 0 4px 6px' }
    });
  
    legend.add(ui.Panel([colorBox, description], ui.Panel.Layout.Flow('horizontal')));
  }
  
  // Add the legend panel to the map panel.
  mapPanel.add(legend);
  
  // Add the main panel to the UI root.
  // This displays the map and the chart below. 
  // Users can expand the chart for a better view and hover to see its values too.
  ui.root.widgets().reset([mainPanel]);
  
