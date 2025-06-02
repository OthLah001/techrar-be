from twilio.rest import Client

from apps.campaigns.models import Provider


def send_twilio_whatsapp_notification(
    provider: Provider | None,
    recipient: str,
    message_body: str,
) -> str | None:
    if provider is None:
        return None

    account_sid = provider.config.get('account_sid')
    auth_token =  provider.config.get('auth_token')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=f"whatsapp:{provider.config.get('whatsapp_number')}",
        body=message_body,
        to=f'whatsapp:{recipient}'
    )

    return message.sid if message.sid else None, message.error_message

def send_twilio_sms_notification(
    provider: Provider | None,
    recipient: str,
    message_body: str,
) -> str | None:
    if provider is None:
        return None

    account_sid = provider.config.get('account_sid')
    auth_token = provider.config.get('auth_token')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=provider.config.get('sms_number'),
        body=message_body,
        to=recipient
    )

    return message.sid if message.sid else None, message.error_message

def send_sendgrid_email_notification(
    provider: Provider | None,
    recipient: str,
    sender_email: str,
    subject: str,
    message_body: str,
) -> str | None:
    if provider is None:
        return None

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=sender_email,
        to_emails=recipient,
        subject=subject or "",
        html_content=message_body
    )

    sg = SendGridAPIClient(provider.config.get('api_key'))
    response = sg.send(message)
    print(response.status_code, response.body, response.headers)
    return None