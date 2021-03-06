from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from etools.applications.attachments.models import AttachmentFlat
from etools.applications.attachments.tests.factories import AttachmentFactory, AttachmentFileTypeFactory
from etools.applications.EquiTrack.tests.cases import BaseTenantTestCase


class TestFileType(BaseTenantTestCase):
    def test_str(self):
        instance = AttachmentFileTypeFactory(label='xyz')
        self.assertIn(u'xyz', str(instance))

        instance = AttachmentFileTypeFactory(label='R\xe4dda Barnen')
        self.assertIn('R\xe4dda Barnen', str(instance))


class TestAttachments(BaseTenantTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.simple_object = AttachmentFileTypeFactory()

    def test_str(self):
        instance = AttachmentFactory(
            file=SimpleUploadedFile('simple_file.txt', b'these are the file contents!'),
            content_object=self.simple_object
        )
        self.assertIn('simple_file', str(instance))

        instance = AttachmentFactory(
            file=SimpleUploadedFile('simple_file.txt', u'R\xe4dda Barnen'.encode('utf-8')),
            content_object=self.simple_object
        )
        self.assertIn('simple_file', str(instance))

    def test_filename(self):
        instance = AttachmentFactory(
            file="test.pdf",
            content_object=self.simple_object
        )
        self.assertEqual(instance.filename, "test.pdf")

    def test_filename_hyperlink(self):
        instance = AttachmentFactory(
            hyperlink="http://example.com/test_file.txt",
            content_object=self.simple_object
        )
        self.assertEqual(instance.filename, "test_file.txt")

    def test_valid_file(self):
        valid_file_attachment = AttachmentFactory(
            # Note: file content is intended to be a byte-string here.
            file=SimpleUploadedFile('simple_file.txt', b'these are the file contents!'),
            content_object=self.simple_object
        )
        valid_file_attachment.clean()
        self.assertIsNotNone(valid_file_attachment.file)
        self.assertEqual(valid_file_attachment.url, valid_file_attachment.file.url)

    def test_valid_hyperlink(self):
        valid_hyperlink_attachment = AttachmentFactory(
            hyperlink='http://example.com/test_file.txt', content_object=self.simple_object
        )
        valid_hyperlink_attachment.clean()
        self.assertIsNotNone(valid_hyperlink_attachment.hyperlink)
        self.assertEqual(valid_hyperlink_attachment.url, valid_hyperlink_attachment.hyperlink)

    def test_invalid(self):
        invalid_attachment = AttachmentFactory(content_object=self.simple_object)
        with self.assertRaises(ValidationError):
            invalid_attachment.clean()


class TestAttachmentFlat(BaseTenantTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.simple_object = AttachmentFileTypeFactory()

    def test_str(self):
        attachment = AttachmentFactory(
            file=SimpleUploadedFile('simple_file.txt', u'R\xe4dda Barnen'.encode('utf-8')),
            content_object=self.simple_object
        )
        flat_qs = AttachmentFlat.objects.filter(attachment=attachment)
        self.assertTrue(flat_qs.exists())
        flat = flat_qs.first()
        self.assertEqual(str(flat), str(attachment.file))
