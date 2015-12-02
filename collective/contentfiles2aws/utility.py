from zope.interface import implements
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

from collective.contentfiles2aws.client import AWSFileClient, FSFileClient
from collective.contentfiles2aws.interfaces import IFileStorageUtility
from collective.contentfiles2aws import config


class FileStorageUtility(object):

    """ File storage utility.

    For more information please see interface definition.

    """

    implements(IFileStorageUtility)

    def _get_settings(self):
        """ Collects settings. """

        pp = getToolByName(getSite(), "portal_properties")
        awsconf_sheet = getattr(pp, config.AWSCONF_SHEET)

        return dict([(pname.lower(), awsconf_sheet.getProperty(pname))
                     for pname in config.AWS_CONF_PROP_NAMES])

    def _parse_metadata(self, metadata):
        """ Parse metadata lines.

        Parse metadata lines and returns metadata dictionary.
        Metadata lines that are not properly formatted (without separator)
        will be ignored.

        :param metadata: metadata strings
        :type metadata: list
        :returns: dict
        """

        return dict([row.split("|") for row in metadata
                     if row.find("|") != -1])

    def _get_bucket_name(self):
        return self._get_settings()['aws_bucket_name']

    def _get_filename_prefix(self):
        return self._get_settings()['aws_filename_prefix']

    def _get_alt_domain(self):
        return self._get_settings()['alt_domain']

    def _get_domain(self):
        """ Gets domain.

        If alt domain is specified then it will return it. Otherwise
        default s3 domain will be build.
        """

        if self.active():
            domain = self._get_alt_domain()
            if not domain:
                settings = self._get_settings()
                active_storage = settings[config.ACTIVE_STORAGE_PNAME.lower()]
                if active_storage == config.AWS_STORAGE:
                    domain = "%s.%s" % (
                        self._get_bucket_name(),
                        self.get_file_client().connection.server)

            return domain

    def get_url_prefix(self):
        """ Build url prefix.

        This url prefix includes domain (cdn or default) and file name prefix
        if it was specified in aws configuration.
        """

        if self.active():
            domain = self._get_domain()
            if domain:
                url = "http://%s" % domain

                prefix = self._get_filename_prefix()
                if prefix:
                    settings = self._get_settings()
                    storage = settings[config.ACTIVE_STORAGE_PNAME.lower()]
                    if storage == config.AWS_STORAGE:
                        url = '%s/%s' % (url, prefix)

                return url

    def get_source_url(self, source_id):
        """ Build source url based on source id.


        :param source_id: source file name
        :type source_id: string
        """

        if self.active():
            prefix = self.get_url_prefix()
            if prefix:
                return "%s/%s" % (prefix, source_id)

    def active(self):
        """ Checks if file storage is active.

        Checks configuration and return false if remote storages is disabled.
        If file system storage is enabled or aws storage is enabled returns
        true.
        """

        settings = self._get_settings()
        active_storage = settings[config.ACTIVE_STORAGE_PNAME.lower()]
        return active_storage in config.STORAGES

    def get_file_client(self):
        """ Provides file client.

        Checks current settings and provide file client accordingly.
        """

        client = None
        settings = self._get_settings()
        active_storage = settings[config.ACTIVE_STORAGE_PNAME.lower()]

        if active_storage == config.AWS_STORAGE:
            client = AWSFileClient(
                settings["aws_key_id"],
                settings["aws_secret_key"],
                settings["aws_bucket_name"],
                aws_filename_prefix=settings["aws_filename_prefix"],
                default_metadata=self._parse_metadata(
                    settings["default_metadata"]))
        elif active_storage == config.FS_STORAGE:
            client = FSFileClient(settings["fs_storage_path"])

        return client


fsutility = FileStorageUtility()
