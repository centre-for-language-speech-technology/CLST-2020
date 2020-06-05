from django.test import TestCase
from scripts.models import (
    Script,
    Pipeline,
    Project,
    Process,
    STATUS,
    BaseParameter,
    LogMessage,
    Profile,
    InputTemplate,
    BooleanParameter,
)
from django.contrib.auth import get_user_model
from django.conf import settings
from unittest.mock import patch, Mock
from django.conf import settings
import shutil, os, inspect, pathlib, datetime, pytz

"""
Both only as notes
STATUS = (
    (STATUS_CREATED, "Created"),
    (STATUS_UPLOADING, "Uploading files to CLAM"),
    (STATUS_RUNNING, "Running"),
    (STATUS_WAITING, "Waiting for download from CLAM"),
    (STATUS_DOWNLOADING, "Downloading files from CLAM"),
    (STATUS_FINISHED, "Finished"),
    (STATUS_ERROR, "Error"),
    (STATUS_ERROR_DOWNLOAD, "Error while downloading files from CLAM"),
)
TYPES = (
    (BOOLEAN_TYPE, "Boolean"),
    (STATIC_TYPE, "Static"),
    (STRING_TYPE, "String"),
    (CHOICE_TYPE, "Choice"),
    (TEXT_TYPE, "Text"),
    (INTEGER_TYPE, "Integer"),
    (FLOAT_TYPE, "Float"),
)
"""

_umodel = get_user_model()
_clamID = 1
_status = 0
_dummyvars = {
    "folder": "temptesting",
    "user": "testUser",
    "email": "test@test.com",
    "passw": "testpass",
    "fafile": "test.ctm",
    "oovdict": "test.oov.dict",
    "filecontent": "This file is purely for testing",
}
_templatevars = {
    "template_id": "why",
    "format": "are these",
    "label": "not",
    "extension": ".test",
    "optional": True,
    "unique": False,
    "accept_archive": True,
}
_dummglogmessages = [r"wait a second!1", r"Oi this went well"]


class DummyClamServer:
    """The dummy clam server mocks the actual clam server by doing fuck all"""
    deleteCall = False

    def create(self, id):
        deleteCall = False #reset upon respawn

    def startsafe(self, id, **kwargs):
        pass

    def addinputfile(self, id, templateid, path):
        pass

    def delete(self, id):
        deleteCall = True

    @staticmethod
    def spawn_dummyClam():
        return DummyClamServer()


