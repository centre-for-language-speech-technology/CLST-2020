from scripts.models import STATUS_DOWNLOAD, STATUS_RUNNING
from background_task import background
from .models import Process


@background(schedule=10)
def update_script(process_id):
    """
    Spawn a background task to update a script.

    :param process_id: the id of the process to update (this is not the process itself as it is not JSON serializable
    :return: the data or None on failure
    """
    process = Process.objects.get(id=process_id)
    status = process.clam_update()
    if status == STATUS_RUNNING or status == STATUS_DOWNLOAD:
        update_script(process.id)
