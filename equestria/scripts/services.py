import zipfile
import os


def zip_dir(zip_directory, zip_to, ignore=None):
    """
    Zip a directory and all of its contents.

    :param zip_directory: the directory to zip
    :param zip_to: the file to write the zip too.
    :param ignore: a list of files to ignore when zipping, this can either be a relative filename (such as error.log),
    then all error.log files will be ignored, or an absolute filename (such as /var/log/error.log), then this file will
    be ignored
    :return: the file name of the zip archive
    """
    # ziph is zipfile handle
    if ignore is None:
        ignore = list()
    ignore.append(zip_to)

    ziph = zipfile.ZipFile(zip_to, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(zip_directory):
        for file in files:
            if not (os.path.join(root, file) in ignore or file in ignore):
                ziph.write(os.path.join(root, file), os.path.join(os.path.relpath(root, zip_directory), file))
    ziph.close()

    return ziph.filename
