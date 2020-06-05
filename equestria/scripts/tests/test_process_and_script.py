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
import shutil, os, inspect, pathlib, datetime, pytz, logging, clam.common.status, clam.common.parameters

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
_projID = "someproject"
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
_dummyClamParams = {
    "bool": clam.common.parameters.BooleanParameter("a", "a"),
    "static": clam.common.parameters.StaticParameter(
        "a", "a", value="whatever"
    ),
    "string": clam.common.parameters.StringParameter("a", "a"),
    "choice": clam.common.parameters.ChoiceParameter(
        "a", "a", "description", choices=["sure", "whatever"]
    ),
    "integer": clam.common.parameters.IntegerParameter("a", "a"),
    "float": clam.common.parameters.FloatParameter("a", "a"),
    "text": clam.common.parameters.TextParameter("a", "a"),
}

_dummyParameterInputs = {
    "bool": True,
    "static": "text",
    "string": "text",
    "choice": ["sure", "whatever"],
    "integer": 2,
    "float": 2.2,
    "text": "more text",
}
_zipdir = "testingDecompress"
_dummglogmessages = [r"wait a second!1", r"Oi this went well"]


class DummyClamServer:
    """The dummy clam server mocks the actual clam server by doing fuck all"""

    class DummyClamData:
        """This dummy Clam data object mocks a clam data object"""

        def parameter(self, input):
            return _dummyClamParams[input]

    class DummyTemplate:
        """This dummy template object mocks a clam template data object"""

        def __init__(self):
            self.id = "someId"
            self.formatclass = "someformat"
            self.label = "somelabel"
            self.extension = ".zip"
            self.optional = True
            self.unique = True
            self.acceptarchive = True

    class DummyClamStatus:
        """This dummy Clam status object mocks a clam status object"""

        def __init__(self, xmlcontent):
            self.status = clam.common.status.DONE
            self.xml = xmlcontent

    deleteCall = False
    xmlContent = ""
    targetfolder = ""

    def create(self, id):
        pass

    def startsafe(self, id, **kwargs):
        pass

    def addinputfile(self, id, templateid, path):
        pass

    def get(self, id):
        return DummyClamServer.DummyClamStatus(self.xmlContent)

    def downloadarchive(self, id, bool, ext):
        """Creates a dir with a single file in it, then zips it. Mocks downloadarchive"""
        nfolder = os.path.join(self.targetfolder, _zipdir)
        targetname = os.path.join(self.targetfolder, str(_clamID))
        if not os.path.exists(nfolder):
            os.mkdir(nfolder)
        shutil.make_archive(targetname, "zip", nfolder)

    @staticmethod
    def delete(id):
        DummyClamServer.deleteCall = True

    @staticmethod
    def spawn_dummyClam():
        return DummyClamServer()

    @staticmethod
    def spawn_Exception():
        # The most useful method
        raise ValueError("Some arbitrary thing occured!!!")
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
        # if os.path.exists(self.folder):
        #     shutil.rmtree(self.folder)  # Recursively destroy the file

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

    def test_token(self):
        """Tests whether a token hex is created of desired length"""
        res = Process.get_random_clam_id()
        self.assertEquals(len(res), 64)

    def test_xml_feed_creation(self):
        """Tests logmessage creation"""
        teststr = self.readXML("xmlmock.xml")
        self.dummyProcess.update_log_messages_from_xml(teststr)
        logmessages = LogMessage.objects.all()
        self.assertEquals(len(logmessages), 2)

    def test_xml_feed_Exception(self):
        """Tests second branch in update_log_messages_from_xml"""
        teststr = self.readXML("xmlmockFaulty.xml")
        try:
            self.dummyProcess.update_log_messages_from_xml(teststr)
            self.fail("Shouldn't be able to parse this XML file")
        except:
            pass

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
        targets = [
            (0, "Ready to start"),
            (2, "Running"),
            (3, "CLAM Done, waiting for download"),
            (4, "Downloading files from CLAM"),
            (5, "Done"),
            (-1, "An error occurred"),
            (-10, "Unknown"),
        ]
        res = True
        for t in targets:
            self.dummyProcess.status = t[0]
            res = res and (self.dummyProcess.get_status_string() == t[1])
        self.assertEqual(res, True)

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
            corresponding_script=self.dummyscript,
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

    def test_2startingClamNew_WithoutBaseParams_WithInputForTemplate_NotOptional_notUnique(
        self,
    ):
        """Tests whether the start method behaves properly when missing provided paramaters"""
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam(False)
        self.dummytemplate.optional = False
        self.dummytemplate.save()
        self.writeFile(f"somefile{_templatevars['extension']}")
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            try:
                res = self.dummyProcess.start(self.dummyprofile)
                self.fail("Missing paramaters should fail!")
            except:
                pass

    def test_2startingClamNew_WithBaseParams_WithInputForTemplate_NotOptional_UniqueDuplicate(
        self,
    ):
        """Tests whether the start method behaves properly when a duplicate file exists despite being unique"""
        created_status = 0
        self.make_tempdir()
        self.spawn_dummyparam()
        self.dummytemplate.optional = False
        self.dummytemplate.unique = True
        self.dummytemplate.save()
        self.writeFile(f"somefile{_templatevars['extension']}")
        self.writeFile(f"duplicatefile{_templatevars['extension']}")
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            try:
                res = self.dummyProcess.start(
                    self.dummyprofile, {self.dummybaseparam.name: True}
                )
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
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
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
        DummyClamServer.deleteCall = False
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            self.dummyProcess.cleanup()
        res = (self.dummyProcess.clam_id == None) and (
            DummyClamServer.deleteCall
        )
        self.assertEqual(res, True)

    def test_cleanup_Exception(self):
        """
        Test whether cleanup performs wanted functionality when no exception occurs
        """
        DummyClamServer.deleteCall = False
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_Exception,
        ):
            try:
                self.dummyProcess.cleanup()
                self.fail("This should be logically unreachable code!")
            except:
                res = (not self.dummyProcess.clam_id == None) or (
                    DummyClamServer.deleteCall
                )
                self.assertEqual(res, False)

    def test_is_finishedTrue(self):
        """
        Test whether finished functions as expected
        """
        finished_status = 5
        self.dummyProcess.status = finished_status
        self.assertEquals(self.dummyProcess.is_finished(), True)

    def test_clam_update_NotRunning(self):
        """
        Tests first branch in clam_update
        """
        finished_status = 5
        self.dummyProcess.status = finished_status
        res = self.dummyProcess.clam_update()
        self.assertEquals(res, False)

    def test_clam_update_Exception(self):
        """
        Tests second branch in clam_update
        """
        finished_status = 5
        self.dummyProcess.status = finished_status
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_Exception,
        ):
            res = self.dummyProcess.clam_update()
        self.assertEquals(res, False)

    def test_clam_update_Nominal(self):
        """
        Tests third branch in clam_update
        """
        running_status = 2
        self.dummyProcess.status = running_status
        DummyClamServer.xmlContent = self.readXML("xmlmock.xml")
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            res = self.dummyProcess.clam_update()
        self.assertEquals(res, True)

    def test_downloadNDelete_wrongStatus(self):
        """
        Tests first branch in download and delete
        """
        running_status = 2
        self.dummyProcess.status = running_status
        res = self.dummyProcess.download_and_delete()
        self.assertEquals(res, False)

    def test_downloadNDelete_Nominal(self):
        """
        Tests second branch in download and delete
        """
        running_status = 2
        self.dummyProcess.status = running_status
        with patch.object(
            self.dummyProcess,
            "download_archive_and_decompress",
            new=lambda: True,
        ):
            res = self.dummyProcess.download_and_delete()
        self.assertEquals(res, False)

    def test_generate_paramaters_NoException(self):
        """
        Tests ALL branches in generate_paramaters_from_clam_data. Only fails if exception occurs
        """
        self.dummyscript.generate_parameters_from_clam_data(
            _dummyClamParams.keys(),
            DummyClamServer.DummyClamData(),
            _dummyParameterInputs,
        )

    def test_template_from_data(self):
        """
        Tests the creation of template data. Only fails if exception is thrown
        """
        self.dummyscript.create_templates_from_data(
            [DummyClamServer.DummyTemplate()]
        )

    def test_download_archive_and_decompress_Exception(self):
        """
        Tests first branch of download_archive_and_decompress
        """
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_Exception,
        ):
            try:
                self.dummyProcess.download_archive_and_decompress()
                self.fail("Should throw an exception")
            except:
                pass

    def test_download_archive_and_decompress_Nominal(self):
        """
        Tests first branch of download_archive_and_decompress
        """
        DummyClamServer.targetfolder = self.folder
        self.make_tempdir()
        with patch.object(
            self.dummyscript,
            "get_clam_server",
            new=DummyClamServer.spawn_dummyClam,
        ):
            res = self.dummyProcess.download_archive_and_decompress()
        self.assertEquals(res, True)
