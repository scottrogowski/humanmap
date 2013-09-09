"use strict";

//Map icon maker
//eval(function(p,a,c,k,e,r){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('3 w={};w.1J=K(h){3 f=h.14||A;3 b=h.1f||A;3 e=h.Q||"#17";3 a=h.13||"#G";3 g=h.20||"#1W";3 d="L://z.N.S.P/z?O=1A";3 j=d+"&T="+f+"x"+b+"&V="+g.4("#","")+","+e.4("#","")+","+a.4("#","")+"&F=.E";3 c=u Z(X);c.W=j;c.10=u B(f,b);c.15=u B(y.1d(f*1.6),b);c.1a=u H(f/2,b);c.19=u H(f/2,y.1d(b/12));c.18=j+"&I=J";c.1j=j+"&C=M,s,1g"+"&I=J";j=d+"&T="+f+"x"+b+"&V="+g.4("#","")+","+e.4("#","")+","+a.4("#","");c.1l=j+"&C=a,s,1o&F=.E";c.v=[f/2,b,(7/16)*f,(5/8)*b,(5/16)*f,(7/16)*b,(7/A)*f,(5/16)*b,(5/16)*f,(1/8)*b,(1/2)*f,0,(11/16)*f,(1/8)*b,(25/A)*f,(5/16)*b,(11/16)*f,(7/16)*b,(9/16)*f,(5/8)*b];1k(3 i=0;i<c.v.1Z;i++){c.v[i]=Y(c.v[i])}D c};w.1V=K(k){3 h=k.14||A;3 j=k.1f||A;3 d=k.Q||"#17";3 i=k.1T||"#G";3 m=w.U(k.1i)||"";3 c=k.1h||"#G";3 l=k.1S||0;3 s=k.1R||"1e";3 f=(s==="1e")?"1Q":"1P";3 t="L://z.N.S.P/z?O="+f;3 n=t+"&T="+h+"x"+j+"&V="+d.4("#","")+","+i.4("#","")+"1O,1c"+"&1b="+m+"&1M="+c.4("#","")+","+l;3 e=u Z(X);e.W=n+"&C=M,s,1K"+"&F=.E";e.10=u B(h,j);e.15=u B(0,0);e.1a=u H(h/2,j/2);e.19=u H(h/2,j/2);e.18=n+"&I=J";e.1j=n+"&C=M,s,1g"+"&I=J";e.1l=n+"&C=a,s,1c&F=.E";e.v=[];R(f==="1I"){e.v=[0,0,h,0,h,j,0,j]}1H{3 o=8;3 r=1G/o;3 b=y.1F(h,j)/2;1k(3 a=0;a<(o+1);a++){3 g=r*a*(y.1E/1D);3 p=b+b*y.1B(g);3 q=b+b*y.1z(g);e.v.1L(Y(p),Y(q))}}D e};w.1y=K(k){3 j=k.Q||"#1N";3 b=k.13||"#G";3 f=k.1x||"#1w";3 a=k.1v||"#1u";3 e=w.U(k.1i)||"";3 d=k.1h||"#G";3 i=k.1t||1s;3 c=(i)?"1r":"1U";3 h="L://z.N.S.P/z?O=d&1q=1p&1b=";3 l=h+c+"\'i\\\\"+"\'["+e+"\'-2\'f\\\\"+"1X\'a\\\\]"+"h\\\\]o\\\\"+j.4("#","")+"\'1Y\\\\"+d.4("#","")+"\'1n\\\\"+b.4("#","")+"\'1m\\\\";R(i){l+=f.4("#","")+"\'1C\\\\"+a.4("#","")+"\'22\\\\"}l+="2a\'f\\\\";3 g=u Z(X);g.W=l+"&F=.E";g.10=(i)?u B(23,28):u B(21,27);D g};w.U=K(a){R(a===26){D 24}a=a.4(/@/,"@@");a=a.4(/\\\\/,"@\\\\");a=a.4(/\'/,"@\'");a=a.4(/\\[/,"@[");a=a.4(/\\]/,"@]");D 29(a)};',62,135,'|||var|replace||||||||||||||||||||||||||new|imageMap|MapIconMaker||Math|chart|32|GSize|chf|return|png|ext|000000|GPoint|chof|gif|function|http|bg|apis|cht|com|primaryColor|if|google|chs|escapeUserText_|chco|image|G_DEFAULT_ICON|parseInt|GIcon|iconSize|||strokeColor|width|shadowSize||ff0000|printImage|infoWindowAnchor|iconAnchor|chl|ffffff01|floor|circle|height|ECECD8|labelColor|label|mozPrintImage|for|transparent|eC|tC|ffffff11|mapsapi|chdp|pin_star|false|addStar|0000FF|starStrokeColor|FFFF00|starPrimaryColor|createLabeledMarkerIcon|sin|mm|cos||180|PI|min|360|else|roundrect|createMarkerIcon|00000000|push|chx|DA7187|ff|itr|it|shape|labelSize|shadowColor|pin|createFlatIcon|ffffff|hv|fC|length|cornerColor||0C||null||undefined|34|39|encodeURIComponent|Lauto'.split('|'),0,{}))

less = {
	env: "development", // or "production"
	dumpLineNumbers: "all",
}

