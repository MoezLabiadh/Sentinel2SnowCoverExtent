/*

MAKE PANEL SECTION

*/


var colors = {'cyan': '#24C1E0', 'transparent': '#11ffee00', 'gray': '#F8F9FA'};

var TITLE_STYLE = {
  fontWeight: '100',
  fontSize: '32px',
  padding: '8px',
  color: '#616161',
  backgroundColor: colors.transparent,
};

var SUBTITLE_STYLE = {
  fontSize: '16px',
  fontWeight: '80',
  color: '#616161',
  padding: '2px',
  backgroundColor: colors.transparent,
};


var PARAGRAPH_STYLE = {
  fontSize: '14px',
  fontWeight: '50',
  color: '#9E9E9E',
  padding: '8px',
  backgroundColor: colors.transparent,
};

var SUBPARAGRAPH_STYLE = {
  fontSize: '13px',
  fontWeight: '50',
  color: '#9E9E9E',
  padding: '2px',
  backgroundColor: colors.transparent,
};

var LABEL_STYLE = {
  fontWeight: '50',
  textAlign: 'center',
  fontSize: '11px',
  backgroundColor: colors.transparent,
};

var THUMBNAIL_WIDTH = 128;

var BORDER_STYLE = '4px solid rgba(97, 97, 97, 0.05)';


  var mainPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical', true),
    style: {
      stretch: 'horizontal',
      height: '100%',
      width: '550px',
      backgroundColor: colors.gray,
      border: BORDER_STYLE,
      position: 'top-left'
    }
  });

  // Add the app title to the side panel
  var titleLabel = ui.Label('Snow Explorer', TITLE_STYLE);
  mainPanel.add(titleLabel);

  // Add the app description to the main panel
  var descriptionText =
      'This app computes a Snow Cover Extent Layer based on user ' +
      'selected dates and Region of Interest.' +
      ' Data are derived from Sentinel-2 imagery.'  + 
      ' Please follow the steps below to run the tool:';
  var descriptionLabel = ui.Label(descriptionText, PARAGRAPH_STYLE);
  mainPanel.add(descriptionLabel);
  
  var firstSubTitle_text = '1) Select the Start and End dates';
  var firstSubTitle = ui.Label(firstSubTitle_text, SUBTITLE_STYLE);
  mainPanel.add(firstSubTitle);
  
   var firstSubParagraph_text = 'The tool will search for images between these dates. '+ 
                                 ' Date format must be: YYYY-MM-DD.';
   var firstSubParagraph = ui.Label(firstSubParagraph_text, SUBPARAGRAPH_STYLE);
   mainPanel.add(firstSubParagraph);
   
   var startDate = ui.Textbox({
     placeholder: 'Enter Start date here...',
     onChange: function(start) {
       startDate.setValue(start);
     }
    });
   
   //Get Today's date and pass it as default End date. 
   var now = new Date();
   var nowStr = now.toLocaleDateString('en-CA'); 
   var endDate = ui.Textbox({
     value: nowStr,
     placeholder: 'Enter End date here...',
     onChange: function(end) {
       endDate.setValue(end);
     }
    });
  
  mainPanel.add(startDate);
  mainPanel.add(endDate);

  var secondSubTitle_text = '2) Select the Region of Interest';
  var secondSubTitle = ui.Label(secondSubTitle_text, SUBTITLE_STYLE);
  mainPanel.add(secondSubTitle);
  
   var secondSubParagraph_text = 'Click on the button, then draw your Region of Interest on the map.';
   var secondSubParagraph = ui.Label(secondSubParagraph_text, SUBPARAGRAPH_STYLE);
   mainPanel.add(secondSubParagraph);
  
Map.add(mainPanel);

/*

IMAGERY PROCESSING SECTION

*/


Map.setCenter (-117,50,6);


