import random
import statistics
from django.utils import timezone
from campaigns.models import Campaign, CampaignSnapshot

ALPHA = 0.6           # вага локального темпу (0..1)
FLOOR_RATE = 10.0     # мінімальна грн/день для розрахунків
MIN_DAYS = 1
MAX_DAYS = 365
JITTER_PCT = 0.10     # ±10% випадковість
SNAPSHOT_WINDOW = 7   # кількість останніх snapshot'ів (або днів) для local_rate

def compute_local_rate_from_snapshots(campaign, window=SNAPSHOT_WINDOW):
    snaps = list(campaign.snapshots.all()[:window])  
    if len(snaps) < 2:
        return None

    snaps_chrono = list(reversed(snaps))
    total_delta = 0
    total_days = 0.0
    for i in range(1, len(snaps_chrono)):
        prev = snaps_chrono[i-1]
        cur = snaps_chrono[i]
        delta_money = cur.saved - prev.saved
        delta_days = max((cur.timestamp - prev.timestamp).total_seconds() / 86400.0, 1/24.0)  
        total_delta += delta_money
        total_days += delta_days

    if total_days <= 0:
        return None
    rate = total_delta / total_days
    # якщо rate <= 0 повернути None (немає росту)
    return rate if rate > 0 else None

def predict_times():
    now = timezone.now()
    predictions = {}

    campaigns = list(Campaign.objects.all())

    local_rates = []
    open_campaigns_info = []  
    for c in campaigns:
        if c.is_closed:
            continue
        # спробувати snapshot-based rate
        rate = compute_local_rate_from_snapshots(c)
        if rate is None:
            days_elapsed = max((now - c.created_at).days, 1)
            rate = (c.saved / days_elapsed) if c.saved and c.saved > 0 else FLOOR_RATE
        if rate <= 0:
            rate = FLOOR_RATE
        local_rates.append(rate)
        open_campaigns_info.append((c, rate))

    if local_rates:
        try:
            global_rate = statistics.median(local_rates)
        except Exception:
            global_rate = sum(local_rates) / len(local_rates)
    else:
        global_rate = FLOOR_RATE
    if global_rate <= 0:
        global_rate = FLOOR_RATE

    for c in campaigns:
        days_elapsed = max((now - c.created_at).days, 1)
        remaining = max(c.goal - c.saved, 0)

        if remaining == 0:
            estimate = 0
        else:
            local_rate = compute_local_rate_from_snapshots(c)
            if local_rate is None:
                local_rate = (c.saved / days_elapsed) if c.saved and c.saved > 0 else FLOOR_RATE
            if local_rate <= 0:
                local_rate = FLOOR_RATE

            effective_rate = ALPHA * local_rate + (1.0 - ALPHA) * global_rate
            effective_rate = max(effective_rate, FLOOR_RATE)

            estimate = remaining / effective_rate if effective_rate > 0 else MAX_DAYS
            estimate = max(estimate, MIN_DAYS)
            estimate = min(estimate, MAX_DAYS)
            jitter = estimate * random.uniform(-JITTER_PCT, JITTER_PCT)
            estimate = estimate + jitter

        predictions[c.id] = int(round(estimate))

    return predictions
