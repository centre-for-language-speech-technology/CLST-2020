
function clear_directory(project_id) {
    if (confirm("This will clear all files from the current project, are you sure you want to continue?")) {
      update_and_callback_no_data(`/api/v1/projects/${project_id}/files/clear/`, {}, project_cleared)
    }
}

function project_cleared() {
    update_update_list();
}

function delete_item(file_id) {
    update_and_callback(`/api/v1/projects/${project_id}/files/${file_id}/`, {}, item_deleted, 'DELETE')
}

function item_deleted() {
    update_update_list();
}

function download_item(file_id) {
    window.location.href = `/api/v1/projects/${project_id}/files/${file_id}/download`;
}