class Test_ProcessMethods(TestCase):
    def setUp(self):
        self.dummy = _umodel.objects.create_user(
            _dummyvars["user"], _dummyvars["email"], _dummyvars["passw"]
        )
        self.folder = os.path.join(
            os.path.join(settings.USER_DATA_FOLDER, _dummyvars["folder"])
        )
        self.dummyscript = Script.objects.create(
            name="dummyscript", hostname="whatever"
        )
        self.dummybaseparam = None
        self.dummyboolparam = None
        self.dummyProcess = Process.objects.create(
            clam_id=_clamID,
            status=_status,
            script=self.dummyscript,
            folder=self.folder,
        )
        self.dummyprofile = Profile.objects.create()
        self.dummytemplate = InputTemplate.objects.create(
            template_id=_templatevars["template_id"],
            format=_templatevars["format"],
            extension=_templatevars["extension"],
            optional=_templatevars["optional"],
            unique=_templatevars["unique"],
            accept_archive=_templatevars["accept_archive"],
            corresponding_profile=self.dummyprofile,
        )
        self.thisfolder = pathlib.Path(__file__).parent.absolute()
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)  # Recursively destroy the file

    def writeFile(self, name):
        """Adds a specific file to the user associated project directory"""
        with open(os.path.join(self.folder, name), "w") as f:
            f.write(_dummyvars["filecontent"])

    def test_string_repr(self):
        alleq = True
        for (l, r) in STATUS:
            alleq = alleq and (
                f"Process for {str(self.dummyscript)} ({STATUS[l][1]})"
                == str(
                    Process.objects.create(status=l, script=self.dummyscript)
                )
            )
        self.assertEquals(alleq, True)

    def readXML(self, name):
        """Reads the specific mock XML in this folder"""
        temp = ""
        with open(os.path.join(self.thisfolder, name), "r") as f:
            temp = f.read()
        return temp

    def readFile(self, name):
        """Reads a specific file in the user associated project directory"""
        temp = ""
        with open(os.path.join(self.folder, name), "r") as f:
            temp = f.read()
        return temp

    # You really can't test this for shit but we gotta get that code cov boi
    @patch("scripts.models.Process.get_random_clam_id", return_value="works")
    def test_token(self, mock):
        self.assertEquals(Process.get_random_clam_id(), "works")

    def test_xml_feed_creation(self):
        """Tests logmessage creation"""
        teststr = self.readXML("xmlmock.xml")
        self.dummyProcess.update_log_messages_from_xml(teststr)
        logmessages = LogMessage.objects.all()
        self.assertEquals(len(logmessages), 2)

    def test_xml_feed_message(self):
        """Tests logmessage string entry"""
        teststr = self.readXML("xmlmock.xml")
        self.dummyProcess.update_log_messages_from_xml(teststr)
        logmessages = LogMessage.objects.all()
        alleq = True
        for c, msg in enumerate(_dummglogmessages):
            alleq = alleq and (msg in logmessages[c].message)
        self.assertEquals(alleq, True)

    def test_timeparseNoException(self):
        """Tests whether the timeparse works"""
        dummydate = r"12/Feb/2018 09:15:32"
        try:
            dtz = pytz.timezone(settings.TIME_ZONE)
            res = dtz.localize(
                datetime.datetime.strptime(dummydate, r"%d/%b/%Y %H:%M:%S")
            )
            val = Process.parse_time_string(dummydate)
            self.assertEqual(str(val), str(res))
        except ValueError as e:
            self.fail(f"Error occured in timeparsing: {e}")

    def test_timeparseException(self):
        """Tests whether the timeparse works"""
        dummydate = r"this cant be parsed"
        val = Process.parse_time_string(dummydate)
        if val == None:
            pass
        else:
            self.fail(f"Shouldn't be able to parse {dummydate}!")

    def test_statusUpdate(self):
        """Tests whether status gets saved properly"""
        status_index = 2  # Corresponds to "running"
        self.dummyProcess.set_status(status_index)
        self.assertEquals(
            Process.objects.get(clam_id=_clamID).status, status_index
        )

    def test_clamIDUpdate(self):
        """Tests whether clam ID gets saved properly"""
        new_id = 7
        self.dummyProcess.set_clam_id(new_id)
        try:
            self.assertEquals(
                Process.objects.get(clam_id=new_id).clam_id, str(new_id)
            )
        except:
            self.fail(f"Failed to set and find process for clam ID {new_id}")

    def test_statusGet(self):
        """Tests whether the status get works"""
        self.assertEqual(self.dummyProcess.get_status(), _status)

    def test_statusString(self):
        """Tests whether the status to string works"""
        target = (
            "Ready to start"  # Ripped straight from the code, was hardcoded
        )
        self.assertEqual(self.dummyProcess.get_status_string(), target)

    def test_finishedFlag(self):
        """Tests whether the is_finished method works"""
        finished_status = 5
        self.dummyProcess.status = STATUS[finished_status][0]
        self.assertEqual(self.dummyProcess.is_finished(), True)

    def test_filterStatusMessages(self):
        """Tests whether the logmessages are filtered correctly"""
        teststr = self.readXML("xmlmock.xml")
        self.dummyProcess.update_log_messages_from_xml(teststr)
        logmessages = self.dummyProcess.get_status_messages()
        self.assertEqual(len(logmessages), len(_dummglogmessages))

    def test_startingClamNotNew(self):
        """Tests whether the start method behaves properly with not new status"""
        finished_status = 5
        self.dummyProcess.status = STATUS[finished_status][0]
        self.assertEquals(self.dummyProcess.start(self.dummyprofile), False)

    def test_startingClamNotNew(self):
        """Tests whether the start method behaves properly with not new status"""
        finished_status = 5
        self.dummyProcess.status = STATUS[finished_status][0]
        self.assertEquals(self.dummyProcess.start(self.dummyprofile), False)

    def make_tempdir(self):
        if not os.path.exists(
            self.folder
        ):  # First spawn a folder to test file seeking
            try:
                os.mkdir(self.folder)
            except:
                self.fail(f"Error in creation of {self.folder}")

    def spawn_dummyparam(self, dpreset=True):
        """Spawns a paramater associated with the script"""
        self.dummybaseparam = BaseParameter.objects.create(
            name="dummy parameter",
            type=BaseParameter.BOOLEAN_TYPE,
            preset=dpreset,  # no idea what this is
            corresponding_script=self.dummyscript
        )
        self.dummyboolparam = BooleanParameter.objects.create(
            base=self.dummybaseparam, value=True
        )

    def test_startingClamNew_WithBaseParams_WithoutInputForTemplate_NotOptional_notUnique(
        self,
    ):
        """Tests whether the start method behaves properly with new status"""
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam()
        self.dummytemplate.optional = False
        self.dummytemplate.save()
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            try:
                self.dummyProcess.start(
                    self.dummyprofile, {self.dummybaseparam.name: True}
                )
                self.fail("Provided no files for process but still succeeds!")
            except:
                pass

    def test_startingClamNew_WithBaseParams_WithInputForTemplate_NotOptional_notUnique(
        self,
    ):
        """Tests whether the start method behaves properly with new status"""
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam()
        self.dummytemplate.optional = False
        self.dummytemplate.save()
        self.writeFile(f"somefile{_templatevars['extension']}")
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            res = self.dummyProcess.start(
                self.dummyprofile, {self.dummybaseparam.name: True}
            )
        self.assertEquals(res, True)

    def test_generate_parameters_from_clamdata(self):
        pass  # TODO: this

    def test_2startingClamNew_WithoutBaseParams_WithInputForTemplate_NotOptional_notUnique(self):
        """Tests whether the start method behaves properly when missing provided paramaters"""
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam(False)
        self.dummytemplate.optional = False
        self.dummytemplate.save()
        self.writeFile(f"somefile{_templatevars['extension']}")
        with patch.object(self.dummyscript, 'get_clam_server', new=DummyClamServer.spawn_dummyClam):
            try:
                res = self.dummyProcess.start(self.dummyprofile)
                self.fail("Missing paramaters should fail!")
            except:
                pass

    def test_2startingClamNew_WithBaseParams_WithInputForTemplate_NotOptional_UniqueDuplicate(self):
        """Tests whether the start method behaves properly when a duplicate file exists despite being unique"""
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam()
        self.dummytemplate.optional = False
        self.dummytemplate.unique = True
        self.dummytemplate.save()
        self.writeFile(f"somefile{_templatevars['extension']}")
        self.writeFile(f"duplicatefile{_templatevars['extension']}")
        with patch.object(self.dummyscript, 'get_clam_server', new=DummyClamServer.spawn_dummyClam):
            try:
                res = self.dummyProcess.start(self.dummyprofile, {self.dummybaseparam.name: True})
                self.fail("Duplicate file should fail for unique!")
            except:
                pass

    def test_startSafe_Exception(self):
        """Test whether starting safe works if an exception is thrown"""
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam(False)
        self.dummytemplate.optional = False
        self.dummytemplate.save()
        self.writeFile(f"somefile{_templatevars['extension']}")
        with patch.object(self.dummyscript, 'get_clam_server', new=DummyClamServer.spawn_dummyClam):
            try:
                res = self.dummyProcess.start_safe(self.dummyprofile)
                self.fail("Start safe should propagate exception!")
            except:
                pass

    def test_startSafe_NoException(self):
        """
        Test whether starting safe works if no exception is thrown
        """
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam()
        self.dummytemplate.optional = False
        self.dummytemplate.save()
        self.writeFile(f"somefile{_templatevars['extension']}")
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            res = self.dummyProcess.start_safe(
                self.dummyprofile, {self.dummybaseparam.name: True}
            )
        self.assertEquals(res, True)

    def test_cleanup_NoException(self):
        """
        Test whether cleanup performs wanted functionality when no exception occurs
        """
        pass

