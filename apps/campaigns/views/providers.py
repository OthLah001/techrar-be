from apps.campaigns.models import Provider
from config.utils.authentication import auth_bearer
from ninja import NinjaAPI, Schema

from config.utils.errors import NinjaError


providers_api = NinjaAPI(urls_namespace="providers", auth=auth_bearer)


# Set custom exception handler
@providers_api.exception_handler(NinjaError)
def handle_elham_error(request, exc: NinjaError):
    return providers_api.create_response(
        request,
        {"error_name": exc.error_name, "message": exc.message},
        status=exc.status_code,
    )


##### Providers List Start #####

class ProviderSchema(Schema):
    id: int
    name: str
    provider_type: str
    channel: list[str]

@providers_api.get("/", response=list[ProviderSchema])
def list_providers(request):
    templates_qs = Provider.objects.all()
    return templates_qs

###### Providers List End #####