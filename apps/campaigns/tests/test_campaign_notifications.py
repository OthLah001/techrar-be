from django.test import TestCase, Client
from apps.merchants.models import Merchant
from apps.merchants.utils import create_jwt_token
from apps.campaigns.models import Campaign, Notification, Provider, Template
from django.utils.timezone import now, timedelta

class CampaignNotificationsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "secret123"
        self.merchant = Merchant.objects.create(
            email="merchant@example.com",
            name="Test Merchant",
            mobile="+212612345678",
            password=self.password
        )
        self.token = create_jwt_token(self.merchant.id)

        self.provider = Provider.objects.create(
            name="Twilio",
            provider_type="twilio",
            channel=["sms"],
            config={"api_key": "dummy", "auth_key": "dummy"}
        )

        self.template = Template.objects.create(name="Reminder", body="Don't forget!")

        self.campaign = Campaign.objects.create(
            name="Notify Campaign",
            merchant=self.merchant,
            template=self.template,
            provider=self.provider,
            channel="sms",
            subject="Campaign Notification",
            message="Hello there!",
            status=Campaign.StatusTypes.SENT
        )

        self.notification1 = Notification.objects.create(
            campaign=self.campaign,
            recipient="+212600000001",
            status=Notification.StatusTypes.SENT,
            created_at=now() - timedelta(minutes=10)
        )

        self.notification2 = Notification.objects.create(
            campaign=self.campaign,
            recipient="+212600000002",
            status=Notification.StatusTypes.FAILED,
            created_at=now()
        )

        self.url = f"/api/campaigns/{self.campaign.id}/notifications/"

    def test_list_campaign_notifications_authenticated(self):
        # Act
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()["items"]
        self.assertEqual(len(data), 2)

        recipients = [n["recipient"] for n in data]
        self.assertIn("+212600000001", recipients)
        self.assertIn("+212600000002", recipients)

    def test_campaign_notifications_unauthenticated(self):
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 401)

    def test_campaign_notifications_not_found(self):
        # Act
        invalid_url = "/api/campaigns/9999/notifications/"
        response = self.client.get(
            invalid_url,
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error_name"], "campaign_not_found")
