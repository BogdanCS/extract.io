(function() {

  var LIMIT = 500;

  var keyword = "diabetes",
    response;

  var startDatepickerState = 0,
      endDatepickerState = 0,
    stopInitialAnimation = 0,
    activeTipsy = null;

  window.onload = function() {

    /*
     * initialize date picker
     */
    $("#startdatepicker").datepicker({
      dateFormat: "dd.mm.y",
      minDate: new Date(757382400), // 1 January 1994
      maxDate: new Date(),
      onSelect: function(date) {
	toggleDatepicker("#startdatepicker", "#startDatepickerBtn", true);
	setDateText(true, "#startdatepicker", "startDateText");  
	//TODO - set minDate for endDatePicker to selected date here
      }
    });
    $("#enddatepicker").datepicker({
      dateFormat: "dd.mm.y",
      minDate: new Date(757382400), // 1 January 1994
      maxDate: new Date(),
      onSelect: function(date) {
	toggleDatepicker("#enddatepicker", "#endDatepickerBtn", false);
	setDateText(true, "#enddatepicker", "endDateText");  
	removeTopics();
      }
    });
    $("#startdatepicker").datepicker("setDate", new Date());
    $("#enddatepicker").datepicker("setDate", new Date());
    $('#startDatepickerBtn').addClass('active');
    $('#endDatepickerBtn').addClass('active');

    /*
     * initialize topics
     */
    displayLoading();
    getTopics();

    /*
     * add moveToFront function to d3.js
     */
    d3.selection.prototype.moveToFront = function() {
      return this.each(function() {
        this.parentNode.appendChild(this);
      });
    };
  }

  window.onerror = function() {
    _("topics").innerHTML = "Ooops! Something went wrong!"
  }

  if (!window.XMLHttpRequest)
    XMLHttpRequest = function() {
      try {
        return new ActiveXObject("Msxml2.XMLHTTP.6.0")
      } catch (e) {}
      try {
        return new ActiveXObject("Msxml2.XMLHTTP.3.0")
      } catch (e) {}
      try {
        return new ActiveXObject("Msxml2.XMLHTTP")
      } catch (e) {}
      try {
        return new ActiveXObject("Microsoft.XMLHTTP")
      } catch (e) {}
      throw new Error("Could not find an XMLHttpRequest alternative.")
    };

  function _(id) {
    return document.getElementById(id);
  }

  function getTopics() {

      console.log("got here");
    // create url
    var pathArray = document.URL.split('/');
    var url = pathArray[0] + "//" + pathArray[2] + "/rpcNewSearch?keywords=" + keyword;

      startDate = Math.floor(jQuery("#startdatepicker").datepicker("getDate")
        .getTime() / 1000);
      endDate = Math.floor(jQuery("#enddatepicker").datepicker("getDate")
        .getTime() / 1000);
      url += "&start_date=" + startDate + "&end_date=" + endDate;
     
    url += "&limit=" + LIMIT;

    // make call
    var http_request = new XMLHttpRequest();
    http_request.open("GET", url, true);
    http_request.onreadystatechange = function() {
      if (http_request.readyState == 4) {
        hideLoading();

        if (http_request.status == 200) {
          onSuccess(http_request.responseText);
        } 
        else {
          onFailure();
        }
      }
    }

    http_request.send(null);

    pauseInitialAnimation();
    displayLoading();
  }

  function onSuccess(responseText) {

    // parse responseText
    try {
      response = JSON.parse(responseText);
    } catch (e) {
      response = responseText;
    }

    if (response == "") {
      _("topics").innerHTML = "YOU SHOULD ENTER VALID INPUT!";
      return;
    }

    if (response.topics.length == 0) {
      _("topics").innerHTML = "NO TOPIC FOUND!";
      return;
    }

    drawTopics();
    setCurrentChartExplanation();
    stopInitialAnimation = 0;
    setTimeout(startInitialAnimation, 3000);
  }

  function onFailure(msg) {
    _("topics").innerHTML = msg || "YOU CRASHED IT!"
  }

  function displayLoading() {
    $("#topics").empty().append('<span>Loading...</span><div id="loading-area"><div class="spinner"></div></div>');
  }

  function hideLoading() {
    $("#topics").empty()
  }

  /**
   * Draws chart
   */
  function drawTopics(callback) {
    currentChart.draw(callback);
  }

  /**
   * Removes chart
   */
  function removeTopics() {
    currentChart.remove();
  }

  /**
   * Initial animation.
   * Fired when site launched (after chart are drawn)
   */
  function startInitialAnimation(list, index) {
    try {
      if (stopInitialAnimation) {
        return;
      }
      if (!list) {
        list = $('circle');
      }
      if (typeof index == "undefined") {
        index = 0;
      }
      if (list[index]) {
        activeTipsy = $(list[index]).mouseover();
        setTimeout(function() {
          $(list[index]).mouseout();
          activeTipsy = null;
          startInitialAnimation(list, index + 1);
        }, 5000);
      }
    } catch (e) {
      // TODO: handle exception
    }
  }

  function pauseInitialAnimation() {
    if (activeTipsy) {
      activeTipsy.mouseout();
      stopInitialAnimation = 1;
      activeTipsy = null;
    }
  }

  /**
   * Set current chart explanation
   */
  function setCurrentChartExplanation(message) {
    var message = "Topics extracted from medical abstracts published";

      message += " between " + jQuery("#startdatepicker")
        .datepicker("getDate")
        .toDateString()
        .substring(4) + " and " + jQuery("#enddatepicker")
	.datepicker("getDate")
	.toDateString()
	.substring(4);

    if (keyword == "diabetes") {
      message += " about Diabetes";
    } else {
      message += " about Cancer";
    }

    $('#topics').prepend("<span>" + message + "</span>");
  }

  function setKeyword(node, r) {
    if (keyword != r) {
      keyword = r;
      removeTopics();

      // change style
      changeRegionBtnStyle(node);
    }
    return false;
  }

  function setDateText(date, picker, text) {
    if (date) {
      _(text).innerHTML = jQuery(picker)
        .datepicker("getDate")
        .toDateString()
        .substring(4);
    } else {
      _(text).innerHTML = "pick a date";
    }
  }

  function changeRegionBtnStyle(node) {
    $('nav a').removeClass('current');
    $(node).addClass('current');
  }

  function toggleDatepicker(picker, pickerBtn, start) {
    if ((start && startDatepickerState) ||
        (!start && endDatepickerState)) {
      $(picker).slideUp();
      $(pickerBtn).removeClass('datepicker-open');
    } else {
      $(picker).slideDown();
      $(pickerBtn).addClass('datepicker-open');
    }
    if(start)
    {
	startDatepickerState = !startDatepickerState;
    }
    else
    {
	endDatepickerState = !endDatepickerState;
    }

    return false;
  }

  /**
   * Charts
   */
  var charts = {
    bubbleChart: function() {

      var area = _("topics"),
	node,
	svg;

      return {
        draw: function() {
           // Clear draw area.
           area.innerHTML = null;

          var w = area.offsetWidth;
          var h = area.offsetHeight;

          svg = d3.select("#topics").append("svg")
            .attr("width", w)
            .attr("height", h);

	  // Links - forces
	  // Set a threshold for creating an edge
	  // or keep top edges for every node
	  // Fix the documents stuff
	  // Delete lone numbers
	  // multi select
	  var links = response.links;
	  var simulation = d3.forceSimulation()
		.force("link", d3.forceLink().id(function(d) { return d.uid; })
		.distance(function(d) { return (1/d.value)*20000;}))
		.force("charge", d3.forceManyBody())
		.force("center", d3.forceCenter(w / 2, h / 2));

	  var link = svg.append("g")
		.attr("class", "links")
		.selectAll("line")
		.data(links)
		.enter().append("line");
		//.attr("stroke-width", function(d) { return 0.1;/*Math.sqrt(d.value);*/ }); // this is a bit redunant, maybe we can use the stroke width to represent something else

	  // Topics - nodes
	  var nodes = response.topics;
	  var length = nodes.length;
	  var maxNodeValue = nodes[0].score; 
	  for (var idx = 0; idx < length; idx++)
	  {
	      if(nodes[idx].score > maxNodeValue)
		  maxNodeValue = nodes[idx].score;
	  }
          var fill = d3.scaleOrdinal().range(Math.random() >= 0.5 ? ['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c', '#ffffb2'] : ['#253494', '#2c7fb8', '#41b6c4', '#a1dab4', '#ffffcc']);
          //var radiusCoefficient = (3500 / w) * (maxNodeValue / 100);
	     
          node = svg.selectAll(".node")
	    .data(nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("cx", function(d) {
              return d.x;
            }).attr("cy", function(d) {
              return d.y;
            }).attr("r", 0).style("fill", function(d) {
              return assignColor(d);
            }).style("stroke", function(d, i) {
              return d3.rgb(d.color).darker(2);
            }).call(d3.drag()
		    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));  

	  simulation
            .nodes(nodes)
            .on("tick", ticked);
	    
	  simulation.force("link")
	    .links(links);
	    
	  function ticked() 
	  {
	      link
		  .attr("x1", function(d) { return d.source.x; })
		  .attr("y1", function(d) { return d.source.y; })
		  .attr("x2", function(d) { return d.target.x; })
		  .attr("y2", function(d) { return d.target.y; });

	      node
		  .attr("cx", function(d) { return d.x; })
		  .attr("cy", function(d) { return d.y; });
	  }
	    
          node.transition()
            .duration(1000)
            .attr("r", function(d) {
		return d.score*500; /// radiusCoefficient;
            });

          svg.style("opacity", 1e-6)
            .transition()
            .duration(1000)
            .style("opacity", 1);

          // Tooltip for circles
          $('circle').tipsy({
            gravity: 's',
            html: true,
            fade: false,
            offset: 0,
            fadeAnimationDuration: 200,
            title: function() {

              // Control for initial animation
              pauseInitialAnimation();

              // Bring to front
              var sel = d3.select(this);
              sel.moveToFront();

              var d = this.__data__;
              return '<div class="tipsy-topic">' + getWords(d.words) + '</div><span class="tipsy-time">' + pretifyDuration((d.score*10).toFixed(3)) + '</span>';
            }
          });
	    
	  // On click event for cicles
	  $('circle').click(function ()
	  {
	      var d = this.__data__;
	      drawDocs(d.docs)
	      drawTemporalTrend(d.years)
	  })

	  function drawDocs(docs)
	  {
	     // Clear docs area
	     var area = _("docs")
	     area.innerHTML = null;

	     listLength = docs.length;
	     // Consider randomising the documents displayed
	     for (var idx = 0; idx < listLength && idx < 6; idx++)
	     {
		 area.innerHTML += "<a href=\"" + docs[idx] + "\"> Document #" + idx + "</a>";
	     }
	      
	     $('#docs').prepend("<br>")
	     $('#docs').prepend("<span>" + "Documents about the topic"  + "</span>");
	  }

	  function drawTemporalTrend(years)
	  {
	      // Should either use integers or pass the whole date
	      var data = new Array();
	      for (var idx = 0; idx < years.length; idx++)
	      {
		  data.push(new Date(years[idx], 1, 1))
	      }

	      var area = _("tempHist");
	      // Clear draw area.
	      area.innerHTML = null;

	      // Create initial svg
              svg = d3.select("#tempHist").append("svg")
		  .attr("width", area.offsetWidth*2)
		  .attr("height",area.offsetHeight/3);
	      
	      var margin = {top: 10, right: 30, bottom: 30, left: 30};
	      var width  = svg.attr("width") - margin.left - margin.right;
	      var height = svg.attr("height") - margin.top - margin.bottom;
	      var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	      var x = d3.scaleTime()
	        .domain([new Date(2006, 1, 1), new Date(2017, 1, 1)]) //to update to start date, end date
		.rangeRound([0, width]);

	      var bins = d3.histogram()
		.domain(x.domain())
		.thresholds(x.ticks(d3.timeYear))
		(data);

	      var y = d3.scaleLinear()
		.domain([0, d3.max(bins, function(d) { return d.length; })])
		.range([height, 0]);

	      var bar = g.selectAll(".bar")
		 .data(bins)
		 .enter().append("g")
		 .attr("class", "bar")
		 .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; });

	      bar.append("rect")
		 .attr("x", 1)
		 .attr("width", x(bins[0].x1) - x(bins[0].x0) - 1)
		 .attr("height", function(d) { return height - y(d.length); });

	      if(data.length > 0)
	      {
		  g.append("g")
		      .attr("class", "axisBlue")
		      .attr("transform", "translate(0," + height + ")")
		      .call(d3.axisBottom(x));
		  g.append("g")
		      .attr("class", "axisBlue")
		      .call(d3.axisLeft(y));
	      }

	      $('#tempHist').prepend("<span>" + "Temporal trend for the topic"  + "</span>");
	  }


	 function dragstarted(d) {
	     if (!d3.event.active) simulation.alphaTarget(0.3).restart();
		d.fx = d.x;
		d.fy = d.y;
	    }

	 function dragged(d) {
		d.fx = d3.event.x;
		d.fy = d3.event.y;
	    }

	 function dragended(d) {
		if (!d3.event.active) simulation.alphaTarget(0);
		d.fx = null;
		d.fy = null;
	    } 
          //function tick(e) {
          //  var k = -0.1 * e.alpha;
          //  nodes.forEach(function(o, i) {
          //    o.y += k;
          //    o.x += k;
          //  });

          //  node.attr("cx", function(d) {
          //    return d.x;
          //  }).attr("cy", function(d) {
          //    return d.y;
          //  });
          //}

	  //function gravity(alpha) {
	  //	return function(d) {
	  //	    d.y += (d.cy - d.y) * alpha;
	  //	    d.x += (d.cx - d.x) * alpha;}
	  //};

          //function charge(d) {
          //  return -Math.pow(d.score / (radiusCoefficient * 2), 2.0) / 8;
          //}

          function assignColor(d) {
            //console.log(d.value, maxNodeValue, Math.floor(d.value / (maxNodeValue / 5)));
            d.color = fill(Math.floor(d.score / (maxNodeValue / 5)));
            return d.color;
          }

          function pretifyDuration(value) {
            if (value == 0) {
              return "";
            } else if (value > 59) {
              return Math.floor(value / 60) + " h. " + pretifyDuration(value % 60);
            } else {
              return value + " avg score."
            }
          }
	    
          function getWords(wordList) 
	  {
	      var listLength = wordList.length;
	      var output = ""
	      for (var idx = 0; idx < listLength; idx++)
	      {
		  output += wordList[idx] + ' '
	      }

	      return output
          }

        },
        remove: function() {

          node.transition()
            .duration(1000)
            .attr("r", 0)
            .remove();

          svg.style("opacity", 1)
            .transition()
            .duration(1000)
            .style("opacity", 1e-6)
            .remove()

	  getTopics();
        }
      }
    }
  }

  var currentChart = charts.bubbleChart();

  /**
   * UI element bindings
   */
  jQuery("#cancerBtn").click(function() {
    setKeyword(this, "cancer");
  });

  jQuery("#diabetesBtn").click(function() {
    setKeyword(this, "diabetes");
  });

  jQuery("#startDatepickerBtn").click(function() {
    toggleDatepicker("#startdatepicker", "#startDatepickerBtn", true);
  });
  jQuery("#endDatepickerBtn").click(function() {
    toggleDatepicker("#enddatepicker", "#endDatepickerBtn", false);
  });
})();

// TODO onresize
