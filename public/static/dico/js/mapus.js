var stateCodes = ["", 
	"AL", "AK", "AS", "AZ", "AR", "CA", "??", "CO", "CT", "DE", 
	"DC", "FL", "GA", "GU", "HI", "ID", "IL", "IN", "IA", "KS", 
	"KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", 
	"NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", 
	"OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VT", 
	"VA", "VI", "WA", "WV", "WI", "WY"];
	
var districtScope = "district",
	stateScope = "state";

function initmap(mapFrameID, mapFile) {
	// Initialize the map.
	var width = $(mapFrameID).width();
	var height = width / 8 * 5;
	if (height > window.innerHeight - 30) {
		height = window.innerHeight - 30;
		width = height / 5 * 8;
		$(mapFrameID).width(width);
	}
	

	function ready(error, us) {
	  if (error) return console.error(error);

		var projection = d3.geo.albersUsa()
			.scale(width * 4 / 3)
			.translate([width / 2, height / 2]);

		var path = d3.geo.path()
			.projection(projection);

		// add the path for all of the us land.
		svg.append("defs").append("path")
		  .attr("id", "land")
		  .datum(topojson.feature(us, us.objects.land))
		  .attr("d", path);

		svg.append("clipPath")
		  .attr("id", "clip-land")
		  .append("use")
			.attr("xlink:href", "#land");
			
		svg.append("g")
		  .attr("class", "land")
		  .attr("clip-path", "url(#clip-land)");
	}

	svg = d3.select(mapFrameID).append("svg")
		.attr("width", width)
		.attr("height", height);
		
	// json files for us state map and us districts map taken from https://gist.github.com/mbostock/4090846
	queue()
		.defer(d3.json, mapFile)
		.await(ready);
}

function mapdatapoints(mapFrameID, constituentAreaLabelID, newScope, dataPoints, countKey)
{
	var countMax;
	countMax = d3.max(dataPoints, function(d) {return d[countKey]; })

	if (countMax < 10) { countMax = 10; }

	var svg = d3.select(mapFrameID).select("svg");
	var circles = svg.selectAll(".bubble");

	rScale = d3.scale.linear()
				.domain([0, countMax])
				.range([0, 30]);

	// Clear the radii of all of the circles.
	circles.attr("r", 0);
	
	if (newScope == districtScope)
		$(constituentAreaLabelID).text('District');
	else
		$(constituentAreaLabelID).text('State');
	
	for (i = 0; i < dataPoints.length; ++i) {
		var dataPoint = dataPoints[i];
		var dataPointID;
		
		if (newScope == districtScope) {
			// Handle the special case for 'DC' here. The case for states with only one district
			// is handled elsewhere.
			if (dataPoint['state'] == 'DC') {
				dataPointID=100*stateCodes.indexOf(dataPoint['state']) + 98;
			} else {
				dataPointID=100*stateCodes.indexOf(dataPoint['state']) + dataPoint['district'];
			}
		}
		else {
			dataPointID=stateCodes.indexOf(dataPoint['state']);
		}

		var ba = circles.filter(function() { return (this.getAttribute("id")==dataPointID);})
		if (ba.size() == 0 && newScope == districtScope && dataPoint['district'] == 1) {
			ba = circles.filter(function() { return (this.getAttribute("id")==dataPointID-1);})
		}
		if (ba.size() > 0) {
			newRadius = rScale(dataPoint[countKey]);
			ba[0][0].setAttribute("r", newRadius);
		}
	}
}

function show_table_data(constituentTableBodyID, newScope, dataPoints, countKey)
{
	$(constituentTableBodyID).empty();
	
	tr = d3.select(constituentTableBodyID).selectAll("tr")
			.data(dataPoints)
			.enter()
			.append("tr");
	
	td = tr.selectAll("td")
			.data(function(d) { 
				if (newScope == districtScope)
					area =  d['state'] + "-" + d['district'];
				else
					area =  d['state'];
				return [area, d[countKey]];
			})
			.enter()
			.append("td")
			.text(function(d) { return d; });
}

