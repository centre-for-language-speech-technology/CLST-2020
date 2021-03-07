
function try_g2p_start() {
    send_update_request(`/api/v1/processes/${project_id}/${next_script_id}/start`, callback_start_g2p, 'POST');
}

function callback_start_g2p(data) {
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
}