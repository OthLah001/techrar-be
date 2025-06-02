from celery import shared_task

from apps.campaigns.models import Campaign, Notification, Provider


@shared_task
def send_campaign_notifications_task(campaign: Campaign, recipients: list[str]):
    provider: Provider = campaign.provider
    if not provider:
        campaign.status = Campaign.StatusTypes.FAILED
        campaign.save()
        return

    for recipient in recipients:
        notification = Notification.objects.create(
            campaign=campaign,
            recipient=recipient
        )

        try:
            message_id: str | None = None

            # Ensure recipient starts with '+'
            if campaign.channel in [Campaign.ChannelTypes.SMS, Campaign.ChannelTypes.WHATSAPP] and not recipient.startswith('+'):
                recipient = f"+{recipient}"

            # TWILIO Provider Logic
            if provider.provider_type == Provider.ProviderTypes.TWILIO:
                if campaign.channel == Campaign.ChannelTypes.WHATSAPP and Campaign.ChannelTypes.WHATSAPP in provider.channel:
                    from apps.campaigns.utils.send_provider_notifications import send_twilio_whatsapp_notification
                    message_id, error_message = send_twilio_whatsapp_notification(provider, recipient, campaign.message)

                elif campaign.channel == Campaign.ChannelTypes.SMS and Campaign.ChannelTypes.SMS in provider.channel:
                    from apps.campaigns.utils.send_provider_notifications import send_twilio_sms_notification
                    message_id, error_message = send_twilio_sms_notification(provider, recipient, campaign.message)

                else:
                    notification.error_message = f"Unsupported channel type {campaign.channel} for provider {provider.name}"

                if message_id:
                    notification.message_sid = message_id
                    check_message_status_task.apply_async((notification,), countdown=10) # Fetch status after 10 seconds
                else:
                    notification.send_status = Notification.StatusTypes.FAILED
                    notification.error_message = error_message if error_message else "Failed to send message"

            # SENDGRID Provider Logic
            elif provider.provider_type == Provider.ProviderTypes.SENDGRID:
                if campaign.channel == Campaign.ChannelTypes.EMAIL and Campaign.ChannelTypes.EMAIL in provider.channel:
                    from apps.campaigns.utils.send_provider_notifications import send_sendgrid_email_notification
                    send_sendgrid_email_notification(provider, recipient, campaign.merchant.email, campaign.subject, campaign.message)
                    notification.status = Notification.StatusTypes.SENT

                else:
                    notification.error_message = f"Unsupported channel type {campaign.channel} for provider {provider.name}"

        except Exception as e:
            notification.status = Notification.StatusTypes.FAILED
            notification.error_message = str(e)
        finally:
            notification.save()
    
    campaign.status = Campaign.StatusTypes.SENT
    campaign.save()

@shared_task
def check_message_status_task(notification: Notification):
    if not notification.message_sid:
        return
    
    provider = notification.campaign.provider
    if not provider:
        return
    
    if provider.provider_type == Provider.ProviderTypes.TWILIO:
        from apps.campaigns.utils.check_provider_notifications_status import check_twilio_notification_status
        check_twilio_notification_status(notification)