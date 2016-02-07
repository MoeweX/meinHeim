$(document).ready(function() {
	
	//Button pressed
	$(".button").click(function(e) {
		console.log("Button clicked");
		//TODO Dimmer
		$.ajax({
			type: "GET",
			url: "/socket/nXN",
			data:{
				address: $(this).attr("address"), 
				unit: $(this).attr("unit"), 
				state: $(this).attr("state")
			}
		})
		.done(function(string) {
			console.log(string);
		});
	});
	
	//Load bvg information
	$.ajax({
		type: "GET",
		url: "/additional_information/bvg",
	})
	.done(function(string) {
		$("#information_bvg").replaceWith(string);
	});
	
	//Load connected devices
	$.ajax({
		type: "GET",
		url: "/additional_information/connected_devices",
	})
	.done(function(string) {
		$("#information_connected_devices").replaceWith(string);
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
	
	//Load status of watering rule
	$.ajax({
		type: "GET",
		url: "/rule/watering_rule_status",
	})
	.done(function(string) {
		$("#watering_rule_status").replaceWith('<li id="watering_rule_status">Bewässerungsregel (9 + 19 Uhr): ' + string + '</li>');
	});
	
	//Load status of balkon rule
	$.ajax({
		type: "GET",
		url: "/rule/balkon_rule_status",
	})
	.done(function(string) {
		$("#balkon_rule_status").replaceWith('<li id="balkon_rule_status">Balkonbeleuchtungsregel (17 - 22 Uhr): ' + string + '</li>');
	});
	
	//Load status of desk lamp rule
	$.ajax({
		type: "GET",
		url: "/rule/desk_lamb_rule_status",
	})
	.done(function(string) {
		$("#desk_lamb_rule_status").replaceWith('<li id="desk_lamb_rule_status">Schreibtischlampenregel: ' + string + '</li>');
	});
	
});