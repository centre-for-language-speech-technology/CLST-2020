PROFILE_OVERVIEW = document.getElementById("process_profile_overview");
STATUS_MESSAGE = document.getElementById("process_status_message")
DOWNLOAD_BUTTON = document.getElementById("process_download_button");

function get_status(status_url, callback /*, args */) {
    let args = Array.prototype.slice.call(arguments, 2);
    jQuery(function ($) {
        $.ajax({
            type: 'POST', url: status_url, dataType: 'json', asynch: true, success:
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
        DOWNLOAD_BUTTON.style.display = 'block';
    }
    else {
        DOWNLOAD_BUTTON.style.display = 'none';
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
    }
    else if (returned_data.status === 1) {
        //Running
        toggle_download(false);
    }
    else {
        //Finished
        toggle_download(true);
    }
}

function reload_process_status() {
    get_status(STATUS_URL, update_process_status);
}

if (typeof STATUS_URL !== 'undefined') {
    reload_process_status();
    jQuery(document).ready(function($) {
        window.setInterval(function(){
            reload_process_status();
        }, 10000);
    });
}
else {
    console.warn("STATUS_URL is not defined by the webpage, automatic status checking is disabled.")
}