from django.test import TestCase
from scripts.models import Script, Pipeline, Project, Process
from django.contrib.auth import get_user_model
from django.conf import settings
import shutil
import os
import inspect

_proj_name = "Testing project"
_umodel = get_user_model()
_dummyvars = {
    "user": "testUser",
    "email": "test@test.com",
    "passw": "testpass",
    "fafile": "test.ctm",
    "oovdict": "test.oov.dict",
    "filecontent": "This file is purely for testing",
}


class Test_ProjectMethods(TestCase):
    """
    Tests projects in scripts/models.py
    Keep in mind this relies on the clam fixture - implying you will have to add the password manually
    """

    fixtures = ["clam.json"]

    def setUp(self):
        # Looks like these must all be in setup due to Django initializing the fixture with the class
        self.dummy = _umodel.objects.create_user(
            _dummyvars["user"], _dummyvars["email"], _dummyvars["passw"]
        )
        self.folder = os.path.join(
            os.path.join(settings.USER_DATA_FOLDER, self.dummy.username),
            _proj_name,
        )
        self.FA_script = Script.objects.create(name="fa_script1", hostname="na")
        self.FA_script2 = Script.objects.create(
            name="fa_script2", hostname="na"
        )
        self.G2P_script = Script.objects.get(pk=2)
        self.test_pipeline = Pipeline.objects.create(
            name="Testing pipeline",
            fa_script=self.FA_script,
            g2p_script=self.G2P_script,
        )
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)  # Recursively destroy the file

    def writeFile(self, name):
        """Adds a specific file to the user associated project directory"""
        with open(os.path.join(self.folder, name), "w") as f:
            f.write(_dummyvars["filecontent"])

    def readFile(self, name):
        """Reads a specific file in the user associated project directory"""
        temp = ""
        with open(os.path.join(self.folder, name), "r") as f:
            temp = f.read()
        return temp

    def test_project_creation(self):
        """Tests whether a project can be created for a given user"""
        try:
            Project.create_project(
                name=_proj_name, pipeline=self.test_pipeline, user=self.dummy
            )
            pass
        except ValueError:
            self.fail("Project creation failed with exception!")

    def test_duplicate_project(self):
        """Tests whether a project throws a value error when a duplicate project is created"""
        Project.objects.create(
            name=_proj_name, pipeline=self.test_pipeline, user=self.dummy
        )
        try:
            Project.create_project(
                name=_proj_name, pipeline=self.test_pipeline, user=self.dummy
            )
            self.fail("Duplicate project should abort!")
        except ValueError:
            pass

    def create_project(self, log):
        """Boilerplate"""
        try:
            return Project.create_project(
                name=_proj_name, pipeline=self.test_pipeline, user=self.dummy
            )
        except ValueError:
            self.fail("Failed to create project in {0}!".format(log))

    def test_project_stage_uploading(self):
        """Tests whether a project enters the UPLOADING phase appropriately"""
        proj = self.create_project(inspect.currentframe().f_code.co_name)
        self.assertEquals(proj.get_next_step(), Project.UPLOADING)

    def test_project_stage_checkdictionary(self):
        """Tests whether a project enters the CHECK_DICTIONARY phase appropriately"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        try:
            self.writeFile(_dummyvars["fafile"])
        except:
            self.fail("Failed to write file in {0}".format(frame))
        self.assertEquals(proj.get_next_step(), Project.CHECK_DICTIONARY)

    def test_project_stage_fa(self):
        """Tests whether a project enters the FA_RUNNING phase appropriately"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.current_process = Process.objects.create(script=self.FA_script)
        self.assertEquals(proj.get_next_step(), Project.FA_RUNNING)

    def test_project_stage_g2p(self):
        """Tests whether a project enters the FA_RUNNING phase appropriately"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.current_process = Process.objects.create(script=self.G2P_script)
        self.assertEquals(proj.get_next_step(), Project.G2P_RUNNING)

    def test_property_g2p(self):
        """Tests whether a project enters the FA_RUNNING phase appropriately, but through accessing the property"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.current_process = Process.objects.create(script=self.G2P_script)
        self.assertEquals(proj.status, Project.G2P_RUNNING)

    def test_property_fa(self):
        """Tests whether a project enters the FA_RUNNING phase appropriately, but through accessing the property"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.current_process = Process.objects.create(script=self.FA_script)
        self.assertEquals(proj.status, Project.FA_RUNNING)

    def test_property_checkdictionary(self):
        """Tests whether a project enters the CHECK_DICTIONARY phase appropriately, but through accessing the property"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        try:
            self.writeFile(_dummyvars["fafile"])
        except:
            self.fail("Failed to write file in {0}".format(frame))
        self.assertEquals(proj.status, Project.CHECK_DICTIONARY)

    def test_property_uploading(self):
        """Tests whether a project enters the UPLOADING phase appropriately, but through accessing the property"""
        proj = self.create_project(inspect.currentframe().f_code.co_name)
        self.assertEquals(proj.status, Project.UPLOADING)

    def test_oovDictPath(self):
        """Tests whether the oov.dict's path is returned correctly"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        res = os.path.join(self.folder, _dummyvars["oovdict"])
        try:
            self.writeFile(_dummyvars["oovdict"])
        except:
            self.fail("Failed to write file in {0}".format(frame))
        self.assertEquals(proj.get_oov_dict_file_path(), res)

    def test_oovDictContent(self):
        """Tests whether the oov.dict's content is returned correctly"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        try:
            self.writeFile(_dummyvars["oovdict"])
        except:
            self.fail("Failed to write file in {0}".format(frame))
        self.assertEquals(
            proj.get_oov_dict_file_contents(), _dummyvars["filecontent"]
        )

    def test_isProjectScript_true(self):
        """Checks if project has the same associated script as provided"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        self.assertEquals(proj.is_project_script(self.FA_script), True)

    def test_isProjectScript_false(self):
        """Checks if project has another associated script as provided"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        self.assertEquals(proj.is_project_script(self.FA_script2), False)

    def test_writeOovDict_clean(self):
        """Checks if we can write to an oov dict file"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        try:
            self.writeFile(_dummyvars["oovdict"])
        except:
            self.fail("Failed to write file in {0}".format(frame))
        try:
            proj.write_oov_dict_file_contents(_dummyvars["filecontent"])
        except:
            self.fail("Failed to write file in {0}".format(frame))
        self.assertEquals(
            self.readFile(_dummyvars["oovdict"]), _dummyvars["filecontent"]
        )

    def test_writeOovDict_newfile(self):
        """Checks if we can create and write to an oov dict file"""
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        try:
            proj.write_oov_dict_file_contents(
                _dummyvars["filecontent"], name=_dummyvars["oovdict"]
            )
        except:
            self.fail("Failed to write file in {0}".format(frame))
        self.assertEquals(
            self.readFile(_dummyvars["oovdict"]), _dummyvars["filecontent"]
        )

    def test_canUpload_false(self):
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.current_process = Process.objects.create(script=self.FA_script)
        self.assertEqual(proj.can_upload(), False)

    def test_canStartNew_false(self):
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.current_process = Process.objects.create(script=self.FA_script)
        self.assertEqual(proj.can_start_new_process(), False)

    def test_canStartNew_true(self):
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.current_process = Process.objects.create(script=self.FA_script)
        proj.cleanup()
        self.assertEqual(proj.can_start_new_process(), True)

    def test_createCompressedArchive(self):
        frame = inspect.currentframe().f_code.co_name
        proj = self.create_project(frame)
        proj.create_downloadable_archive()
        self.assertEqual(
            os.path.exists(
                os.path.join(self.folder, "{0}{1}".format(_proj_name, ".zip"))
            ),
            True,
        )
