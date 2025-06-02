from apps.campaigns.models import Campaign
from pydantic import AwareDatetime
from apps.campaigns.tasks import send_campaign_notifications_task
from apps.campaigns.utils.send_provider_notifications import send_twilio_whatsapp_notification
from config.utils.authentication import auth_bearer
from ninja import NinjaAPI, Schema, File, Form
from ninja.pagination import paginate
from ninja.files import UploadedFile
import csv
from io import StringIO
from django.db import transaction

from config.utils.errors import NinjaError


campaigns_api = NinjaAPI(urls_namespace="campaigns", auth=auth_bearer)


# Set custom exception handler
@campaigns_api.exception_handler(NinjaError)
def handle_elham_error(request, exc: NinjaError):
    return campaigns_api.create_response(
        request,
        {"error_name": exc.error_name, "message": exc.message},
        status=exc.status_code,
    )


##### Campaigns List Start #####

class CampaignSchema(Schema):
    id: int
    name: str
    provider_name: str | None
    channel: Campaign.ChannelTypes
    status: Campaign.StatusTypes
    scheduled_at: AwareDatetime | None = None

    @staticmethod
    def resolve_provider_name(obj: Campaign) -> str:
        return obj.provider.name if obj.provider else None

@campaigns_api.get("/", response=list[CampaignSchema])
@paginate
def list_campaigns(request):
    """
    List all campaigns.
    """
    campaigns_qs = Campaign.objects.order_by("-created_at").select_related("provider")
    return campaigns_qs

##### Campaigns List End #####

##### Campaigns Create Start #####

class CampaignInSchema(Schema):
    name: str
    template_id: int
    provider_id: int
    channel: Campaign.ChannelTypes
    message: str
    scheduled_at: AwareDatetime | None = None

@campaigns_api.post("/", response=CampaignSchema)
@transaction.atomic
def create_campaign(
    request, 
    name: str = Form(...),
    template_id: int = Form(...),
    provider_id: int = Form(...),
    channel: Campaign.ChannelTypes = Form(...),
    subject: str | None = Form(None),
    message: str = Form(...),
    scheduled_at: AwareDatetime | None = Form(None),
    recipients_file: UploadedFile = File(...)
):
    """
    Create a new campaign.
    """
    # Validate recipients_file type (csv)
    if not recipients_file.name.endswith('.csv') or recipients_file.content_type != 'text/csv':
        raise NinjaError(message="Invalid file type. Please upload a CSV file.", status_code=400, error_name="invalid_file_type")
    
    # Fetch recipients email or mobile numbers from the file and validate them
    try:
        content = recipients_file.read().decode('utf-8')
        reader = csv.DictReader(StringIO(content))

        row_name = "email" if channel == Campaign.ChannelTypes.EMAIL else "mobile"
        recipients = [row[row_name] for row in reader if row_name in row and row[row_name]]

        if len(recipients) == 0 or not all(recipients):
            raise NinjaError(message="No valid recipients found in the file.", status_code=400, error_name="invalid_recipients")
    except Exception as e:
        raise NinjaError(message=f"Error reading file: {str(e)}", status_code=400, error_name="file_read_error")
    
    try:
        campaign = Campaign.objects.create(
            name=name,
            merchant=request.merchant,
            template_id=template_id,
            provider_id=provider_id,
            channel=channel,
            subject=subject,
            message=message,
            scheduled_at=scheduled_at,
            status=Campaign.StatusTypes.SCHEDULED if scheduled_at else Campaign.StatusTypes.DRAFT
        )

        if channel not in campaign.provider.channel:
            raise Exception(f"Channel {channel} is not supported by the provider {campaign.provider.name}")

        if scheduled_at:
            transaction.on_commit(lambda: send_campaign_notifications_task.apply_async((campaign, recipients), eta=scheduled_at))
        else:
            transaction.on_commit(lambda: send_campaign_notifications_task.delay(campaign, recipients))
    except Exception as e:
        raise NinjaError(message=f"Error creating campaign: {str(e)}", status_code=500, error_name="campaign_creation_error")
    
    return campaign

##### Campaigns Create End #####