from django.test import TestCase
from scripts.models import *
import os
from scripts.tasks import *
from unittest.mock import patch, Mock


class TestTasks(TestCase):
    """Test the LogMessage model"""

    fixtures = [
        "simple_pipelines.json",
    ]

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.process1 = Process.objects.create(
            script=Script.objects.all()[0],
            # clam_id=1337,
            # status=STATUS_WAITING,
            folder=os.path.abspath(os.path.dirname(__file__)),
        )
        self.id1 = self.process1.get_random_clam_id()
        self.process1.set_clam_id(self.id1)
        self.process1.set_status(STATUS_WAITING)
        self.process2 = Process.objects.create(
            script=Script.objects.all()[1],
            # clam_id=69420,
            # status=STATUS_RUNNING,
            folder=os.path.abspath(os.path.dirname(__file__)),
        )
        self.id2 = self.process2.get_random_clam_id()
        self.process2.set_clam_id(self.id2)
        self.process2.set_status(STATUS_RUNNING)

    @patch(
        "scripts.models.Process.get_status",
        side_effect=[
            scripts.models.STATUS_RUNNING,
            scripts.models.STATUS_WAITING,
        ],
    )
    @patch("scripts.models.Process.clam_update")
    @patch("scripts.models.Process.download_and_delete")
    def test_update_script(self, mockWaiting, mockRunning, mockStatus):
        """Tests the update_script function."""
        update_script2(1)
        assert mockWaiting.call_count == 1
        assert mockRunning.call_count == 1
