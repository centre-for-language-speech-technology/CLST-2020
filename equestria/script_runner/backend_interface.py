import requests
from urllib import parse
from xml.etree import ElementTree
from os.path import basename


def run(script, argument_list):
    """
    Mock function to run a script.

    TODO: change this function to do actual things
    :param script:
    :param argument_list:
    :return:
    """
    wrapper = ClamWrapper(str(script.hostname))
    wrapper.get_output_archive(str(45), "zip")


class ClamWrapper:
    """Interface for a CLAM server."""

    def __init__(self, hostname):
        """
        Initialise a ClamWrapper object.

        :param hostname: the hostname of the CLAM server (including the port)
        """
        self.hostname = hostname

    def create_new_project(self, project_id):
        """
        Create a new project with id project_id.

        :param project_id: the project id of the project
        :return: None, raises an Exception when the CLAM server is not reachable or the project already exists
        """
        r = requests.get(parse.urljoin(self.hostname, project_id))

        if r.status_code == 200 or r.status_code == 403:
            raise Exception("Project ID already exists!")
        elif r.status_code != 404:
            raise Exception("The CLAM server is unavailable")

        r = requests.put(parse.urljoin(self.hostname, project_id))

        if r.status_code != 201:
            raise Exception("Project ID could not be created!")

    def upload_input_file(self, file, input_template, project_id):
        """
        Upload an input file for a script, if the input_template of a unique file is already specified to, overwrite this file.

        TODO: We can also deliver files with URL's to the Django server
        :param file: the relative path to the file to upload to the CLAM server
        :param input_template: the input_template on the CLAM server that this file has to be uploaded to
        :param project_id: the project id this input file has to be uploaded to
        :return: None, raises an exception when the project is not found or on unauthorized access
        """
        multipart_form_data = {
            "file": (file, open(file, "r")),
        }

        r = requests.post(
            parse.urljoin(
                parse.urljoin(self.hostname, project_id + "/"), "input"
            ),
            basename(file),
            {"inputtemplate": input_template, "contents": "text-content"},
            files=multipart_form_data,
        )

        check_error_message(r.status_code, project_id)

    def upload_input_files(self, files, project_id):
        """
        Use self.upload_input_file to upload multiple files.

        :param files: a list of tuples (file_path, input_template) specifying all file paths and their corresponding
        input templates
        :param project_id: the project id this input files have to be uploaded to
        :return: None, raises an exception when a file can not be uploaded
        """
        for (file, input_template) in files:
            self.upload_input_file(file, input_template, project_id)

    def run(self, project_id, parameters):
        """
        Run a project.

        TODO: implement parameters
        :param project_id: the project id to start
        :param parameters: the parameters to start the project with
        :return: None, raises an exception when running a project failed
        """
        r = requests.post(parse.urljoin(self.hostname, project_id + "/"))

        check_error_message(r.status_code, project_id)

    def get_output_archive(self, project_id, request_format, file_to_save_to):
        """
        Download the output archive.

        :param project_id: the project id of the project to download the output archive from
        :param request_format: the archive format to download. Either zip, tar.gz or tar.bz2
        :param file_to_save_to: the file to save the archive to, the extension must be the extension specified in
        request_format
        :return: None, raises an exception on an error from the URL request
        """
        r = requests.get(
            parse.urljoin(
                parse.urljoin(self.hostname, project_id + "/"), "output/"
            ),
            params={"format": request_format},
            stream=True,
        )

        check_error_message(r.status_code, project_id)

        with open(file_to_save_to, "wb") as file:
            for chunk in r.iter_content(chunk_size=128):
                file.write(chunk)

    def check_error_message(self, code, project_id):
        """Raise exception."""
        errorlist = [401, 403, 404, 500]
        if code in errorlist:
            raise Exception(
                "Running {} failed! error code: {}".format(project_id, code)
            )


