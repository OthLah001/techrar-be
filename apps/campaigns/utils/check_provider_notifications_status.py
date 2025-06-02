from twilio.rest import Client

from apps.campaigns.models import Notification, Provider


def check_twilio_notification_status(
    notification: Notification
):
    if not notification.message_sid:
        return

    provider: Provider | None = notification.campaign.provider
    if not provider or provider.provider_type != provider.ProviderTypes.TWILIO:
        return

    account_sid = provider.config.get('account_sid')
    auth_token = provider.config.get('auth_token')
    client = Client(account_sid, auth_token)

    try:
        message = client.messages(notification.message_sid).fetch()
        notification.status = (
            Notification.StatusTypes.SENT 
            if not message.error_message
            else Notification.StatusTypes.FAILED
        )
        notification.error_message = message.error_message
        notification.save()
    except Exception as e:
        print(f"Error fetching message status: {e}")