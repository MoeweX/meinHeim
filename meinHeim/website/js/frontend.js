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
	
	//Load bvg information
	$.ajax({
		type: "GET",
		url: "/information_bvg",
	})
	.done(function(string) {
		$("#information_bvg").replaceWith(string);
	});
	
	//Load connected devices
	$.ajax({
		type: "GET",
		url: "/information_connected_devices",
	})
	.done(function(string) {
		$("#information_connected_devices").replaceWith(string);
	});
	
	//Load status of watering rule
	$.ajax({
		type: "GET",
		url: "/watering_rule_status",
	})
	.done(function(string) {
		$("#watering_rule_status").replaceWith('<li id="watering_rule_status">Bewässerungsregel (9 + 19 Uhr): ' + string + '</li>');
	});
	
	//Load status of desk lamp rule
	$.ajax({
		type: "GET",
		url: "/desk_lamb_rule_status",
	})
	.done(function(string) {
		$("#desk_lamb_rule_status").replaceWith('<li id="desk_lamb_rule_status">Schreibtischlampenregel: ' + string + '</li>');
	});
	
	//Load illuminance from BrickletAmbientLight(amm)
	$.ajax({
		type: "GET",
		url: "/information_amm_illuminance",
	})
	.done(function(string) {
		$("#information_amm_illuminance").replaceWith('<li id="information_amm_illuminance">Aktuelle Helligkeit (amm): ' + string + ' Lux</li>');
	});
	
	//Load distance from BrickletDistanceUS(iTm)
	$.ajax({
		type: "GET",
		url: "/information_iTm_distance",
	})
	.done(function(string) {
		$("#information_iTm_distance").replaceWith('<li id="information_iTm_distance">Aktuelle Entfernung (iTm): ' + string + '</li>');
	});
});