class ClamConfiguration:
    """Interface for a CLAM servers configuration."""

    def __init__(self, hostname, project_id):
        """
        Initialise a ClamConfiguration object, on initialisation the CLAM server is contacted and the XML response is cached in self.clam_xml.

        :param hostname: the hostname of the CLAM server (including the port)
        :param project_id: the project_id of the project on the CLAM server
        """
        self.hostname = hostname
        self.project_id = project_id

        self.clam_xml = None
        if not self.refresh_request_information():
            raise Exception(
                "CLAM server responded with a non-200 status message while getting the CLAM XML file"
            )

        self.namespace = self.get_namespace()

    def get_description(self):
        """
        Find the value stored in the description tag of the CLAM XML file.

        :return: the description of the CLAM server
        """
        return self.clam_xml.find("./description").text

    def get_version(self):
        """
        Find the value stored in the version tag of the CLAM XML file.

        :return: the version of the CLAM server
        """
        return self.clam_xml.find("./version").text

    def get_author(self):
        """
        Find the value stored in the author tag of the CLAM XML file.

        :return: the author of the CLAM server
        """
        return self.clam_xml.find("./author").text

    def get_project_log(self):
        """
        Find the log tags stored in the status tag in the CLAM XML file and reads their content (containing log messages).

        :return: log messages in list format, this function returns a list of strings
        """
        return list(
            reversed([x.text for x in self.clam_xml.find("status").iter("log")])
        )

    def refresh_request_information(self):
        """
        Refresh the CLAM XML document, gets the latest version of the CLAM XML document from the CLAM server.

        :return: True on success, False on failure
        """
        request_information = requests.get(
            parse.urljoin(self.hostname, self.project_id)
        )

        if request_information.status_code != 200:
            return False

        self.clam_xml = ElementTree.fromstring(request_information.text)
        return True

    def get_profiles(self):
        """
        Find the profile tags in the profiles tag in the CLAM XML file.

        :return: all profile tags in a list, this function returns a list of ElementTree elements
        """
        return self.clam_xml.findall("./profiles/profile")

    def get_input_templates(self):
        """
        Find all input templates for all profiles in the CLAM XML file.

        :return: a list of a list specifying per profile all template input files and their attributes
        """
        profiles = self.get_profiles()
        return [
            [y.attrib for y in x.findall("./input/InputTemplate")]
            for x in profiles
        ]

    def get_output_templates(self):
        """
        Find all output templates for all profiles in the CLAM XML file.

        :return: a list of a list specifying per profile all template output files and their attributes
        """
        profiles = self.get_profiles()
        return [
            [y.attrib for y in x.findall("./output/OutputTemplate")]
            for x in profiles
        ]

    def get_input_files(self):
        """
        Find all input files in the CLAM XML file.

        :return: a list of dictionaries, each dictionary being an input file. Each dictionary will have two keys, 'name'
        specifying the name of the file and 'href' specifying the file's location on the CLAM server
        """
        files = self.clam_xml.findall("./input/file")
        # TODO: This should work with namespaces
        return [
            {
                "name": x.find("name").text,
                "href": x.attrib["{http://www.w3.org/1999/xlink}href"],
            }
            for x in files
        ]

    def get_output_files(self):
        """
        Find all output files in the CLAM XML file.

        :return: a list of dictionaries, each dictionary being an output file. Each dictionary will have two keys,
        'name' specifying the name of the file and 'href' specifying the file's location on the CLAM server
        """
        files = self.clam_xml.findall("./output/file")
        # TODO: This should work with namespaces
        return [
            {
                "name": x.find("name").text,
                "href": x.attrib["{http://www.w3.org/1999/xlink}href"],
            }
            for x in files
        ]

    def get_namespace(self):
        """
        Return the namespace of the XML file.

        TODO: This function must be implemented to work on all XML files
        :return: a dictionary containing the XML variables in the XML file
        """
        return {"xlink": "http://www.w3.org/1999/xlink"}

    def get_parameter_groups(self):
        """
        Find all parameter groups with their parameters.

        :return: a list containing a dictionary per parameter, each dictionary object has a 'name' key, specifying the
        name of the parameter group and a 'parameter' key specifying a list of parameters. These parameters are also
        dictionaries specifying their description, name, etc.
        """
        parameter_groups = self.clam_xml.findall("./parameters/parametergroup")
        return [
            {
                "name": x.attrib["name"],
                "parameters": [
                    {**{"tag": y.tag}, **y.attrib} for y in x.findall("*")
                ],
            }
            for x in parameter_groups
        ]
