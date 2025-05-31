from django.test import TestCase, Client
from django.urls import reverse
from apps.campaigns.models import Template
from apps.merchants.models import Merchant
from apps.merchants.utils import create_jwt_token

class TemplatesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.templates_url = "/api/templates/"

        self.merchant = Merchant.objects.create(
            email="merchant@example.com",
            name="Test Merchant",
            mobile="+212612345678",
            password="secret123"
        )

        self.template1 = Template.objects.create(name="Welcome", body="Welcome body")
        self.template2 = Template.objects.create(name="Promo", body="Promo body")

        self.token = create_jwt_token(self.merchant.id)

    def test_list_templates_authenticated(self):
        # Act
        response = self.client.get(
            self.templates_url,
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

        names = [t["name"] for t in data]
        self.assertIn("Welcome", names)
        self.assertIn("Promo", names)

    def test_list_templates_unauthenticated(self):
        # Act
        response = self.client.get(self.templates_url)

        # Assert
        self.assertEqual(response.status_code, 401)
