from django.core.management.base import BaseCommand, CommandError
from campaigns.models import Campaign
from campaigns.scraper import scrape_campaign

class Command(BaseCommand):
    help = 'Scrape all active campaigns (or by ID) to update saved/goal/name/image.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='If provided, only scrape the campaign with this ID.'
        )

    def handle(self, *args, **options):
        if options['id']:
            try:
                camp = Campaign.objects.get(pk=options['id'])
            except Campaign.DoesNotExist:
                raise CommandError(f"Campaign ID={options['id']} not found.")
            self.stdout.write(f"Scraping Campaign ID={camp.id}…")
            scrape_campaign(camp)
            self.stdout.write(self.style.SUCCESS("✔ Done."))
        else:
            qs = Campaign.objects.filter(is_closed=False)
            total = qs.count()
            self.stdout.write(f"Scraping {total} campaigns…")
            for idx, camp in enumerate(qs, 1):
                self.stdout.write(f"[{idx}/{total}] {camp.external_url}")
                try:
                    scrape_campaign(camp)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✖ Failed: {e}"))
            self.stdout.write(self.style.SUCCESS("All done."))
