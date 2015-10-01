$(document).ready(function() {
	
	//Button pressed
	$(".button").click(function(e) {
		$.ajax({
			type: "GET",
			url: "/button_"+$(this).attr("val"),
		})
		.done(function(string) {
			console.log(string);
		});
	});
	
	//Load connected devices
	$.ajax({
		type: "GET",
		url: "/connectedDevices",
	})
	.done(function(string) {
		$("#connectedDevices").replaceWith(string);
	});
});