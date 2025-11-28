from django.db import models

class DonationSite(models.Model):
    name               = models.CharField(max_length=100)
    domain             = models.URLField(unique=True)

    selector_name      = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="CSS selector to extract campaign name"
    )
    selector_goal      = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="CSS selector to extract the goal amount"
    )
    selector_saved     = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="CSS selector to extract the saved amount"
    )
    selector_image     = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="CSS selector to extract image URL"
    )
 
    
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    site         = models.ForeignKey(
        DonationSite,
        on_delete=models.CASCADE,
        related_name='campaigns'
    )
    name         = models.CharField(max_length=255)
    goal         = models.BigIntegerField(help_text="Total target in UAH")
    saved        = models.BigIntegerField(help_text="Amount already collected in UAH")
    image_url    = models.URLField(blank=True, null=True)
    external_url = models.URLField(help_text="Original donation page URL")
    is_closed    = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.site.name})"



from django.utils import timezone

class CampaignSnapshot(models.Model):
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.CASCADE,
        related_name='snapshots'
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    saved = models.BigIntegerField()
    goal = models.BigIntegerField()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['campaign', 'timestamp']),
        ]

    def __str__(self):
        return f"Snapshot(campaign={self.campaign_id}, saved={self.saved}, ts={self.timestamp.isoformat()})"
