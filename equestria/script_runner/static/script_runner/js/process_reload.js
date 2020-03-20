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

function update_ui(status) {
    console.log(status);
    if (status === 0) {
        //Ready
        toggle_download(false);
        toggle_profile_overview(true);
    }
    else if (status === 1) {
        //Running
        toggle_download(false);
        toggle_profile_overview(false);
	update_console_output();
    }
    else {
        //Finished
        toggle_download(true);
        toggle_profile_overview(false);
	fetch_console_output_if_not_loaded();
    }
}

function update_process_status(returned_data) {
    //Update status message
    if (returned_data.errors) {
        update_status_message(returned_data.error_message);
    }
    else {
        update_status_message(returned_data.status_message);
    }

    update_ui(returned_data.status)
}

function reload_process_status() {
    get_status(STATUS_URL, update_process_status);
}

function check_env_vars() {
    var ret = typeof STATUS_URL !== 'undefined' && typeof CSRF_TOKEN !== 'undefined';
    if (!ret) {
	console.warn("STATUS_URL or CSRF_TOKEN is not defined by the webpage, automatic status checking is disabled.");
    }
    return ret;
}

var timeout = 1000;
function main_loop() {
    reload_process_status()
    setTimeout(main_loop, timeout);
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
	//	alert(content);
	$('#console_output').html(content.replace(/\n/g, '<br />'));
    }, 'text'); 
}

$(document).ready(function() {
    if (check_env_vars()) main_loop();
    // assuming the user has bad internet and function execution takes more than a second
    // setInterval will run the function again, while setTimeout will wait for completion first
    // reloading a system log file every 10s is way too slow
});
