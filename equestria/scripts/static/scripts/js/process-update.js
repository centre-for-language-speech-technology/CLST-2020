PROCESS_PROFILES = document.getElementById("process-profiles");
PROCESS_DJANGO_STATUS = document.getElementById("process-django-status");
PROCESS_DOWNLOAD = document.getElementById("process-download-button");
CONSOLE_OUTPUT = document.getElementById("console_output");

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

function update_console_output(messages) {
    let text = "";
    for (let i = 0; i < messages.length; i++) {
        console.log(messages[i].time);
        console.log(messages[i].message)
        text += messages[i].time + ' ' + messages[i].message + '<br>';
    }
    CONSOLE_OUTPUT.innerHTML = text;
}

function update_page(returned_data) {
    if (returned_data.status == 0) {
        enable_process_start();
        disable_download();
        set_status_message("Ready to start");
    }
    else if (returned_data.status == 1) {
        disable_process_start();
        disable_download();
        set_status_message("Running");
    }
    else if (returned_data.status == 2) {
        disable_process_start();
        disable_download();
        set_status_message("CLAM server finished running");
    }
    else if (returned_data.status == 3) {
        disable_process_start();
        disable_download()
        set_status_message("Downloading files from CLAM server");
    }
    else if (returned_data.status == 4) {
        disable_process_start();
        enable_download();
        set_status_message("Done");
    }
    else if (returned_data.status == -1) {
        disable_process_start();
        disable_download();
        set_status_message("An error occurred, please try again later");
    }
    else {
        disable_process_start();
        set_status_message("Webserver request returned unknown status code.");
    }
    update_console_output(returned_data.log);
}

function main_loop() {
    get_status(update_page);
    setTimeout(main_loop, 5000);
}

$(document).ready(function() {
    main_loop();
});
