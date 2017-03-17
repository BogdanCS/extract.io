(function() {

  var LIMIT = 50;
    
  var LDA_NODE_SIZE= 1.5;
  var LLDA_NODE_SIZE = 10;
    
  var LDA_LINK_SIZE = 1.2;
  var DUAL_LINK_SIZE = 1.2;
  var LLDA_LINK_SIZE = 120;

  var keyword = "diabetes",
      model = "LDA",
      url,
      backupReqTimer,
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
      dateFormat: "dd/mm/yy",
      minDate: "01/01/1994", 
      onSelect: function(date) {
	toggleDatepicker("#startdatepicker", "#startDatepickerBtn", true);
	setDateText(true, "#startdatepicker", "startDateText");  
	//TODO - set minDate for endDatePicker to selected date here
      }
    });
    $("#enddatepicker").datepicker({
      dateFormat: "dd/mm/yy",
      minDate: "01/01/1994", 
      onSelect: function(date) {
	toggleDatepicker("#enddatepicker", "#endDatepickerBtn", false);
	setDateText(true, "#enddatepicker", "endDateText");  
	// TODO - have a submit button
	removeTopics();
      }
    });
    $("#startdatepicker").datepicker("setDate", "01/01/2001");
    $("#enddatepicker").datepicker("setDate", "01/01/2016");
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

    // create url
    var pathArray = document.URL.split('/');
    var requestType = model == "DUAL" ? "rpcNewSearchDualView" : "rpcNewSearch"
      
    url = pathArray[0] + "//" + pathArray[2] + "/" + requestType + "?keywords=" + keyword;

    startDate = Math.floor(jQuery("#startdatepicker").datepicker("getDate").getTime() / 1000);
    endDate = Math.floor(jQuery("#enddatepicker").datepicker("getDate").getTime() / 1000);
    url += "&start_date=" + startDate + "&end_date=" + endDate;
     
    url += "&limit=" + LIMIT;
    if (model != "DUAL")
	url += "&model=" + model;

    // make call
    var http_request = new XMLHttpRequest();
    http_request.open("GET", url, true);
    http_request.onreadystatechange = createHttpReady(http_request)
    http_request.send(null);

    pauseInitialAnimation();
    displayLoading();
  }

  function createHttpReady(http_request)
  {
      return function () {
      if (http_request.readyState == 4) {

        if (http_request.status == 200) {
          hideLoading();
          onSuccess(http_request.responseText);
        } 
        else {
	  console.log("Retrying..")
	  backupReqTimer = setTimeout(function() {
	      console.log(url)
	      var backup_request = new XMLHttpRequest();
	      backup_request.open("GET", url, true);
	      backup_request.onreadystatechange = createHttpReady(backup_request)
	      backup_request.send(null)}, 
		     60000);
        }
	  }}
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
    if (backupReqTimer != null)
    {
	clearTimeout(backupReqTimer)
    }
      
    if (currentChart != null)
    {
	currentChart.remove();
    }
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
        /*setTimeout(function() {
          $(list[index]).mouseout();
          activeTipsy = null;
          startInitialAnimation(list, index + 1);
        }, 5000);*/
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
    
  function setModel(node, r) {
    if (model != r) {
      model = r;
      removeTopics();

      // change style
      changeModelBtnStyle(node);
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
    $('#regions a').removeClass('current');
    $(node).addClass('current');
  }
    
  function changeModelBtnStyle(node) {
    $('#models a').removeClass('current');
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
	linkedByIdx,
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
		.distance(function(d) { 
		    if (model == "LDA")
		    {
			console.log(d.value*LDA_LINK_SIZE)
			return (1/(d.value*LDA_LINK_SIZE))*20000;
	            }
		    else if (model == "LLDA")
		    {
			console.log("weird")
			console.log(d.value*LLDA_LINK_SIZE)
			return (1/(d.value*LLDA_LINK_SIZE))*20000;
		    }
		    else 
			return (1/(d.value*DUAL_LINK_SIZE))*20000;
		}))
		.force("charge", d3.forceManyBody())
		.force("center", d3.forceCenter(w / 2, h / 2));

	  var link = svg.append("g")
		.attr("class", "links")
		.selectAll("line")
		.data(links)
		.enter().append("line");
		//.attr("stroke-width", function(d) { return 0.1;/*Math.sqrt(d.value);*/ }); // this is a bit redunant, maybe we can use the stroke width to represent something else
	    
	  // Create this index for later use when highlighting neighbouring nodes
	  linkedByIdx = {};
	  links.forEach(function(d) {
	      linkedByIdx[d.source + "," + d.target] = 1;
	  });
	  console.log(linkedByIdx)

	  // Topics - nodes
	  var nodes = Object.keys(response.topics).map(function(key){
	      return response.topics[key];
	  });
	  var length = nodes.length;
	  var maxNodeValue = nodes[0].score; 
	  for (var idx = 0; idx < length; idx++)
	  {
	      if(nodes[idx].score > maxNodeValue)
		  maxNodeValue = nodes[idx].score;
	  }
          var fill = d3.scaleOrdinal().range(['#253494', '#2c7fb8', '#41b6c4', '#a1dab4', '#ffffcc']);
	  var fillLLDA = d3.scaleOrdinal().range(['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c', '#ffffb2'])
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
		if (model == "LLDA")
		{
		    return d.score*500*LLDA_NODE_SIZE;
		}
		else if (model == "DUAL" && d.uid < 0)
		{
		    return d.score*500*(LLDA_NODE_SIZE*0.8);
		}

		return d.score*500*LDA_NODE_SIZE; /// radiusCoefficient;
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
              return '<div class="tipsy-topic">' + getWords(d.nameTokens) + '</div><span class="tipsy-time">' + pretifyDuration((d.score*10).toFixed(3)) + '</span>';
            }
          });
	    
	  // On click event for cicles
	  $('circle').click(function ()
	  {
	      var d = this.__data__;
	      
	      if (model != "DUAL")
	      {
		  drawDocs(d.docs, d.wordsProb, d.nameTokens)
		  if(d.years.length > 0)
	     	      drawTemporalTrend(d.years, d.maxYearCount, "tempHist")
		  else
		  {
	     	      var area = _('tempHist');
	     	      // Clear draw area.
	     	      area.innerHTML = null;
	     	      $('#tempHist').prepend("<span>Not enough data</span>");
		  }
		  if(d.forecastYears.length > 0)
	     	      drawTemporalTrend(d.forecastYears, d.maxYearCount, "forTempHist")
		  else
		  {
	     	      var area = _('forTempHist');
	     	      // Clear draw area.
	     	      area.innerHTML = null;
	     	      $('#forTempHist').prepend("<span>Not enough data to forecast</span>");
		  }
	      }
	      highlightAdjacent(d, 0.1) // argument is opacity
	  })
	    
	  function neighboring(a, b) {
	    return linkedByIdx[a.uid + "," + b.uid] || linkedByIdx[b.uid + "," + a.uid];
	  }

	  function highlightAdjacent(d, opacity)
	  {
	      // Fade out everything
	      svg.selectAll("circle, line").style("opacity", opacity); // to use fill and stroke opacity
	      
	      // Highlight adjacent links
	      link.style("opacity", function(o) {
		  return o.source === d || o.target === d ? 1 : opacity;
	      });

	      node.style("opacity", function(o) {
		  return d.uid == o.uid || neighboring(d, o) ? 1 : opacity;
	      });
	  }

	  function createTopicTitle(tokens)
	  {
	      var topicTitle = ""
	      for (var jdx = 0; jdx < tokens.length; jdx++)
	      {
		  topicTitle += tokens[jdx] + " "
	      }
	      titleLength = topicTitle.length < 11 ? doc.title.length : 11 
	      return topicTitle.slice(0,titleLength) + "..."
	  }
	    
	  function createModalNew(pmid, doc)
	  {
	      var modal = "<div id=\"mod"+ pmid +"\" class=\"modal\">" +
		          "<div class=\"modal-content\">" +
                          "<span class=\"close\" id=clo"+ pmid +">&times;</span>" +
                          "<p><b>" + doc.title + "</b></p>"
	      
	      var words = doc.uiText.split(" ")
	      
	      modal += "<p>"
	      for (var idx = 0; idx < doc.topicList.length; idx++)
	      {
		  var topicId = doc.topicList[idx]
		  modal += "<a class=\"modalReg\" id=\"top" + topicId + "\">"
		  modal += createTopicTitle(response.topics[topicId].nameTokens) + "</a>"
		  
		  topId = "#top" + topicId
		  $("#docs").on({
		      mouseenter: function(e) {
			  $(".snip").css({opacity: 0.2})
			  var curCls = ".sniptop" + (this.id).slice(3,(this.id).length)
			  $(curCls).css({opacity: 1.0})
		      },
		      mouseleave: function(e) {
			  $(".snip").css({opacity: 1.0})
		      }
		  }, topId)
		  
	      }

	      modal += "</p><p>"

	      for (var idx = 0; idx < words.length; idx++)
	      {
		  modal += "<span class=\"snip "
		  
		  for (var jdx = 0; jdx < doc.topicList.length; jdx++)
		  {
		      var topicId = doc.topicList[jdx]
		      if (idx >= doc.summaries[topicId][0] &&
			  idx <= doc.summaries[topicId][1])
		      {
			  modal += " sniptop" + topicId
		      }
		  }
		  
		  modal += "\">" + words[idx] + " " + "</span>"
	      }
	      
              modal += "</p>" +
	               "</div>" +
                       "</div>"

	      return modal
	  }

	  function createModal(pmid, doc)
	  {
	      var modal = "<div id=\"mod"+ pmid +"\" class=\"modal\">" +
		          "<div class=\"modal-content\">" +
                          "<span class=\"close\" id=clo"+ pmid +">&times;</span>" +
                          "<p><b>" + doc.title + "</b></p>"
	      
	      // Assign each word (where possible) to a topic
	      var wordTopicDict = {}
	      var words = doc.uiText.split(" ")
	      for (var idx = 0; idx < words.length; idx++)
	      {
		  wordTopicDict[words[idx].replace(/\W/g, '').toLowerCase()] = {topicId: "", 
									        prob: 0.0}
	      }
 
	      modal += "<p>"
	      for (var idx = 0; idx < doc.topicList.length; idx++)
	      {
		  var topicId = doc.topicList[idx]
		  modal += "<a class=\"region\" id=\"top" + topicId + "\">"
		  modal += createTopicTitle(response.topics[topicId].nameTokens) + "</a>"
		  
		  topId = "#top" + topicId
		  $("#docs").on({
		      mouseenter: function(e) {
			  $(this).attr("class", "current")
			  $(".word").css({opacity: 0.0})
			  var curCls = ".wtop" + (this.id).slice(3,(this.id).length)
			  $(curCls).css({opacity: 1.0})
			  // These are stop words or words not assigned to a particular topic
			  $(".wtop").css({opacity: 0.3})
		      },
		      mouseleave: function(e) {
			  $(this).attr("class", "region")
			  $(".word").css({opacity: 1.0})
		      }
		  }, topId)
		  
		  // Check the topic words and match them with the words in doc text
		  for (var jdx = 0; jdx < response.topics[topicId].wordsProb.length; jdx++)
		  {
		      word = response.topics[topicId].wordsProb[jdx][0]
		      prob = response.topics[topicId].wordsProb[jdx][1]
		      // Alternative here - add more classes instead of choosing just one
		      // Considering reducing WORDS_PER_TOPIC and have more topics per DOC
		      if ((word in wordTopicDict) &&
			  response.topics[topicId].score * prob > wordTopicDict[word].prob)
		      {
			  wordTopicDict[word].topicId = topicId
			  wordTopicDict[word].prob = response.topics[topicId].score * prob
		      }
		  }
	      }

	      modal += "</p><p>"

	      for (var idx = 0; idx < words.length; idx++)
	      {
		  modal += "<span class=\"word wtop"
		  
		  key = words[idx].replace(/\W/g, '').toLowerCase()
		  if (key in wordTopicDict)
		  {
		      modal += wordTopicDict[key].topicId
		  }
		  
		  modal += "\">" + words[idx] + " " + "</span>"
	      }
	      
              modal += "</p>" +
	               "</div>" +
                       "</div>"

	      return modal
	  }

	  function drawDocs(docs, topicWords, topicNameTokens)
	  {
	     // Clear docs area
	     var area = _("docs")
	     area.innerHTML = null;

	     listLength = docs.length;
	     for (var idx = 0; idx < listLength && idx < 5; idx++){
		     pmid = docs[idx]
		     doc = response.docs[pmid]
		     titleLength = doc.title.length < 21 ? doc.title.length : 21 
		     title = doc.title.slice(0,titleLength) + "..."
		     area.innerHTML += "<button class=\"region\" id=\"but"+pmid+"\">"+title+"</button>"
		     area.innerHTML += createModalNew(pmid, doc)
		 
		     var btnid = "#but" + pmid
		     $("#docs").on("click", btnid, function(e) {
			 id = "mod" + (this.id).slice(3,(this.id).length)
			 document.getElementById(id).style.display = "block";
		     })
		     
		     // When the user clicks on <span> (x), close the modal
		     var spanid = "#clo" + pmid
		     $("#docs").on("click", spanid, function(e) {
			 id = "mod" + (this.id).slice(3,(this.id).length)
			 document.getElementById(id).style.display = "none";
		     })
	     }
	      
	     $('#docs').prepend("<br>")
	     $('#docs').prepend("<span>" + "Documents about the topic"  + "</span>");
	  }

	  function drawTemporalTrend(years, maxCount, areaId)
	  {
	      // Should either use integers or pass the whole date
	      var data = new Array();
	      var startDate = new Date(2050,1,1)
	      var endDate = new Date(1960,1,1)
	      for (var idx = 0; idx < years.length; idx++)
	      {
		  //tokens = years[idx].split('-')
		  //date = new Date(tokens[0], tokens[1], 1)
		  date = new Date(years[idx],1,1)
		  if(date < startDate)
		      startDate = date
		  if(date > endDate)
		      endDate = date
		  data.push(date)
	      }

	      var area = _(areaId);
	      // Clear draw area.
	      area.innerHTML = null;

	      // Create initial svg
              svg = d3.select("#" + areaId).append("svg")
		  .attr("width", area.offsetWidth*2)
		  .attr("height",area.offsetHeight/3);
	      
	      var margin = {top: 10, right: 30, bottom: 30, left: 40};
	      var width  = svg.attr("width") - margin.left - margin.right;
	      var height = svg.attr("height") - margin.top - margin.bottom;
	      var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	      minEndDate = new Date(startDate.getFullYear() + 5, 1, 1)
	      endDate = minEndDate.getTime() < endDate.getTime() ? endDate : minEndDate
	      var x = d3.scaleTime()
	        .domain([startDate, endDate]) 
		.rangeRound([0, width]);

	      var bins = d3.histogram()
		.domain(x.domain())
		.thresholds(x.ticks(d3.timeYear))
		(data);

	      //var max = d3.max(bins, function(d) { return d.length; })
	      var y = d3.scaleLinear()
		.domain([0, maxCount])
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

	      title = ""
	      if (areaId == "tempHist")
		  title = "Temporal trend for topic"
	      $('#' + areaId).prepend("<span>" + title  + "</span>");
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

          function assignColor(d) {
	    if(d.uid >= 0)
		d.color = fill(Math.floor(d.score / (maxNodeValue / 5)));
	    else
		d.color = fillLLDA(Math.floor(d.score / (maxNodeValue / 5)));
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

	  if (node != null)
          node.transition()
            .duration(1000)
            .attr("r", 0)
            .remove();

	  if (svg != null)
          svg.style("opacity", 1)
            .transition()
            .duration(1000)
            .style("opacity", 1e-6)
            .remove()

	  // Clear docs area
	  var area = _("docs")
	  area.innerHTML = null;

	  var area = _("tempHist");
	  // Clear draw area.
	  area.innerHTML = null;
	  var area = _("forTempHist");
	  // Clear draw area.
	  area.innerHTML = null;
	    
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

  jQuery("#ldaBtn").click(function() {
    setModel(this, "LDA");
  });
  jQuery("#lldaBtn").click(function() {
    setModel(this, "LLDA");
  });
  jQuery("#dualBtn").click(function() {
    setModel(this, "DUAL");
  });

  jQuery("#startDatepickerBtn").click(function() {
    toggleDatepicker("#startdatepicker", "#startDatepickerBtn", true);
  });
  jQuery("#endDatepickerBtn").click(function() {
    toggleDatepicker("#enddatepicker", "#endDatepickerBtn", false);
  });
})();

// TODO onresize
