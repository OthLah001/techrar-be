def create_jwt_token(user_id: int):
    from django.conf import settings
    import jwt
    from django.utils import timezone
    import datetime

    payload = {
        "user_id": user_id,
        "exp": timezone.now() + datetime.timedelta(days=30),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")