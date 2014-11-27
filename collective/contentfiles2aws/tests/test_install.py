import unittest2

from Products.CMFCore.utils import getToolByName

from collective.contentfiles2aws.testing import \
    AWS_CONTENT_FILES_INTEGRATION_TESTING


class InstallTestCase(unittest2.TestCase):
    """ Test case for installation tests. """

    layer = AWS_CONTENT_FILES_INTEGRATION_TESTING

    # TODO: add more installation tests.

    def test_properties(self):
        """ Checks that all properties were installed."""

        prop_names = ('AWS_KEY_ID', 'AWS_SEECRET_KEY', 'AWS_BUCKET_NAME',
                      'AWS_FILENAME_PREFIX', 'ALTERNATIVE_CDN_DOMAIN')

        portal = self.layer['portal']
        properties = getToolByName(portal, 'portal_properties')
        sheet = getattr(properties, 'contentfiles2aws', None)

        self.assert_(sheet)

        for name in prop_names:
            self.assertIsNotNone(sheet.getProperty(name, None),
                                 msg='Missed %s property.' % name)


def test_suite():
    suite = unittest2.TestSuite()
    suite.addTest(unittest2.makeSuite(InstallTestCase))
    return suite