google.maps.Map.prototype.clearMarkers = function() {
    if (typeof(this.markers) != 'undefined') {
	    for(var i=0; i<this.markers.length; i++) {
	        this.markers[i].setMap(null);
		}
	    this.markers = new Array();
	}
}

var markers;

$(document).ready(function(){
	setGlobalVars();
	initMap();
	filterYears(-250,500);
	initSlider(-250,500);
	})

function setGlobalVars() {
	window.startColor = RGB('bb2201');
	window.endColor = RGB('91ff42');
	window.startYear = -1500;
	window.endYear = 2013;
	window.totalYears = (endYear-startYear)*1.0;
}

function initMap() {
	/*
	Initialize the map to be centered on the parthenon
	*/
	console.log('Init Map');
	var mapOptions = {
		center: new google.maps.LatLng(37.9715, 23.7267)
		,mapTypeId: google.maps.MapTypeId.ROADMAP
		,mapTypeControl: false
		,zoomControlOptions: {style:google.maps.ZoomControlStyle.LARGE}
		,zoom:3
		};
	window.map = new google.maps.Map($("#map")[0], mapOptions);
}

function clearMarkers() {
	/*
	Remove all the markers from the map when using the slider
	*/
	if (typeof markers != 'undefined') { 
		console.log("Clearing markers");
		for (var i=0; i<markers.length; i++) {
			markers[i].setMap(null);
		}
	}
	markers = [];
}


function placeMarkers(json) {
	/*
	Generate map markers and place them on the map
	*/
	console.log("placing "+json.length.toString()+' markers');
	console.log(json[0]);
	clearMarkers();
	window.currentJSON = json
	for (var i=0; i<json.length; i++) {
		var coord = new google.maps.LatLng(json[i]['coordinates']['lat'],json[i]['coordinates']['lng'])
		/*
		var yearInt = json[i]['startDate']['year']
		if (yearInt<0)
			var year = (-1*yearInt).toString()+' BCE'
		else
			var year = yearInt.toString()

		var yearFill = Array(year.length).join('0')
		*/

		var yearColor = calculateHexColor(json[i]['startDate']['year']);

		markers[i] = new google.maps.Marker({
				map: map
				,position: coord
				,icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%7C"+yearColor+"%7C000000"
			})
		markers[i].i = i;
		google.maps.event.addListener(markers[i], 'click', function() {
			var title = json[this.i]['title'];
			var slug = title.replace(' ','_');
			var paragraph = json[this.i]['firstParagraph'];
			var content = "<a class='articleTitle' href='http://en.wikipedia.org/wiki/"+slug+"'>"+title+"</a>"+paragraph;

			if (typeof(window.infowindow) != 'undefined')
				window.infowindow.close()
    		window.infowindow = new google.maps.InfoWindow({
    			content:content 
				});		
			window.infowindow.open(map,this);
		});
	}
}



function initSlider(from,to) {
	/*
	Init a new slider which will display the year on top when dragged and will call filterYears when dropped
	*/
	slider = $('#slider').slider({
		orientation: "horizontal",
		range: true,
		min: startYear,
		max: endYear,
		values: [ from, to ],
		stop: function(event, ui) {
			$('.dial').hide()
			filterYears(ui.values[0],ui.values[1])
		},
		slide: function(event, ui) {
			console.log(event)

			if (ui.value < 0)
				var year = (-1*ui.value).toString()+" BCE"
			else
				var year = ui.value.toString()

			if (ui.value == ui.values[0])
				$('#fromYear').show().text(year)
			else 
				$('#toYear').show().text(year)
		}
	})
	$('.ui-slider-handle').eq(0).append('<div class="dial" id="fromYear"></div>')
	$('.ui-slider-handle').eq(1).append('<div class="dial" id="toYear"></div>')
}

function filterYears(from,to) {
	/*
	Filter the JSON from 'from' to 'to'
	Called when the slider stops
	*/
	var json = []	
	for (var i=0;i<allJSON.length;i++) {
		if (from<=allJSON[i]['startDate']['year'] && allJSON[i]['startDate']['year']<=to) {
			json.push(allJSON[i]);
		}
	}
	placeMarkers(json);
}

function RGB(str) {
	/*
	A representation of RGB used to generate hex colors
	*/
	var self = this;
	var rInt = parseInt(str.substring(0,2),16);
	var gInt = parseInt(str.substring(2,4),16);
	var bInt = parseInt(str.substring(4,6),16);

	var percentRGBString = function(other,percent) {
		var newR = Math.floor((this.rInt-other.rInt)*percent+other.rInt).toString(16);
		var newG = Math.floor((this.gInt-other.gInt)*percent+other.gInt).toString(16);
		var newB = Math.floor((this.bInt-other.bInt)*percent+other.bInt).toString(16);
		newR = ('0'+newR).substr(-2);
		newG = ('0'+newG).substr(-2);
		newB = ('0'+newB).substr(-2);
		return newR+newG+newB;
		}
	return {
		rInt:rInt,
		gInt:gInt,
		bInt:bInt,
		percentRGBString:percentRGBString
	}
}

function calculateHexColor(year) {
	return endColor.percentRGBString(startColor,(year-startYear)/totalYears);
}

//Facebook nonsense
