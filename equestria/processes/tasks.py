"""Module to handle tasks I guess."""
from background_task import background
import processes.models


@background(schedule=1)
def update_script(process_id):
    """
    Spawn a background task to update a script's status.

    :param process_id: the id of the process to update (this is not the process itself as it is not JSON serializable)
    :return: None
    """
    process = processes.models.Process.objects.get(id=process_id)
    if process.status == processes.models.Process.STATUS_RUNNING:
        if not process.clam_update():
            process.status = processes.models.Process.STATUS_ERROR
            return

        update_script(process_id)
    elif process.status == processes.models.Process.STATUS_WAITING:
        process.download_and_cleanup()
