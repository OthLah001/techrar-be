from apps.merchants.utils import create_jwt_token
from ninja import NinjaAPI, Schema
from pydantic import EmailStr
from django.utils import timezone
from django.shortcuts import get_object_or_404

from config.utils.errors import NinjaError
from apps.merchants.models import Merchant

merchants_api = NinjaAPI(urls_namespace="merchants")

# Set custom exception handler
@merchants_api.exception_handler(NinjaError)
def handle_elham_error(request, exc: NinjaError):
    return merchants_api.create_response(
        request,
        {"error_name": exc.error_name, "message": exc.message},
        status=exc.status_code,
    )


##### Login Merchant Start #####

class LoginInSchema(Schema):
    email: EmailStr
    password: str

class LoginOutSchema(Schema):
    token: str
    name: str
    email: EmailStr
    mobile: str

@merchants_api.post("login/", response=LoginOutSchema)
def merchant_login(request, data: LoginInSchema):
    merchant = Merchant.objects.filter(email=data.email).first()

    if merchant is None or not merchant.check_password(data.password):
        raise NinjaError(
            error_name="invalid_credentials",
            message="Invalid email or password",
            status_code=401,
        )

    token = create_jwt_token(merchant.id)
    return {
        "token": token,
        "name": merchant.name,
        "email": merchant.email,
        "mobile": merchant.mobile,
    }

##### Login Merchant End #####