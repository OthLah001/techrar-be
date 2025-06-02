import os
import tempfile
import csv
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.merchants.models import Merchant
from apps.merchants.utils import create_jwt_token
from apps.campaigns.models import Campaign, Provider, Template

class CampaignCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/campaigns/"
        self.password = "secret123"

        self.merchant = Merchant.objects.create(
            email="merchant@example.com",
            name="Test Merchant",
            mobile="+212612345678",
            password=self.password
        )
        self.token = create_jwt_token(self.merchant.id)

        self.template = Template.objects.create(name="Promo", body="Use code XYZ")
        self.provider = Provider.objects.create(
            name="Twilio",
            provider_type="twilio",
            channel=["sms", "whatsapp"],
            config={"api_key": "dummy", "auth_key": "dummy"}
        )

    def _upload_file(self, data: list[dict], field_name: str) -> SimpleUploadedFile:
        # Generate a CSV file and wrap it as a SimpleUploadedFile
        csv_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="")
        writer = csv.DictWriter(csv_file, fieldnames=[field_name])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        csv_file.close()
        with open(csv_file.name, "rb") as f:
            file = SimpleUploadedFile("recipients.csv", f.read(), content_type="text/csv")
        os.unlink(csv_file.name)
        return file

    def test_create_campaign_valid_sms(self):
        # Arrange
        file = self._upload_file([{"mobile": "+212600000001"}, {"mobile": "+212600000002"}], "mobile")

        # Act
        response = self.client.post(
            self.url,
            {
                "name": "SMS Campaign",
                "template_id": self.template.id,
                "provider_id": self.provider.id,
                "channel": "sms",
                "message": "Hello there!",
                "recipients_file": file
            },
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "SMS Campaign")

    def test_invalid_file_type(self):
        # Arrange
        file = SimpleUploadedFile("recipients.txt", b"Just text", content_type="text/plain")

        # Act
        response = self.client.post(
            self.url,
            {
                "name": "Invalid File",
                "template_id": self.template.id,
                "provider_id": self.provider.id,
                "channel": "sms",
                "message": "Hey",
                "recipients_file": file
            },
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_name"], "invalid_file_type")

    def test_empty_csv_file(self):
        # Arrange
        file = self._upload_file([], "mobile")

        # Act
        response = self.client.post(
            self.url,
            {
                "name": "Empty Recipients",
                "template_id": self.template.id,
                "provider_id": self.provider.id,
                "channel": "sms",
                "message": "Test",
                "recipients_file": file
            },
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_name"], "file_read_error")

    def test_csv_missing_required_column(self):
        # Arrange
        file = self._upload_file([{"email": "user@example.com"}], "email")  # Wrong field for SMS

        # Act
        response = self.client.post(
            self.url,
            {
                "name": "Missing Mobile",
                "template_id": self.template.id,
                "provider_id": self.provider.id,
                "channel": "sms",
                "message": "Oops",
                "recipients_file": file
            },
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_name"], "file_read_error")

    def test_unauthenticated_create_campaign(self):
        # Arrange
        file = self._upload_file([{"mobile": "+212600000001"}], "mobile")

        # Act
        response = self.client.post(
            self.url,
            {
                "name": "Unauthorized",
                "template_id": self.template.id,
                "provider_id": self.provider.id,
                "channel": "sms",
                "message": "Fail",
                "recipients_file": file
            },
        )

        # Assert
        self.assertEqual(response.status_code, 401)
