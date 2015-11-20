import os
import shutil

from zope.interface import implements

from collective.contentfiles2aws.client.interfaces import IFileClient

# TODO: Use correct error types


class FileClientError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class FileClientRetrieveError(FileClientError):
    """ Base Retrieve Error Exception"""
    pass


class FileClientStoreError(FileClientError):
    """ Base Store Error Exception """
    pass


class FileClientRemoveError(FileClientError):
    """ Base Remove Error Exception """
    pass


class FileClientCopyError(FileClientError):
    """ Base Copy Error Exception """
    pass


class FSFileClient(object):
    implements(IFileClient)

    def __init__(self, storage_path):
        self.storage_path = storage_path

    def get(self, filename, **kw):
        """ Get file with specified filename from local storage.

        Search file in local storage and if file with specified name
        exists returns file content.

        :param filename: name of file.
        :type filename: string
        :returns: file content in case file exists,
         ohterwise returns None

        """

        file_path = os.path.join(self.storage_path, filename)
        try:
            file_obj = open(file_path, "r")
        except IOError:
            return
        else:
            return file_obj.read()

    def put(self, filename, data, **kw):
        """Writes file to local storage under provided file name.

        :param filename: name of file.
        :type filename: string
        :param data: file content.
        :type: string: string
        :param kw: dictionary with file metadata
        :type kw: dict
        :returns: None

        """

        file_path = os.path.join(self.storage_path, filename)
        file_obj = open(file_path, "w")
        file_obj.write(data)

    def delete(self, filename, **kw):
        """ Removes file form amazon storage using provided filename.

        :param filename: name of file.
        :type filename: string

        """

        file_path = os.path.join(self.storage_path, filename)

        try:
            os.remove(file_path)
        except OSError:
            pass

    def copy_source(self, filename, new_filename, **kw):
        """ Create a copy of specified file.

        :param filename: source file name
        :type filename: string
        :param new_filename: new file name
        :type new_filename: string

        """

        file_path = os.path.join(self.storage_path, filename)
        new_file_path = os.path.join(self.storage_path, new_filename)
        shutil.copyfile(file_path, new_file_path)
