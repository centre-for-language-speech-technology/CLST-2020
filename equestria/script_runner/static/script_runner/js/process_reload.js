PROFILE_OVERVIEW = document.getElementById("process_profile_overview");
STATUS_MESSAGE = document.getElementById("process_status_message")
DOWNLOAD_BUTTON = document.getElementById("process_download_button");

function get_status(status_url, callback /*, args */) {
    let args = Array.prototype.slice.call(arguments, 2);
    let data = {
        'csrfmiddlewaretoken': CSRF_TOKEN,
    };
    jQuery(function ($) {
        $.ajax({
            type: 'POST', url: status_url, data, dataType: 'json', asynch: true, success:
                function (returned_data) {
                    args.unshift(returned_data);
                    callback.apply(this, args);
                }
        }).fail(function () {
            console.error("Error while getting information about process ${process_id}.")
        });
    });
}

function toggle_download(display) {
    if (display) {
        DOWNLOAD_BUTTON.style.display = '';
    }
    else {
        DOWNLOAD_BUTTON.style.display = 'none';
    }
}

function toggle_profile_overview(display) {
    if (display) {
        PROFILE_OVERVIEW.style.display = '';
    }
    else {
        PROFILE_OVERVIEW.style.display = 'none';
    }
}

function update_status_message(message) {
    STATUS_MESSAGE.innerHTML = message;
}

function update_process_status(returned_data) {
    //Update status message
    if (returned_data.errors) {
        update_status_message(returned_data.error_message);
    }
    else {
        update_status_message(returned_data.status_message);
    }

    if (returned_data.status === 0) {
        //Ready
        toggle_download(false);
        toggle_profile_overview(true);
    }
    else if (returned_data.status === 1) {
        //Running
        toggle_download(false);
        toggle_profile_overview(false);
    }
    else {
        //Finished
        toggle_download(true);
        toggle_profile_overview(false);
    }
}

function reload_process_status() {
    get_status(STATUS_URL, update_process_status);
}

if (typeof STATUS_URL !== 'undefined' && typeof CSRF_TOKEN !== 'undefined') {
    reload_process_status();
    jQuery(document).ready(function($) {
        window.setInterval(function(){
            reload_process_status();
        }, 10000);
    });
}
else {
    console.warn("STATUS_URL or CSRF_TOKEN is not defined by the webpage, automatic status checking is disabled.")
}

function update_console_output() {
    var timeout = 1000;
    var file_to_load = $("#file_to_load").text();
    if (file_to_load === "None") {
	setTimeout(update_console_output, timeout);
	return;
    }
    if (!file_to_load.startsWith("/scripts/process/")) {
	file_to_load = "/scripts/process/1/" + file_to_load
    }
    $.get(file_to_load, function( content ) {
	//	alert(content);
	$('#console_output').html(content.replace(/\n/g, '<br />'));
    }, 'text'); 
    // execute every half a second
    setTimeout(update_console_output, timeout);
}

$( document ).ready(function() {
    update_console_output();
});
