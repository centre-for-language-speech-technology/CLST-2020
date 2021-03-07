
let sync_timer = null;

function sync_with_server_callback(data) {
    setTimeout(function() {
        process_configure_vue.loading = false;
    }, 500);
}

function commence_update(data) {
    process_configure_vue.loading = true;
    update_and_callback(SYNC_SETTINGS_URL, JSON.stringify(data), sync_with_server_callback, method = "PUT");
}

function sync_with_server(data) {
    clearTimeout(sync_timer);
    sync_timer = setTimeout(commence_update, 500, data);
}

function start_process() {
    process_configure_vue.loading = true;
    let selected_profile = process_configure_vue.selected_profile;
    if (selected_profile !== null) {
        send_update_request(`/api/v1/processes/${project_id}/${script_id}/start/${selected_profile}`, callback_start_process, 'POST');
    }
    else {
        window.alert("Please select a profile first");
    }
}

function callback_start_process(data) {
    console.log(data.errors);
    if (data.errors.length > 0) {
        let error_msg = "The following error(s) occurred while starting the process: \n";
        for (let i = 0; i < data.errors.length; i++) {
            error_msg = error_msg.concat(`${data.errors[i]}\n`);
        }
        alert(error_msg);
    }
    else {
        window.location.href = data.redirect;
    }
    setTimeout(function() {
        process_configure_vue.loading = false;
    }, 500);
}