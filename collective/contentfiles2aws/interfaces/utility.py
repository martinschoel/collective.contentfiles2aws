from zope.interface import Interface


class IFileStorageUtility(Interface):

    """ File Storage utility.

    Utility provides ability to work with different files clients.
    Currently it supports following file clients:
      * AWS S3 file client.
          This file client allows to store files and images in Amazon
          S3 cloud service.
      * Local file system file client.
          This file client allows to store files in local folder. This
          client is useful for local tests and development.

    Utility checks current settings and provide file client accordingly.
    """

    def active():
        """ Checks if file storage is active.

        Checks configuration and return false if remote storages is disabled.
        If file system storage is enabled or aws storage is enabled returns
        true.
        """

    def get_file_client():
        """ Provides file client.

        Checks current settings and provide file client accordingly.
        """

    def get_source_url(source_id):
        """ Build source url based on source id.


        :param source_id: source file name
        :type source_id: string
        """

    def get_url_prefix():
        """ Build url prefix.

        This url prefix includes domain (alternative or default) and file name
        prefix if it was specified in aws configuration.
        """
