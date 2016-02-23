$(document).ready(function() {

	//Load socket list
	$.ajax({
		type: "GET",
		url: "/socket/list",
	})
	.done(function(string) {
		$("#sockets").append(string);
	});

	//Load bvg information
	$.ajax({
		type: "GET",
		url: "/additional_information/bvg",
	})
	.done(function(string) {
		$("#information_bvg").append(string);
	});

	//Load connected devices
	$.ajax({
		type: "GET",
		url: "/additional_information/connected_devices",
	})
	.done(function(string) {
		$("#information_connected_devices").append(string);
	});

	//Load illuminance from BrickletAmbientLight(amm)
	$.ajax({
		type: "GET",
		url: "/additional_information/amm_illuminance",
	})
	.done(function(string) {
		$("#information_amm_illuminance").replaceWith('<li id="information_amm_illuminance">Aktuelle Helligkeit (amm): ' + string + ' Lux</li>');
	});

	//Load distance from BrickletDistanceUS(iTm)
	$.ajax({
		type: "GET",
		url: "/additional_information/iTm_distance",
	})
	.done(function(string) {
		$("#information_iTm_distance").replaceWith('<li id="information_iTm_distance">Aktuelle Entfernung (iTm): ' + string + '</li>');
	});

	//Load rules
	$.ajax({
		type: "GET",
		url: "/rule/list",
	})
	.done(function(string) {
		$("#rules").append(string);
	});

});
