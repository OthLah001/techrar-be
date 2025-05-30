from django.db import models
from django.contrib.auth.hashers import make_password, identify_hasher, check_password

from config.utils.models import BaseModel

class Merchant(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)

    def check_password(self, raw_password):
        return identify_hasher(self.password) and check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        try:
            identify_hasher(self.password) # If password is not hashed, this will raise a ValueError
        except ValueError:
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name