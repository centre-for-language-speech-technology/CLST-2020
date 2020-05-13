"""Module to handle tasks I guess."""
from background_task import background
import scripts.models


@background(schedule=1)
def update_script(process_id):
    """
    Spawn a background task to update a script's status.

    :param process_id: the id of the process to update (this is not the process itself as it is not JSON serializable)
    :return: None
    """
    process = scripts.models.Process.objects.get(id=process_id)
    status = process.get_status()
    if status == scripts.models.STATUS_RUNNING:
        process.clam_update()
        update_script(process_id)
    elif status == scripts.models.STATUS_WAITING:
        process.download_and_delete()
