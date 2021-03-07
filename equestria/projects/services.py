import shutil
from pathlib import Path


def remove_files_from_directory(absolute_path_to_directory):
    """
    Remove all files from a directory.

    :param absolute_path_to_directory: the absolute path to the directory to remove
    """
    shutil.rmtree(absolute_path_to_directory)
    Path(absolute_path_to_directory).mkdir(parents=True, exist_ok=True)


def get_dictionary_files_with_content(project):
    """Get a list of dictionary file ids, names and content."""
    dictionary_files = project.get_dictionary_files()
    dictionary_files_with_content = []
    for file in dictionary_files:
        with file.file.open("r") as f:
            lines = f.read()
            dictionary_files_with_content.append(
                {"id": file.id, "filename": file.filename, "content": lines}
            )
    return dictionary_files_with_content


def update_dictionary_data(project, list_update):
    """Update the content of a dictionary file."""
    dictionary_files = project.get_dictionary_files()
    for dictionary_update in list_update:
        if (
            type(dictionary_update) == dict
            and "content" in dictionary_update.keys()
            and "id" in dictionary_update.keys()
            and type(dictionary_update["content"]) == str
            and type(dictionary_update["id"]) == int
        ):
            for dictionary_file in dictionary_files:
                if dictionary_file.id == dictionary_update["id"]:
                    update_file_contents(
                        dictionary_file, dictionary_update["content"]
                    )


def update_file_contents(file, content):
    """Update the content of a file."""
    with file.file.open("w") as f:
        f.write(content)
