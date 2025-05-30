from django.contrib import admin

from apps.merchants.models import Merchant

# Register your models here.
@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'mobile', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'mobile')
    ordering = ('-id',)
    readonly_fields = ('created_at', 'updated_at')
    