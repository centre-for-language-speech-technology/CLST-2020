from django.utils import timezone
from django.test import TestCase
from scripts.models import LogMessage, Process, Script
import os


class TestLogMessage(TestCase):
    """Test the LogMessage model"""

    fixtures = [
        "simple_pipelines.json",
    ]

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.process1 = Process.objects.create(
            script=Script.objects.all()[0],
            folder=os.path.abspath(os.path.dirname(__file__)),
        )

    def test_log_message_creation(self):
        logmessage1 = LogMessage.objects.create(
            time=timezone.now(), message="Test", process=self.process1, index=1
        )
        self.assertTrue(logmessage1 in LogMessage.objects.all())
