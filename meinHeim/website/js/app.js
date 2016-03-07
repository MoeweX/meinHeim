$(document).foundation();
$(document).ready(function() {

	//initialize timepicker
	$('#weckzeit').timepicker({ 'timeFormat': 'H:i' });
	$('#weckzeit').on("change", function() {
		$.ajax("/additional_information/set_wakeup_time?time=" + $('#weckzeit').val());
	});

	//Load old wakeup time
	$.ajax({
		type: "GET",
		url: "/additional_information/get_wakeup_time",
	})
	.done(function(string) {
		split = string.split(":");
		date = new Date()
		date.setHours(parseInt(split[0]));
		date.setMinutes(parseInt(split[1]));
		$('#weckzeit').timepicker(
			'setTime',
			date
		);
	});

	//Load socket list
	$.ajax({
		type: "GET",
		url: "/socket/list",
	})
	.done(function(string) {
		$("#sockets").append(string);
		$(document).foundation();
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
		$("#information_amm_illuminance").replaceWith(string);
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
