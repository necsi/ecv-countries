//var margin = {top: 50, right: 20, bottom: 50, left: 20},
var margin = {top: 58, right: 30, bottom: 58, left: 30},
//var margin = {top: 50, right: 30, bottom: 50, left: 30},
    width = 270 - margin.left - margin.right,
    height = 220 - margin.top - margin.bottom;
 
//Read the data from csv file
// d3.csv("./result.csv", function(data) {
  d3.csv("./result.csv", function(dataset) {

  var data = [];  // storing based on color 
  for(var i = 0; i < dataset.length; i++){
    if(dataset[i].color == 'orange'){
      data.push(dataset[i]);
    }
  }
  var dataOrganized = d3.nest() // organize all data by country 
    .key(function(d) { if(d.color == 'orange'){ return d.country;}})  // keys are country, values are the data associated w the country
    .entries(data);
    //console.log(data);
  //all x axis scales are the same 
  var x = d3.scaleTime()
    .domain(d3.extent(data, function(d) { return d3.timeParse("%Y-%m-%d")(d.date); }))
    .range([ 0, width-margin.left]);  // adds extra padding to line chart 

  var y = d3.local();
  /* // area under line variable
  var area = d3.local(); */ 
  var line = d3.local();
  var yy = d3.local();

  var svg = d3.select("#my_dataviz")
    .selectAll("uniqueChart")
    .data(dataOrganized)
    .enter()
    .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")")
    .each(function(d) {
      //y axis scales unique to each chart 
      var ty = y.set(this, d3.scaleLinear()
        .domain([0, d3.max(d.values, function(d) { return +d.avg_cases; })])
        .range([height-10, 0]));

      /* // code for shading area under the line
      area.set(this, d3.area()
        .x(function(d) { return x(d3.timeParse("%Y-%m-%d")(d.date)); })
        .y0(height)
        .y1(function(d) { return ty(+d.avg_cases); })); */

      line.set(this, d3.line()
        .x(function(d) { return x(d3.timeParse("%Y-%m-%d")(d.date)); })
        .y(function(d) { return ty(+d.avg_cases); }));
    });

  svg
    .append("g")
    // .attr("transform", "translate(0," + height + ")")
    .attr("transform", "translate(0," + (height-10)+ ")")
    .style("font-size", "8px") // font size for dates
    .call(d3.axisBottom(x).ticks(5).tickFormat(d3.timeFormat("%b"))); // plotting x axis for each svg plot
  svg
    .append("path") // plotting line for each svg plot
    .attr("fill", "none")
    .attr("stroke", function(d) {return (d.values[0].color);})  // values holds each country's color from result.csv
    .attr("stroke-width", 2)
    .attr("d", function(d) { return line.get(this)(d.values); }); // plots each point 

  svg.each(function(d){
    var ty = yy.set(this, d3.scaleLinear()
      .domain([0, d3.max(d.values, function(d) { return +d.avg_cases; })])
      .range([height-10, 0]));

    var svg = d3.select(this),
      filtered_data = svg.datum().values;

    var focus = svg.append("g")
      .attr("class", "focus")
      .style("display", "none");
    // creates dot to follow over paths 
    focus.append("circle")
      .attr("fill", function(d) {return (d.values[0].color);})
      .attr("r", 5);
        
    // creates box to hold text 
    focus.append("rect")
      .attr("class", "tooltip")
      .attr("width", 80)
      .attr("height", 50)
      .attr("x", -25)
      .attr("y", -55)
      .attr("rx", 4)
      .attr("ry", 4);

    focus.append("text")
      .attr("x", -25)
      //.attr("dy", 0)
	  .attr("dy", 10)
	  .style("font-size", "12px");
        
    focus.append("text")
      .attr("class", "tooltip-date")
      .attr("x", -20)
      //.attr("y", -45)
	  .attr("y", -40)
	  .style("font-size", "12px");

    focus.append("text")
      .attr("class", "tooltip-info-avg")
      .attr("x", -20)
      .attr("y", -26)
	  .style("font-size", "12px");

    focus.append("text")
      .attr("class", "tooltip-info-new")
      .attr("x", -20)
      .attr("y", -12)
	  .style("font-size", "12px");

    svg.append("rect")
      .attr("class", "overlay")
      .attr("fill", "none")
      .attr("width", width-margin.left) // extra padding since we gave extra padding to line chart
      .attr("height", height)
      .on("mouseover", function() { focus.style("display", null); })
      .on("mouseout", function() { focus.style("display", "none"); })
      .on("mousemove", function(){
        var x0 = x.invert(d3.mouse(this)[0]), 
            i = (d3.bisector(function(d) { return (d3.timeParse("%Y-%m-%d")(d.date)); }).left)(filtered_data, x0, 1),
            d0 = filtered_data[i - 1],
            d1 = filtered_data[i],
            d = x0 - d0.date > d1.date - x0 ? d1 : d1;
        var curr_date = (d3.timeParse("%Y-%m-%d")(d.date));
        focus.attr("transform", "translate(" + x(d3.timeParse("%Y-%m-%d")(d.date)) + "," + ty(+d.avg_cases) + ")");
        focus.select(".tooltip-date").text(d3.timeFormat("%B %d")(curr_date));
        focus.select(".tooltip-info-avg").text("7-day avg: "+ d3.format(",")(Math.floor(+d.recent_new)));
        focus.select(".tooltip-info-new").text("New: "+ d3.format(",")(+d.new_cases));
      });
  })

  // country titles
  svg
    .append("text")
    .attr("text-anchor", "middle")
    .attr("transform",
          "translate(" + ((width-margin.left)/2) + " ," + (height+24) + ")") //centers titles
    .text(function(d){ return(d.key)})
	.style("font-size", "18px")
    .style("fill", "black");

    // total cases title
    svg
    .append("text")
    .style("font-size", "13px")
	//.attr("x", 0)
    //.attr("y", 10)
    .attr("text-anchor", "middle")
    .attr("transform",
          "translate(" + ((width-margin.left)/2) + " ," + (height+40) + ")") //centers titles
    .text(function(d){ return("Total Cases: "+d3.format(",")(d.values[0].total_cases))})
    .style("fill", "grey");
  
    // recent/new day title
    svg
    .append("text")
    .style("font-size", "13px")
    .attr("text-anchor", "middle")
    .attr("transform",
          "translate(" + ((width-margin.left)/2) + " ," + (height+55) + ")") //centers titles
    .text(function(d){ return("Recent New/Day: "+ d3.format(",")(Math.floor(d.values[d.values.length-1].recent_new)))})
    .style("fill", "grey");
})
