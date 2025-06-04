from django.db import models

from config.utils.models import BaseModel
from django.contrib.postgres.fields import ArrayField


class Template(BaseModel):
    name = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.name


class Campaign(BaseModel):
    class ChannelTypes(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        PUSH = 'push', 'Push Notification'
        WHATSAPP = 'whatsapp', 'WhatsApp'

    class StatusTypes(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SCHEDULED = 'scheduled', 'Scheduled'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    name = models.CharField(max_length=255)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE)
    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True)
    provider = models.ForeignKey('Provider', on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=50, choices=ChannelTypes.choices, default=ChannelTypes.EMAIL)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=StatusTypes.choices, default=StatusTypes.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Provider(BaseModel):
    class ProviderTypes(models.TextChoices):
        TWILIO = 'twilio', 'Twilio'
        SENDGRID = 'sendgrid', 'SendGrid'

    name = models.CharField(max_length=255, unique=True)
    provider_type = models.CharField(max_length=50, choices=ProviderTypes.choices, default=ProviderTypes.TWILIO)
    channel = ArrayField(models.CharField(max_length=50, choices=Campaign.ChannelTypes.choices), default=list)
    config = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} ({self.provider_type})"


class Notification(BaseModel):
    class StatusTypes(models.TextChoices):
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'
        PENDING = 'pending', 'Pending'

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='notifications')
    recipient = models.CharField(max_length=255)
    message_sid = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=StatusTypes.choices, default=StatusTypes.PENDING)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.campaign.name} to {self.recipient} ({self.status})"