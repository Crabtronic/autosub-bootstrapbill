// Javascript for test buttons used from Sickbeard source, Thanks. Project can be found here: https://github.com/midgetspy/Sick-Beard

jQuery.fn.dataTableExt.oSort['euro-date-pre']  = function(a,b) {
	if ($.trim(a) != '') {
            var frDatea = $.trim(a).split(' ');
            var frTimea = frDatea[1].split(':');
            var frDatea2 = frDatea[0].split('-');
            var x = (frDatea2[2] + frDatea2[1] + frDatea2[0] + frTimea[0] + frTimea[1] + frTimea[2]) * 1;
        } else {
            var x = 10000000000000; // = l'an 1000 ...
        } 
    return x;
};

jQuery.fn.dataTableExt.oSort['euro-date-asc']  = function(a,b) {
	return a - b;
};

jQuery.fn.dataTableExt.oSort['euro-date-desc'] = function(a,b) {
	return b - a;
};

$(document).ready(function () {

	$('#wanted').dataTable({ 
		"bStateSave": true,
		"fnStateSave": function (oSettings, oData) { localStorage.setItem( 'AutoSub-Wanted', JSON.stringify(oData) ); },
		"fnStateLoad": function (oSettings) { return JSON.parse( localStorage.getItem('AutoSub-Wanted') ); },
		"iCookieDuration": 60*60*24*365,
		"bLengthChange": true,
		"bPaginate": true,
		"aLengthMenu": [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
		"aaSorting": [ [ 0, "asc"], [ 1, "asc"], [ 2, "asc"] ],
		"aoColumnDefs": [ { "aDataSort": [ 0, 1, 2 ], "aTargets": [ 0 ] }, { "sType": "euro-date", "aTargets": [ 8 ] }, { "bSortable": false, "aTargets": [ 9 ] } ]
	});

	$('#downloaded').dataTable({ 
		"bStateSave": true,
		"fnStateSave": function (oSettings, oData) { localStorage.setItem( 'AutoSub-Downloaded', JSON.stringify(oData) ); },
		"fnStateLoad": function (oSettings) { return JSON.parse( localStorage.getItem('AutoSub-Downloaded') ); },
		"iCookieDuration": 60*60*24*365,
		"bLengthChange": true,
		"bPaginate": true,
		"aLengthMenu": [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
		"aaSorting": [ [ 8, "desc" ] ],
		"aoColumnDefs": [ { "aDataSort": [ 0, 1, 2 ], "aTargets": [ 0 ] }, { "sType": "euro-date", "aTargets": [ 8 ] }, { "bSortable": false, "aTargets": [ 9 ] } ]
	});
	
    $('#testMail').click(function () {
        $('#testMail-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Mail...</span>');
        var mailsrv = $("#mailsrv").val();
		var mailfromaddr = $("#mailfromaddr").val();
		var mailtoaddr = $("#mailtoaddr").val();
		var mailusername = $("#mailusername").val();
		var mailpassword = $("#mailpassword").val();
		var mailsubject = $("#mailsubject").val();
		var mailencryption = $("#mailencryption").val();
		var mailauth = $("#mailauth").val();
		$.get(autosubRoot + "/config/testMail", {'mailsrv': mailsrv, 'mailfromaddr': mailfromaddr, 'mailtoaddr': mailtoaddr, 'mailusername': mailusername, 'mailpassword': mailpassword, 'mailsubject': mailsubject, 'mailencryption': mailencryption, 'mailauth': mailauth},
			function (data) { $('#testMail-result').html(data); });
    });

    $('#testTwitter').click(function () {
        $('#testTwitter-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Twitter...</span>');
        var twitterkey = $("#twitterkey").val();
		var twittersecret = $("#twittersecret").val();
		$.get(autosubRoot + "/config/testTwitter", {'twitterkey': twitterkey, 'twittersecret': twittersecret},
			function (data) { $('#testTwitter-result').html(data); });
    });
    
    $('#testPushalot').click(function () {
        $('#testPushalot-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Pushalot...</span>');
        var pushalotapi = $("#pushalotapi").val();
		$.get(autosubRoot + "/config/testPushalot", {'pushalotapi': pushalotapi},
			function (data) { $('#testPushalot-result').html(data); });
    });
	
	$('#testNotifyMyAndroid').click(function () {
        $('#testNotifyMyAndroid-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Notify My Android...</span>');
        var nmaapi = $("#nmaapi").val();
		var nmapriority = $("#nmapriority").val();
		$.get(autosubRoot + "/config/testNotifyMyAndroid", {'nmaapi': nmaapi, 'nmapriority': nmapriority},
			function (data) { $('#testNotifyMyAndroid-result').html(data); });
    });
	
	$('#testPushover').click(function () {
        $('#testPushover-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Pushover...</span>');
        var pushoverapi = $("#pushoverapi").val();
		$.get(autosubRoot + "/config/testPushover", {'pushoverapi': pushoverapi},
			function (data) { $('#testPushover-result').html(data); });
    });
	
	$('#testGrowl').click(function () {
        $('#testGrowl-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Growl...</span>');
        var growlhost = $("#growlhost").val();
		var growlport = $("#growlport").val();
		var growlpass = $("#growlpass").val();
		$.get(autosubRoot + "/config/testGrowl", {'growlhost': growlhost, 'growlport': growlport, 'growlpass': growlpass},
			function (data) { $('#testGrowl-result').html(data); });
    });
	
	$('#testProwl').click(function () {
        $('#testProwl-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Prowl...</span>');
        var prowlapi = $("#prowlapi").val();
		var prowlpriority = $("#prowlpriority").val();
		$.get(autosubRoot + "/config/testProwl", {'prowlapi': prowlapi, 'prowlpriority': prowlpriority},
			function (data) { $('#testProwl-result').html(data); });
    });
	
	$('#testBoxcar2').click(function () {
        $('#testBoxcar2-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Boxcar2...</span>');
        var boxcar2token = $("#boxcar2token").val();
		$.get(autosubRoot + "/config/testBoxcar2", {'boxcar2token': boxcar2token},
			function (data) { $('#testBoxcar2-result').html(data); });
    });
	
	$('#testAddic7ed').click(function () {
        $('#testAddic7ed-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Addic7ed login...</span>');
        var addic7eduser = $("#addic7eduser").val();
		var addic7edpasswd = $("#addic7edpasswd").val();
		$.get(autosubRoot + "/config/testAddic7ed", {'addic7eduser': addic7eduser, 'addic7edpasswd': addic7edpasswd},
			function (data) { $('#testAddic7ed-result').html(data); });
    });
	
	$('#testPlex').click(function () {
        $('#testPlex-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Testing Plex Media Server...</span>');
        var plexserverhost = $("#plexserverhost").val();
		var plexserverport = $("#plexserverport").val();
		$.get(autosubRoot + "/config/testPlex", {'plexserverhost': plexserverhost, 'plexserverport': plexserverport},
			function (data) { $('#testPlex-result').html(data); });
    });
	
	$('#RetrieveAddic7edCount').click(function () {
        $('#Addic7edCount-result').html('<span><img src="' + autosubRoot + '/images/loading16.gif"> Retrieving Addic7ed download count, this will take a minute...</span>');
		$.get(autosubRoot + "/config/RetrieveAddic7edCount",
			function (data) { $('#Addic7edCount-result').html(data); });
    });
	
	// Code to display the tooltip and popover.
	$("a").tooltip()
	$("span").popover()
	
	$("span").on('shown.bs.popover', function () {
		$("span").not(this).popover('hide');
	});
		
	// Code to hide/show the notification fields.
	$(".enabler option:selected").each(function () {
		if ($(this).val() == "False") {
			$('#content_' + $(this).parent().attr("id")).hide();
		}
	});

	$(".enabler").change(function () {
 		var dropdown = $(this);
		$(this).children("option:selected").each(function() {
 			if ($(this).val() == "True") {
 				$('#content_' + dropdown.attr("id")).show();
 			}
 			if ($(this).val() == "False") {
 				$('#content_' + dropdown.attr("id")).hide();
 			}
 		});
 	});
	
	$(".enableraddic7ed option:selected").each(function () {
		if ($(this).val() == "None") {
			$('#content_' + $(this).parent().attr("id")).hide();
		}
	});

	$(".enableraddic7ed").change(function () {
 		var dropdown = $(this);
		$(this).children("option:selected").each(function() {
 			if ($(this).val() == "None") {
 				$('#content_' + dropdown.attr("id")).hide();
 			}
			else {
				$('#content_' + dropdown.attr("id")).show();
			}
 		});
 	});

});

// Code to sort the Wanted/Downloaded tables on the Home page.
var lines = $(".overview");
var elems = $(".overview div");
var numElems = elems.length;
for (var index = 1; index <= elems.length; index++) {
	var elemId = "Display" + index;
	var containerIndex = parseInt((index - 1) / 4);
	var container = lines[containerIndex];
	var elem = document.getElementById(elemId);
	elem.parentNode.removeChild(elem);
	container.appendChild(elem);
}
