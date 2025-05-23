from django.contrib import admin
from django import forms
from .models import DonationSite, Campaign
from .scraper import scrape_campaign

class CampaignAdminForm(forms.ModelForm):
    scrape_on_save = forms.BooleanField(
        required=False,
        label="Scrape data on save",
        help_text="Automatically scrape this campaign immediately after saving."
    )

    class Meta:
        model = Campaign
        fields = ['site', 'name', 'goal', 'saved', 'image_url', 'external_url', 'is_closed', 'scrape_on_save']

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignAdminForm
    list_display = ('name', 'site', 'goal', 'saved', 'is_closed')
    list_filter = ('site', 'is_closed')
    actions = ['action_scrape_now']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if form.cleaned_data.get('scrape_on_save'):
            try:
                scrape_campaign(obj)
                self.message_user(request, "Campaign scraped successfully.")
            except Exception as e:
                self.message_user(request, f"Error scraping campaign: {e}", level='error')

    def action_scrape_now(self, request, queryset):
        for camp in queryset:
            scrape_campaign(camp)
        self.message_user(request, "Selected campaigns have been scraped.")
    action_scrape_now.short_description = "Scrape selected campaigns now"

@admin.register(DonationSite)
class DonationSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'created_at')
