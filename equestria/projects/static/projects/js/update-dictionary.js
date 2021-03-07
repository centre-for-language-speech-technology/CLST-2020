
let sync_timer = null;


function update_dictionary_containers() {
    check_dictionary_vue.loading = true;
    update_and_callback(`/api/v1/projects/${project_id}/dictionary`, JSON.stringify({"files": check_dictionary_vue.files}), dictionary_update_containers_callback, 'PATCH');
}

function dictionary_update_containers_callback(data) {
    setTimeout(function() {
        check_dictionary_vue.loading = false;
    }, 500);
}

function sync_with_server(data) {
    clearTimeout(sync_timer);
    sync_timer = setTimeout(update_dictionary_containers, 500, data);
}