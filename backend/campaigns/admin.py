from django.contrib import admin, messages
from django import forms
from .models import DonationSite, Campaign, CampaignSnapshot
from .scraper import scrape_campaign, scrape_saved_field

@admin.register(CampaignSnapshot)
class CampaignSnapshotAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'timestamp', 'saved', 'goal')
    list_filter = ('campaign',)
    search_fields = ('campaign__name',)
    ordering = ('-timestamp',)


class CampaignAdminForm(forms.ModelForm):
    scrape_on_save = forms.BooleanField(
        required=False,
        label="Автоматично оновити з сайту при збереженні",
        help_text="Якщо вибрано — після збереження запис автоматично спробує отримати актуальні дані з зовнішньої сторінки."
    )

    class Meta:
        model = Campaign
        fields = ['site', 'name', 'goal', 'saved', 'image_url', 'external_url', 'is_closed', 'scrape_on_save']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignAdminForm
    list_display = ('name', 'site', 'goal', 'saved', 'is_closed')
    list_filter = ('site', 'is_closed')
    actions = ['action_scrape_now', 'action_scrape_saved']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if form.cleaned_data.get('scrape_on_save'):
            try:
                # повний скрейп (оновлює name, goal, saved, image_url)
                scrape_campaign(obj)
                # після успішного оновлення saved — створюємо снепшот
                try:
                    CampaignSnapshot.objects.create(
                        campaign=obj,
                        saved=obj.saved,
                        goal=obj.goal
                    )
                    self.message_user(request, "Кампанію оновлено та збережено снепшот.", level=messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Кампанію оновлено, але не вдалося створити снепшот: {e}", level=messages.WARNING)
            except Exception as e:
                self.message_user(request, f"Помилка при скрейпі кампанії: {e}", level=messages.ERROR)

    def action_scrape_now(self, request, queryset):
        for camp in queryset:
            try:
                scrape_campaign(camp)
                # після повного скрейпу створимо снепшот
                try:
                    CampaignSnapshot.objects.create(
                        campaign=camp,
                        saved=camp.saved,
                        goal=camp.goal
                    )
                except Exception as e:
                    self.message_user(request, f"Кампанію проскраплено, але не створено снепшот для id={camp.id}: {e}", level=messages.WARNING)
            except Exception as e:
                self.message_user(request, f"Не вдалося проскрапити campaign id={camp.id}: {e}", level=messages.ERROR)
        self.message_user(request, "Вибрані кампанії успішно проскраплені.", level=messages.INFO)
    action_scrape_now.short_description = "Оновити всі дані (scrape) для вибраних кампаній"

    def action_scrape_saved(self, request, queryset):
        for camp in queryset:
            try:
                scrape_saved_field(camp)
                try:
                    CampaignSnapshot.objects.create(
                        campaign=camp,
                        saved=camp.saved,
                        goal=camp.goal
                    )
                    self.message_user(request, f"Оновлено 'saved' і створено снепшот для id={camp.id}.", level=messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Оновлено 'saved' для id={camp.id}, але не створено снепшот: {e}", level=messages.WARNING)
            except Exception as e:
                self.message_user(request, f"Не вдалося оновити 'saved' для id={camp.id}: {e}", level=messages.ERROR)
    action_scrape_saved.short_description = "Оновити лише поле 'saved' для вибраних кампаній"

@admin.register(DonationSite)
class DonationSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'created_at')