var drawButton = ui.Button({
  label: 'Draw a Rectangle',
  onClick: function() {
// Don't make imports that correspond to the drawn rectangles.
Map.drawingTools().setLinked(false);
// Limit the draw modes to rectangles.
Map.drawingTools().setDrawModes(['rectangle']);
// Add an empty layer to hold the drawn rectangle.
Map.drawingTools().addLayer([]);
// Set the geometry type to be rectangle.
Map.drawingTools().setShape('rectangle');
// Enter drawing mode.
Map.drawingTools().draw();

Map.drawingTools().onDraw(function (geometry) {
  // Do something with the geometry
  var AOI = Map.drawingTools().toFeatureCollection(0);
  //Map.addLayer(AOI, null, 'Region of Interest');
  Map.centerObject(AOI);
  Map.drawingTools().stop();
  Map.drawingTools().layers().forEach(function(layer) {
  layer.setShown(false);
  });

  //Define dates
  var date_start = startDate.getValue();
  var date_end= endDate.getValue();

  //Define a Cloud Threshold
  var cloud_threshold = 20;

  //Setup a function to caclulate the NDSI
  function CalculateNDSI(image) {
    var NDSI = image.normalizedDifference(['B3', 'B11']).rename('NDSI');
    return image.addBands(NDSI);
        } 
        
  //Setup a function to caclulate the Cloud and Cloud Shadow Mask        
  function CloudMask (image){
    var cloud_mask = image.expression(
      "(b('MSK_CLDPRB') >= 90) ? 2 " +
       ": ((b('MSK_CLDPRB') >= 50) && (b('B8A') >= 3000)) || ((b('MSK_CLDPRB') >= 20) && (b('B8A') >= 9000))  ? 1" +
         ": 0").rename('CloudMask');
    return image.addBands(cloud_mask);
        } 

  //Add Sentinel-2 Collection and filter using AOI, dates, cloud threshold.
  var S2 = ee.ImageCollection("COPERNICUS/S2_SR")
      .filterDate(date_start, date_end)
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold))
      .sort('system:time_start')
      .filterBounds(AOI)
      .map(CloudMask) //Add Cloud Mask band.
      .map(CalculateNDSI); //Add NDSI band.

  print (S2);
  var mosaic = S2.mosaic();
  print (mosaic);

  //Create the Snow Cover Extent (SCE) layer
  var SCE = mosaic.expression(
      "((b('CloudMask') == 0 && (b('NDSI') >= 0.3) && (b('B4') >= 1000))) ? 2" +
       ": (b('CloudMask') > 0) ? 1" +
        ": 0"
    ).clip(AOI);

  //Create a Band Composite image (SWIR2,SWIR1,Green)
  var BandComposite = mosaic.clip(AOI);

  //Set the visualisation parameters.
  var SCEkViz = {
    min: 0,
    max: 2,
    palette: ['yellow', 'red','blue'],
  };

  var BandCompViz = {
    min: 0,
    max: 1500,
    gamma: [0.95, 1.1, 1]
  };

  //var mask = SCE.gt(0);
  var SCE_masked = SCE.updateMask(SCE.gt(0));

  Map.addLayer(BandComposite.select('B4', 'B3', 'B2').clip(AOI), BandCompViz, 'Sentinel-2 Imagery');
  Map.addLayer(SCE_masked.clip(AOI), SCEkViz, 'Snow Cover Extent');
  
});

  }


});

mainPanel.add(drawButton);

var thirdSubParagraph_text = 'To refresh the view, press F5 or use the "Reset Map!" button.';
var thirdSubParagraph = ui.Label(thirdSubParagraph_text, SUBPARAGRAPH_STYLE);
mainPanel.add(thirdSubParagraph);
var refreshButton = ui.Button({
  label: 'Reset Map!',
  onClick: function() {
   Map.setCenter (-117,50,6);
   Map.layers().reset();
   Map.drawingTools().layers().reset();
  }
});

mainPanel.add(refreshButton);



/*

ADD A LEGEND

*/



// set position of panel
var legend = ui.Panel({
  style: {
    position: 'bottom-right',
    padding: '8px 15px'
  }
});

// Create legend title
var legendTitle = ui.Label({
  value: 'Legend',
  style: {
    fontWeight: 'bold',
    fontSize: '18px',
    margin: '0 0 4px 0',
    padding: '0'
    }
});

// Add the title to the panel
legend.add(legendTitle);
    
// Creates and styles 1 row of the legend.
var makeRow = function(color, name) {
      
      // Create the label that is actually the colored box.
      var colorBox = ui.Label({
        style: {
          backgroundColor: '#' + color,
          // Use padding to give the box height and width.
          padding: '8px',
          margin: '0 0 4px 0'
        }
      });
      
      // Create the label filled with the description text.
      var description = ui.Label({
        value: name,
        style: {margin: '0 0 4px 6px'}
      });
      
      // return the panel
      return ui.Panel({
        widgets: [colorBox, description],
        layout: ui.Panel.Layout.Flow('horizontal')
      });
};

//  Palette with the colors
var palette =['0000FF', 'FF0000'];

// name of the legend
var names = ['Snow','Clouds'];

// Add color and and names
for (var i = 0; i < 2; i++) {
  legend.add(makeRow(palette[i], names[i]));
  }  

Map.add(legend);
