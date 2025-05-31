from apps.campaigns.models import Template
from apps.merchants.utils import create_jwt_token
from config.utils.authentication import auth_bearer
from ninja import NinjaAPI, Schema

from config.utils.errors import NinjaError


templates_api = NinjaAPI(urls_namespace="templates", auth=auth_bearer)


# Set custom exception handler
@templates_api.exception_handler(NinjaError)
def handle_elham_error(request, exc: NinjaError):
    return templates_api.create_response(
        request,
        {"error_name": exc.error_name, "message": exc.message},
        status=exc.status_code,
    )


##### Templates List Start #####

class TemplateSchema(Schema):
    id: int
    name: str
    body: str

@templates_api.get("/", response=list[TemplateSchema])
def list_templates(request):
    templates_qs = Template.objects.all()
    return templates_qs

###### Templates List End #####