from zope.interface import implements
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

from collective.contentfiles2aws.client import AWSFileClient, FSFileClient
from collective.contentfiles2aws.interfaces import IAWSFileClientUtility
from collective.contentfiles2aws.config import AWSCONF_SHEET


class AWSFileClientUtility(object):
    """
    """
    implements(IAWSFileClientUtility)

    def active(self):
        pp = getToolByName(getSite(), 'portal_properties')
        awsconf_sheet = getattr(pp, AWSCONF_SHEET)
        return awsconf_sheet.getProperty('USE_AWS')

    def get_configuration(self):
        """ Collect configuration infomation for aws client. """
        # TODO: temporary we will save configuration in property sheet.
        #      it will be good to have more flexible solution for this.
        pp = getToolByName(getSite(), "portal_properties")
        awsconf_sheet = getattr(pp, AWSCONF_SHEET)
        aws_key_id = awsconf_sheet.getProperty("AWS_KEY_ID")
        aws_seecret_key = awsconf_sheet.getProperty("AWS_SEECRET_KEY")
        aws_bucket_name = awsconf_sheet.getProperty("AWS_BUCKET_NAME")
        aws_filename_prefix = awsconf_sheet.getProperty("AWS_FILENAME_PREFIX")
        use_local_storage = awsconf_sheet.getProperty("USE_LOCAL_STORAGE")
        local_storage_path = awsconf_sheet.getProperty("LOCAL_STORAGE_PATH")
        alt_cdn_domain = awsconf_sheet.getProperty(
            "ALTERNATIVE_CDN_DOMAIN", None)

        return {"aws_key_id": aws_key_id,
                "aws_seecret_key": aws_seecret_key,
                "aws_bucket_name": aws_bucket_name,
                "aws_filename_prefix": aws_filename_prefix,
                'cdn_domain': alt_cdn_domain,
                "use_local_storage": use_local_storage,
                "local_storage_path": local_storage_path}

    def get_bucket_name(self):
        return self.get_configuration()['aws_bucket_name']

    def get_filename_prefix(self):
        return self.get_configuration()['aws_filename_prefix']

    def get_file_client(self):
        """ Provide an aws file client. """
        config = self.get_configuration()
        if config["use_local_storage"]:
            client = FSFileClient(config["local_storage_path"])
        else:
            client = AWSFileClient(
                config["aws_key_id"],
                config["aws_seecret_key"],
                config["aws_bucket_name"],
                aws_filename_prefix=config["aws_filename_prefix"])
        return client

    def get_alt_cdn_domain(self):
        return self.get_configuration()['cdn_domain']

    def get_domain(self):
        """ Gets domain.

        If cdn domain is specified then it will return it. Otherwise
        default s3 domain will be build.
        """

        domain = self.get_alt_cdn_domain()
        if not domain:
            domain = "%s.%s" % (self.get_bucket_name(),
                                self.get_file_client().connection.server)

        return domain

    def get_url_prefix(self):
        """ Build url prefix.

        This url prefix includes domain (cdn or default) and file name prefix
        if it was specified in aws configuration.
        """
        url = "http://%s" % self.get_domain()
        prefix = self.get_filename_prefix()
        if prefix:
                url = '%s/%s' % (url, prefix)

        return url

    def get_source_url(self, source_id):
        """ Build source url based on source id.


        :param source_id: source file name
        :type source_id: string
        """

        return "%s/%s" % (self.get_url_prefix(), source_id)

aws_utility = AWSFileClientUtility()
