import random
from django.utils import timezone
from campaigns.models import Campaign


def predict_times():
    predictions = {}
    now = timezone.now()

    for campaign in Campaign.objects.all():
        days_elapsed = max((now - campaign.created_at).days, 1)
        remaining = max(campaign.goal - campaign.saved, 0)

        if remaining == 0:
            estimate = 0  
        else:
            if campaign.saved <= 0:
                worst_rate = 10.0
            else:
                historical_rate = campaign.saved / days_elapsed
                worst_rate = historical_rate * 0.15 

            estimate = remaining / worst_rate

            estimate = max(estimate, 1)
            estimate = min(estimate, 365)

            jitter = estimate * random.uniform(-0.1, 0.1)
            estimate += jitter

        predictions[campaign.id] = int(round(estimate))

    return predictions
