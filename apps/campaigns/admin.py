from django.contrib import admin

from apps.campaigns.models import Campaign, Provider, Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-id',)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-id',)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'merchant', 'channel', 'status', 'scheduled_at', 'created_at', 'updated_at')
    search_fields = ('name', 'merchant__name')
    list_filter = ('channel', 'status', 'merchant')
    ordering = ('-id',)