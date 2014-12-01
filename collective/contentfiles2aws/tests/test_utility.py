import unittest2

from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from collective.contentfiles2aws.client import AWSFileClient
from collective.contentfiles2aws.interfaces import IAWSFileClientUtility
from collective.contentfiles2aws.config import AWSCONF_SHEET
from collective.contentfiles2aws.testing import \
    AWS_CONTENT_FILES_INTEGRATION_TESTING


class AWSUtilityTestCase(unittest2.TestCase):
    """ Test case for AWS Utility."""

    layer = AWS_CONTENT_FILES_INTEGRATION_TESTING

    configuration = [
        {'id': 'AWS_KEY_ID',
         'name': 'aws_key_id',
         'value': 'key_id'},
        {'id': 'AWS_SEECRET_KEY',
         'name': 'aws_seecret_key',
         'value': 'aws_seecret_key'},
        {'id': 'AWS_BUCKET_NAME',
         'name': 'aws_bucket_name',
         'value': 'aws_bucket_name'},
        {'id': 'AWS_FILENAME_PREFIX',
         'name': 'aws_filename_prefix',
         'value': 'filename/prefix'},
        {'id': 'ALTERNATIVE_CDN_DOMAIN',
         'name': 'cdn_domain',
         'value': 'cdn.choosehelp.com'}]

    def setUp(self):
        self.utility = getUtility(IAWSFileClientUtility)
        self.pp = getToolByName(self.layer['portal'], 'portal_properties')
        self.conf_sheet = getattr(self.pp, AWSCONF_SHEET)
        for conf in self.configuration:
            self.conf_sheet._updateProperty(conf['id'], conf['value'])

    def test_active(self):
        """ Checks if active method gets correct property."""
        self.conf_sheet._updateProperty('USE_AWS', False)
        self.assert_(not self.utility.active())

        self.conf_sheet._updateProperty('USE_AWS', True)
        self.assert_(self.utility.active())

    def test_get_configuration(self):
        """ Checks if configuration dict contains correct properties."""

        aws_conf = self.utility.get_configuration()
        for conf in self.configuration:
            self.assertEqual(aws_conf[conf['name']], conf['value'])

    def test_get_bucket_name(self):
        """ Check bucket name. """

        self.assertEqual([c['value'] for c in self.configuration
                          if c['id'] == 'AWS_BUCKET_NAME'][0],
                         self.utility.get_bucket_name())

    def test_get_filename_prefix(self):
        """ Check filename prefix. """

        self.assertEqual([c['value'] for c in self.configuration
                          if c['id'] == 'AWS_FILENAME_PREFIX'][0],
                         self.utility.get_filename_prefix())

    def test_get_file_client(self):
        """ Checks if method returns client object."""

        self.assertIsInstance(self.utility.get_file_client(),
                              AWSFileClient)

    def tes_get_alt_cdn_domain(self):
        """ Check alternative cdn domain. """
        self.assertEqual([c['value'] for c in self.configuration
                          if c['id'] == 'ALTERNATIVE_CDN_DOMAIN'][0],
                         self.utility.get_alt_cdn_domain())

    def test_get_domain(self):
        """ Test for get_domain utility method."""

        self.conf_sheet._updateProperty('ALTERNATIVE_CDN_DOMAIN', '')
        self.assertEqual(self.utility.get_domain(),
                         'aws_bucket_name.s3.amazonaws.com')

        self.conf_sheet._updateProperty('ALTERNATIVE_CDN_DOMAIN', 'cdn.ch.com')
        self.assertEqual(self.utility.get_domain(), 'cdn.ch.com')

    def test_get_url_prefix(self):
        """ Checks that url prefix. """

        self.conf_sheet._updateProperty('ALTERNATIVE_CDN_DOMAIN', '')
        self.conf_sheet._updateProperty('AWS_FILENAME_PREFIX', '')
        self.assertEqual(self.utility.get_url_prefix(),
                         'http://aws_bucket_name.s3.amazonaws.com')

        self.conf_sheet._updateProperty('AWS_FILENAME_PREFIX', 'fprefix')
        self.assertEqual(self.utility.get_url_prefix(),
                         'http://aws_bucket_name.s3.amazonaws.com/fprefix')

        self.conf_sheet._updateProperty('ALTERNATIVE_CDN_DOMAIN', 'cdn.ch.com')
        self.assertEqual(self.utility.get_url_prefix(),
                         'http://cdn.ch.com/fprefix')

    def test_get_source_url(self):
        self.conf_sheet._updateProperty('ALTERNATIVE_CDN_DOMAIN', '')
        self.conf_sheet._updateProperty('AWS_FILENAME_PREFIX', '')
        self.assertEqual(self.utility.get_source_url('source_id'),
                         'http://aws_bucket_name.s3.amazonaws.com/source_id')

        self.conf_sheet._updateProperty('AWS_FILENAME_PREFIX', 'fprefix')
        self.assertEqual(
            self.utility.get_source_url('source_id'),
            'http://aws_bucket_name.s3.amazonaws.com/fprefix/source_id')

        self.conf_sheet._updateProperty('ALTERNATIVE_CDN_DOMAIN', 'cdn.ch.com')
        self.assertEqual(self.utility.get_source_url('source_id'),
                         'http://cdn.ch.com/fprefix/source_id')


def test_suite():
    suite = unittest2.TestSuite()
    suite.addTest(unittest2.makeSuite(AWSUtilityTestCase))
    return suite
