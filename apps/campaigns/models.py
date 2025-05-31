from django.db import models

from config.utils.models import BaseModel


class Template(BaseModel):
    name = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.name
    

class Provider(BaseModel):
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    config = models.JSONField(default=dict)

    def __str__(self):
        return self.name
    

class Campaign(BaseModel):
    class ChannelTypes(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        PUSH = 'push', 'Push Notification'
        whatsapp = 'whatsapp', 'WhatsApp'

    class StatusTypes(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SCHEDULED = 'scheduled', 'Scheduled'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    name = models.CharField(max_length=255)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=50, choices=ChannelTypes.choices, default=ChannelTypes.EMAIL)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=StatusTypes.choices, default=StatusTypes.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name