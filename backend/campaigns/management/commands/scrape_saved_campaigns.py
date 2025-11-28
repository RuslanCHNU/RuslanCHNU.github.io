import time
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.cache import cache
from campaigns.models import Campaign, CampaignSnapshot
from campaigns.scraper import scrape_saved_field

CACHE_KEYS_TO_INVALIDATE = [
    "stats_overview_v1",
    "stats_eta_hist_v1",
    "stats_rate_hist_v1",
    "stats_remains_clusters_v1",
    "stats_recommend_dist_v1",
]

class Command(BaseCommand):
    help = 'Оновлює лише поле "saved" (зібрано) для активних кампаній та зберігає snapshot. Після завершення інвалідує кеш статистики.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='Якщо вказано, оновити тільки кампанію з цим ID.'
        )
        parser.add_argument(
            '--sleep',
            type=float,
            default=0.5,
            help='Затримка між запитами (секунди).'
        )
        parser.add_argument(
            '--no-invalidate-cache',
            action='store_true',
            help='Не інвалідувати кеш після виконання (для локального тестування).'
        )

    def record_snapshot(self, campaign):
        try:
            CampaignSnapshot.objects.create(
                campaign=campaign,
                timestamp=timezone.now(),
                saved=campaign.saved,
                goal=campaign.goal
            )
            self.stdout.write(self.style.SUCCESS(f"✔ Снепшот створено: campaign={campaign.id}, saved={campaign.saved}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Не вдалося записати снепшот для campaign={campaign.id}: {e}"))

    def invalidate_cache(self):
        for k in CACHE_KEYS_TO_INVALIDATE:
            cache.delete(k)
            self.stdout.write(f"Інвалідація кеша: видалено ключ {k}")

    def handle(self, *args, **options):
        campaign_id = options.get('id')
        sleep_between = float(options.get('sleep') or 0.5)
        no_invalidate = options.get('no_invalidate_cache', False)

        if campaign_id:
            try:
                camp = Campaign.objects.get(pk=campaign_id)
            except Campaign.DoesNotExist:
                raise CommandError(f"Кампанія ID={campaign_id} не знайдена.")
            self.stdout.write(f"Оновлюємо 'saved' для кампанії ID={camp.id} …")
            try:
                scrape_saved_field(camp)
                self.record_snapshot(camp)
                self.stdout.write(self.style.SUCCESS("✔ Готово."))
            except Exception as e:
                raise CommandError(f"Помилка при скрейпі: {e}")

            if not no_invalidate:
                self.invalidate_cache()
            return

        qs = Campaign.objects.filter(is_closed=False)
        total = qs.count()
        self.stdout.write(f"Оновлюємо 'saved' у {total} активних кампаніях…")
        for idx, camp in enumerate(qs, start=1):
            self.stdout.write(f"[{idx}/{total}] {camp.external_url} (id={camp.id})")
            try:
                scrape_saved_field(camp)
                self.record_snapshot(camp)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✖ Невдало: {e}"))
            time.sleep(sleep_between)

        if not no_invalidate:
            self.stdout.write("Інвалідуємо кеш статистики (щоб API віддав свіжі дані)…")
            self.invalidate_cache()
        else:
            self.stdout.write("Пропущено інвалідацію кеша (--no-invalidate-cache).")

        self.stdout.write(self.style.SUCCESS("Усі saved оновлено й снепшоти створено."))
