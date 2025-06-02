from django.test import TestCase, Client
from apps.merchants.models import Merchant
from apps.merchants.utils import create_jwt_token
from apps.campaigns.models import Provider

class ProvidersTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/providers/"
        
        self.merchant = Merchant.objects.create(
            email="merchant@example.com",
            name="Test Merchant",
            mobile="+212612345678",
            password="secret123"
        )
        self.token = create_jwt_token(self.merchant.id)

        self.provider1 = Provider.objects.create(
            name="Twilio",
            provider_type="twilio",
            channel=["sms", "whatsapp"],
            config={"api_key": "abc", "auth_key": "xyz"}
        )
        self.provider2 = Provider.objects.create(
            name="SendGrid",
            provider_type="sendgrid",
            channel=["email"],
            config={"api_key": "123", "auth_key": "456"}
        )

    def test_list_providers_authenticated(self):
        # Act
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

        names = [p["name"] for p in data]
        self.assertIn("Twilio", names)
        self.assertIn("SendGrid", names)

    def test_list_providers_unauthenticated(self):
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 401)
