PROFILE_OVERVIEW_PREFIX = "process_profile_overview";
STATUS_MESSAGE_PREFIX = "process_status_message"
DOWNLOAD_BUTTON_PREFIX = "process_download_button";

function get_status(process_info, callback /*, args */) {
    let args = Array.prototype.slice.call(arguments, 2);
    let data = {
        'csrfmiddlewaretoken': CSRF_TOKEN,
    };
    jQuery(function ($) {
        $.ajax({
            type: 'POST', url: process_info[1], data, dataType: 'json', asynch: true, success:
            function (returned_data) {
		args.unshift(process_info[0]);
                args.unshift(returned_data);
                callback.apply(this, args);
                }
        }).fail(function () {
            console.error("Error while getting information about process " + process_info[0] + ".");
        });
    });
}

function toggle_download(display, process_id) {
    download_button = document.getElementById(DOWNLOAD_BUTTON_PREFIX + "_" + process_id)
    download_button.style.display = display ? '' : 'none';
}

function toggle_profile_overview(display, process_id) {
    profile_overview = document.getElementById(PROFILE_OVERVIEW_PREFIX + "_" + process_id)
    profile_overview.style.display = display ? '' : 'none';
}

function update_status_message(message, process_id) {
    status_message = document.getElementById(STATUS_MESSAGE_PREFIX + "_" + process_id);
    status_message.innerHTML = message;
}

function update_ui(status, process_id) {
    if (status === 0) {
        //Ready
        toggle_download(false, process_id);
        toggle_profile_overview(true, process_id);
    }
    else if (status === 1) {
        //Running
        toggle_download(false, process_id);
        toggle_profile_overview(false, process_id);
	update_console_output();
    }
    else {
        //Finished
        toggle_download(true, process_id);
        toggle_profile_overview(false, process_id);
	fetch_console_output_if_not_loaded();
    }
}

function update_process_status(returned_data, process_id) {
    //Update status message
    if (returned_data.errors) {
        update_status_message(returned_data.error_message, process_id);
    }
    else {
        update_status_message(returned_data.status_message, process_id);
    }
    
    update_ui(returned_data.status, process_id)
}

function reload_process_status(process_info) {
    get_status(process_info, update_process_status);
}

function check_env_vars() {
    var ret = typeof PROCESS_LIST !== 'undefined' && typeof CSRF_TOKEN !== 'undefined';
    if (!ret) {
	console.warn("PROCESS_LIST or CSRF_TOKEN is not defined by the webpage, automatic status checking is disabled.");
    }
    return ret;
}

function fetch_console_output_if_not_loaded() {
    if ($('#console_output').html() === "")
	update_console_output()
}

function update_console_output() {
    var file_to_load = $("#file_to_load").text();
    if (file_to_load === "None") {
	return;
    }
    if (!file_to_load.startsWith("/scripts/process/")) {
	file_to_load = "/scripts/process/1/" + file_to_load
    }
    $.get(file_to_load, function( content ) {
	$('#console_output').html(content.replace(/\n/g, '<br />'));
    }, 'text'); 
}

var timeout = 1000;
function main_loop() {
    PROCESS_LIST.forEach(
	function (process_info, index) {
	    // process_id = process_info[0]
	    // status_url = process_info[1]
	    // console.log(process_id + " " + status_url + "\n");
	    reload_process_status(process_info);
        }
    );
    setTimeout(main_loop, timeout);
}

$(document).ready(function() {
    if (check_env_vars()) main_loop();
});

// assuming the user has bad internet and function execution takes more than a second
// setInterval will run the function again, while setTimeout will wait for completion first
// reloading a system log file every 10s is way too slow
