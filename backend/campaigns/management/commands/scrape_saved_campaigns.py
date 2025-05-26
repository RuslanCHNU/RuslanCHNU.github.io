from django.core.management.base import BaseCommand
from campaigns.models import Campaign
from campaigns.scraper import scrape_saved_field

class Command(BaseCommand):
    help = 'Оновлює лише поле "saved" (зібрано) для активних кампаній.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='Якщо вказано, оновити тільки кампанію з цим ID.'
        )

    def handle(self, *args, **options):
        if options['id']:
            try:
                camp = Campaign.objects.get(pk=options['id'])
            except Campaign.DoesNotExist:
                self.stderr.write(f"Кампанія {options['id']} не знайдена.")
                return
            self.stdout.write(f"Оновлюємо 'saved' для Campaign ID={camp.id}…")
            scrape_saved_field(camp)
            self.stdout.write(self.style.SUCCESS("✔ Done."))
        else:
            qs = Campaign.objects.filter(is_closed=False)
            total = qs.count()
            self.stdout.write(f"Оновлюємо 'saved' у {total} активних кампаніях…")
            for idx, camp in enumerate(qs, start=1):
                self.stdout.write(f"[{idx}/{total}] {camp.external_url}")
                try:
                    scrape_saved_field(camp)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✖ Failed: {e}"))
            self.stdout.write(self.style.SUCCESS("Усі saved оновлено."))
