import unittest2

from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from collective.contentfiles2aws.client import AWSFileClient, FSFileClient
from collective.contentfiles2aws.interfaces import IFileStorageUtility
from collective.contentfiles2aws.config import AWSCONF_SHEET, \
    ACTIVE_STORAGE_PNAME, AWS_STORAGE, STORAGE_OFF, FS_STORAGE
from collective.contentfiles2aws.testing import \
    AWS_CONTENT_FILES_INTEGRATION_TESTING


class AWSUtilityTestCase(unittest2.TestCase):
    """ Test case for AWS Utility."""

    layer = AWS_CONTENT_FILES_INTEGRATION_TESTING

    settings = [
        {'id': 'AWS_KEY_ID',
         'name': 'aws_key_id',
         'value': 'key_id'},
        {'id': 'AWS_SECRET_KEY',
         'name': 'aws_secret_key',
         'value': 'aws_secret_key'},
        {'id': 'AWS_BUCKET_NAME',
         'name': 'aws_bucket_name',
         'value': 'aws_bucket_name'},
        {'id': 'AWS_FILENAME_PREFIX',
         'name': 'aws_filename_prefix',
         'value': 'filename/prefix'},
        {'id': 'ALT_DOMAIN',
         'name': 'alt_domain',
         'value': 'cdn.choosehelp.com'}]

    def setUp(self):
        self.utility = getUtility(IFileStorageUtility)
        self.pp = getToolByName(self.layer['portal'], 'portal_properties')
        self.conf_sheet = getattr(self.pp, AWSCONF_SHEET)
        for conf in self.settings:
            self.conf_sheet._updateProperty(conf['id'], conf['value'])

    def test_active(self):
        """ Checks if active method gets correct property."""
        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, STORAGE_OFF)
        self.assert_(not self.utility.active())

        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, AWS_STORAGE)
        self.assert_(self.utility.active())

    def test__get_settings(self):
        """ Checks if settings dict contains correct properties."""

        settings = self.utility._get_settings()
        for conf in self.settings:
            self.assertEqual(settings[conf['name']], conf['value'])

    def test__parse_metadata(self):
        """ Test for "_parse_metadata utility method. """

        parse = self.utility._parse_metadata

        self.assertEqual(parse([]), {})

        # test not properly formatted metadata string
        self.assertEqual(parse(["key value"]), {})

        # test with one bad row
        self.assertEqual(parse(["bad string", "Expires|Mon, July 10 2015"]),
                         {"Expires": "Mon, July 10 2015"})

        self.assertEqual(parse(["Cache-Control|max-age=10000",
                                "Expires|Mon, July 10 2015"]),
                         {"Cache-Control": "max-age=10000",
                          "Expires": "Mon, July 10 2015"})

    def test__get_bucket_name(self):
        """ Check bucket name. """

        self.assertEqual([c['value'] for c in self.settings
                          if c['id'] == 'AWS_BUCKET_NAME'][0],
                         self.utility._get_bucket_name())

    def test__get_filename_prefix(self):
        """ Check filename prefix. """

        self.assertEqual([c['value'] for c in self.settings
                          if c['id'] == 'AWS_FILENAME_PREFIX'][0],
                         self.utility._get_filename_prefix())

    def test_get_file_client(self):
        """ Checks if method returns client object."""

        # storage is off by default
        self.assertIsNone(self.utility.get_file_client())

        # now lets turn on storage and select AWS storage type.
        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, AWS_STORAGE)
        self.assertIsInstance(self.utility.get_file_client(), AWSFileClient)

        # now lets check file system storage type
        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, FS_STORAGE)
        self.assertIsInstance(self.utility.get_file_client(), FSFileClient)

    def tes_get_alt_domain(self):
        """ Check alternative cdn domain. """
        self.assertEqual([c['value'] for c in self.settings
                          if c['id'] == 'ALT_DOMAIN'][0],
                         self.utility.get_alt_domain())

    def test__get_domain(self):
        """ Test for get_domain utility method."""

        self.assertIsNone(self.utility._get_domain())

        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, FS_STORAGE)
        self.conf_sheet._updateProperty("ALT_DOMAIN", "")
        self.assert_(not self.utility._get_domain())

        self.conf_sheet._updateProperty("ALT_DOMAIN", "testdomain.com")
        self.assertEqual(self.utility._get_domain(), "testdomain.com")

        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, AWS_STORAGE)
        self.conf_sheet._updateProperty("ALT_DOMAIN", "")
        self.assertEqual(self.utility._get_domain(),
                         "aws_bucket_name.s3.amazonaws.com")

        self.conf_sheet._updateProperty("ALT_DOMAIN", "cdn.ch.com")
        self.assertEqual(self.utility._get_domain(), "cdn.ch.com")

    def test_get_url_prefix(self):
        """ Checks that url prefix. """

        self.assertIsNone(self.utility.get_url_prefix())

        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, FS_STORAGE)
        self.conf_sheet._updateProperty("ALT_DOMAIN", "")
        self.assert_(not self.utility.get_url_prefix())

        self.conf_sheet._updateProperty("ALT_DOMAIN", "testdomain.com")
        self.conf_sheet._updateProperty("AWS_FILENAME_PREFIX", "")
        self.assertEqual(self.utility.get_url_prefix(),
                         "http://testdomain.com")

        self.conf_sheet._updateProperty("AWS_FILENAME_PREFIX", "prefix")
        self.assertEqual(self.utility.get_url_prefix(),
                         "http://testdomain.com")

        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, AWS_STORAGE)
        self.conf_sheet._updateProperty("ALT_DOMAIN", "")
        self.conf_sheet._updateProperty("AWS_FILENAME_PREFIX", "")
        self.assertEqual(self.utility.get_url_prefix(),
                         "http://aws_bucket_name.s3.amazonaws.com")

        self.conf_sheet._updateProperty("AWS_FILENAME_PREFIX", "fprefix")
        self.assertEqual(self.utility.get_url_prefix(),
                         "http://aws_bucket_name.s3.amazonaws.com/fprefix")

        self.conf_sheet._updateProperty("ALT_DOMAIN", "cdn.ch.com")
        self.assertEqual(self.utility.get_url_prefix(),
                         "http://cdn.ch.com/fprefix")

    def test_get_source_url(self):

        self.assertIsNone(self.utility.get_source_url("source_id"))

        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, FS_STORAGE)
        self.conf_sheet._updateProperty("ALT_DOMAIN", "")
        self.assertIsNone(self.utility.get_source_url("source_id"))

        self.conf_sheet._updateProperty("ALT_DOMAIN", "")
        self.conf_sheet._updateProperty("AWS_FILENAME_PREFIX", "")
        self.assertIsNone(self.utility.get_source_url("source_id"))

        self.conf_sheet._updateProperty(ACTIVE_STORAGE_PNAME, AWS_STORAGE)
        self.assertEqual(self.utility.get_source_url('source_id'),
                         'http://aws_bucket_name.s3.amazonaws.com/source_id')

        self.conf_sheet._updateProperty('AWS_FILENAME_PREFIX', 'fprefix')
        self.assertEqual(
            self.utility.get_source_url('source_id'),
            'http://aws_bucket_name.s3.amazonaws.com/fprefix/source_id')

        self.conf_sheet._updateProperty('ALT_DOMAIN', 'cdn.ch.com')
        self.assertEqual(self.utility.get_source_url('source_id'),
                         'http://cdn.ch.com/fprefix/source_id')


def test_suite():
    suite = unittest2.TestSuite()
    suite.addTest(unittest2.makeSuite(AWSUtilityTestCase))
    return suite
