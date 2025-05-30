from django.test import TestCase, Client
from django.urls import reverse
from apps.merchants.models import Merchant

class MerchantLoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/merchants/login/"
        self.password = "secret123"
        self.merchant = Merchant.objects.create(
            email="merchant@example.com",
            name="Test Merchant",
            mobile="+212612345678",
            password=self.password
        )

    def test_login_success(self):
        # Arrange
        payload = {
            "email": self.merchant.email,
            "password": self.password
        }

        # Act
        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["email"], self.merchant.email)
        self.assertEqual(data["name"], self.merchant.name)
        self.assertEqual(data["mobile"], self.merchant.mobile)

    def test_login_invalid_password(self):
        payload = {
            "email": self.merchant.email,
            "password": "wrongpass"
        }

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["message"], "Invalid email or password")

    def test_login_invalid_email(self):
        payload = {
            "email": "nonexistent@example.com",
            "password": "whatever"
        }

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["message"], "Invalid email or password")

    def test_login_missing_fields(self):
        payload = {
            "email": self.merchant.email
            # missing password
        }

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("password", str(response.json()))
