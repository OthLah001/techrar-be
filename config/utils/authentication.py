from apps.merchants.models import Merchant
import jwt
from ninja.security import HttpBearer
from django.conf import settings

from config.utils.errors import NinjaError


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            merchant_id = payload.get("merchant_id")

            if not merchant_id:
                raise NinjaError(
                    error_name="invalid_token", message="Invalid token", status_code=401
                )

            merchant = Merchant.objects.filter(id=merchant_id).first()

            if not merchant:
                raise NinjaError(
                    error_name="merchant_not_found",
                    message="Merchant not found",
                    status_code=404,
                )

            request.merchant = merchant
            return merchant
        except jwt.ExpiredSignatureError:
            raise NinjaError(
                error_name="token_expired", message="Token expired", status_code=401
            )
        except jwt.InvalidTokenError:
            raise NinjaError(
                error_name="invalid_token", message="Invalid token", status_code=401
            )


auth_bearer = AuthBearer()