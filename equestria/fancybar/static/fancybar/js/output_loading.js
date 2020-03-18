function update_console_output() {
    var file_to_load = "http://localhost:8080/" + $("#file_to_load").text();
    if (file_to_load === "None") {
	setTimeout(update_console_output, 500);
	return;
    }
    $.get(file_to_load, function( content ) {
	//	alert(content);
	$('#console_output').html(content.replace(/\n/g, '<br />'));
    }, 'text'); 
    // execute every half a second
    setTimeout(update_console_output, 500);
}

$( document ).ready(function() {
    update_console_output();
});
