PROCESS_PROFILES = document.getElementById("process-profiles");
PROCESS_DJANGO_STATUS = document.getElementById("process-django-status");
PROCESS_DOWNLOAD = document.getElementById("process-download-button");

function get_status(callback /*, args */) {
    let args = Array.prototype.slice.call(arguments, 2);
    let data = {
        'csrfmiddlewaretoken': CSRF_TOKEN,
    };
    jQuery(function ($) {
        $.ajax({
            type: 'POST', url: PROCESS_STATUS_URL, data, dataType: 'json', asynch: true, success:
            function (returned_data) {
                    args.unshift(returned_data);
                    callback.apply(this, args);
                }
        }).fail(function () {
            console.error("Error while getting information about process.");
        });
    });
}

function disable_process_start() {
    PROCESS_PROFILES.style.display = "none";
}

function enable_process_start() {
    PROCESS_PROFILES.style.display = "";
}

function set_status_message(message) {
    PROCESS_DJANGO_STATUS.innerText = message;
}

function disable_download() {
    PROCESS_DOWNLOAD.style.display = "none";
}

function enable_download() {
    PROCESS_DOWNLOAD.style.display = "";
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

function update_page(returned_data) {
    if (returned_data.django_status == 0) {
        enable_process_start();
        disable_download();
        set_status_message("Ready to start");
    }
    else if (returned_data.django_status == 1) {
        disable_process_start();
        disable_download();
        set_status_message("Running");
	update_console_output();
    }
    else if (returned_data.django_status == 2) {
        disable_process_start();
        disable_download();
        set_status_message("Downloading files from CLAM server");
	update_console_output();
    }
    else if (returned_data.django_status == 3) {
        disable_process_start();
        enable_download();
        set_status_message("Done");
    }
    else if (returned_data.django_status == -1) {
        disable_process_start();
        disable_download();
        set_status_message("An error occurred, please try again later");
	fetch_console_output_if_not_loaded();
    }
    else {
        disable_process_start();
        set_status_message("Webserver request returned wrong status code.");
	fetch_console_output_if_not_loaded();
    }
}

function main_loop() {
    get_status(update_page);
    fetch_console_output_if_not_loaded();
    setTimeout(main_loop, 5000);
}

$(document).ready(function() {
    main_loop();
});
