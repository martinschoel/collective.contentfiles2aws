import os
import unittest2
import tempfile

from collective.contentfiles2aws.client import FSFileClient


class FSFileClientTestCase(unittest2.TestCase):
    """ Test case for AWS Utility."""

    def test_init(self):
        client = FSFileClient("/tmp/storage_path")
        self.assert_(isinstance(client, FSFileClient))
        self.assertEqual(client.storage_path, "/tmp/storage_path")

    def test_get(self):
        storage_bucket = tempfile.mkdtemp()
        fd, fpath = tempfile.mkstemp(prefix="tfile",
                                     dir=storage_bucket,
                                     text=True)
        os.write(fd, "file")
        os.close(fd)

        client = FSFileClient(storage_bucket)
        self.assertIsNone(client.get("notexists"))
        self.assertEqual(client.get(os.path.split(fpath)[-1]), "file")

    def test_put(self):
        storage_bucket = tempfile.mkdtemp()
        client = FSFileClient(storage_bucket)

        client.put("tfile", "file")

        fpath = os.path.join(storage_bucket, "tfile")
        self.assert_(os.path.isfile(fpath))
        self.assertEqual(open(fpath, "r").read(), "file")

    def test_delete(self):
        storage_bucket = tempfile.mkdtemp()
        fd, fpath = tempfile.mkstemp(prefix="tfile",
                                     dir=storage_bucket,
                                     text=True)
        os.write(fd, "file")
        os.close(fd)

        client = FSFileClient(storage_bucket)
        client.delete("notexisted")

        self.assert_(os.path.isfile(fpath))

        client.delete(os.path.split(fpath)[-1])
        self.assert_(not os.path.isfile(fpath))

    def test_copy_source(self):
        storage_bucket = tempfile.mkdtemp()
        fd, fpath = tempfile.mkstemp(prefix="tfile",
                                     dir=storage_bucket,
                                     text=True)
        client = FSFileClient(storage_bucket)
        client.copy_source(os.path.split(fpath)[-1], "new_tfile")

        self.assert_(os.path.isfile(fpath))
        self.assert_(os.path.isfile(os.path.join(storage_bucket, "new_tfile")))

        # clean up
        client.delete("new_tfile")
        self.assert_(not os.path.isfile(os.path.join(storage_bucket,
                                                     "new_tfile")))


def test_suite():
    suite = unittest2.TestSuite()
    suite.addTest(unittest2.makeSuite(FSFileClientTestCase))
    return suite