function show_map(mapFrameID, districtLabel, districtSpan, usjsonfile, congressjsonfile, showDataFunc, newScope) {
	var circleData = [];

	var opts = {
	  lines: 13, // The number of lines to draw
	  length: 20, // The length of each line
	  width: 10, // The line thickness
	  radius: 30, // The radius of the inner circle
	  corners: 1, // Corner roundness (0..1)
	  rotate: 0, // The rotation offset
	  direction: 1, // 1: clockwise, -1: counterclockwise
	  color: '#000', // #rgb or #rrggbb or array of colors
	  speed: 1, // Rounds per second
	  trail: 60, // Afterglow percentage
	  shadow: false, // Whether to render a shadow
	  hwaccel: false, // Whether to use hardware acceleration
	  className: 'spinner', // The CSS class to assign to the spinner
	  zIndex: 2e9, // The z-index (defaults to 2000000000)
	  top: '50%', // Top position relative to parent
	  left: '50%' // Left position relative to parent
	};
	var target = document.getElementById(mapFrameID.substring(1));
	var spinner = new Spinner(opts).spin(target);

	var svg = d3.select(mapFrameID).select("svg");
	
	function mouseoverstate() {
	  stateIndex = parseInt(d3.select(this).select("title").text());
	  s = stateCodes[stateIndex]; 
	  districtSpan.html('').append(s);
	}

	function mouseoverdistrict() {
	  thisTitle = parseInt(d3.select(this).select("title").text());
	  stateIndex = (thisTitle / 100 | 0);
	  districtIndex = thisTitle % 100;
	  s = stateCodes[stateIndex] + "-"; 
	  if (districtIndex == 0) {
		s = s + "01";
	  } else if (districtIndex < 10) {
		s = s + "0" + districtIndex;
	  } else {
		s = s + districtIndex;
	  }

	  districtSpan.html('').append(s);
	}

	function mouseoutstate() {
	  districtSpan.html('');
	}

	function mouseoutdistrict() {
	  districtSpan.html('');
	}

	function ready(error, us, congress) {
		if (error) return console.error(error);

		var districts = congress.objects.districts;

		var width = $(mapFrameID).width(),
			height = width / 8 * 5;
		if (height > window.innerHeight - 30) {
			height = window.innerHeight - 30;
			width = height / 5 * 8;
		}

		svg.attr("width", width)
		   .attr("height", height);
	   
		var projection = d3.geo.albersUsa()
			.scale(width * 4 / 3)
			.translate([width / 2, height / 2]);

		var path = d3.geo.path()
			.projection(projection);

		circleData = [];

		// Count the circleArray positions manually in case the indexes are not continuous.
		i = 0;
		var district = svg.select("g").selectAll("path");
	
		pathNodes = null;	
		if (newScope == districtScope) {
			  pathNodes = district.data(topojson.feature(congress, districts).features)
			.enter().append("path")
			  .attr("d", path)
			  .attr("class", "district")
			  .on("mouseover", mouseoverdistrict)
			  .on("mouseout", mouseoutdistrict)
			  .each(function(d){
					// Get the centroid or, if the centroid is degenerate, the bounds.
					centroid = path.centroid(d);
					if (isNaN(centroid[0]))
						centroid = path.bounds(d);

					if (!isNaN(centroid[0])) {
						circleData[i] = {"cx": centroid[0], "cy": centroid[1], "r": 0, "id": d.id};
						i++;
					}
				});
		} else {
			pathNodes = district.data(topojson.feature(us, us.objects.states).features)
				.enter().append("path")
				.attr("d", path)
				.attr("class", "state")
				.on("mouseover", mouseoverstate)
				.on("mouseout", mouseoutstate)
				.each(function(d){
						// Get the centroid or, if the centroid is degenerate, the bounds.
					centroid = path.centroid(d);
					if (isNaN(centroid[0]))
						centroid = path.bounds(d);

					if (!isNaN(centroid[0])) {
						circleData[i] = {"cx": centroid[0], "cy": centroid[1], "r": 0, "id": d.id};
						i++;
					}
				});
		}

		pathNodes
		  .append("title")
		  .text(function(d) { return d.id; });

		if (newScope == districtScope) {
		  svg.append("path")
			  .attr("class", "border border--district")
			  .datum(topojson.mesh(congress, congress.objects.districts, function(a, b) { return a !== b && (a.id / 1000 | 0) === (b.id / 1000 | 0); }))
			  .attr("d", path);
		}

		svg.append("path")
		  .attr("class", "border border--state")
		  .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
		  .attr("d", path);
  
		circles = svg.selectAll("circle")
			.data(circleData)
			.enter()
			.append("circle")
				.attr("class", "bubble")
				.attr("cx", function(d, i) { return d.cx; })
				.attr("cy", function(d) { return d.cy; })
				.attr("r", function(d) { return d.r; })
				.attr("id", function(d) { return d.id; })
				.call(showDataFunc);
		
		spinner.stop();
	}

	// Set the label for the object when mousing over.
	if (newScope == districtScope)
		$(districtLabel).html('').append("District:");
	else
		$(districtLabel).html('').append("State:");
	
	svg.selectAll(".district").remove();
	svg.selectAll(".state").remove();
	svg.selectAll(".border").remove();
	svg.selectAll(".bubble").remove();

	// json files for us state map and us districts map taken from https://gist.github.com/mbostock/4090846
	queue()
		.defer(d3.json, usjsonfile)
		.defer(d3.json, congressjsonfile)
		.await(ready);
}

function resizemap(mapFrameID) {
	var width = $(mapFrameID).width();
	var height = width / 8 * 5;
	if (height > window.innerHeight - 30) {
		height = window.innerHeight - 30;
		width = height / 5 * 8;
		$(mapFrameID).width(width)
	}

	var projection = d3.geo.albersUsa()
		.scale(width * 4 / 3)
		.translate([width / 2, height / 2]);

	var path = d3.geo.path()
		.projection(projection);

	var svg = d3.select(mapFrameID).select("svg");

	// add the path for all of the us land.
	svg.select("defs").select("path")
	  .attr("d", path);
}

function initmapheight(mapFrameID)
{
	d3.select(self.frameElement).style("height", ($(mapFrameID).width() / 8 * 5) + "px");
}

