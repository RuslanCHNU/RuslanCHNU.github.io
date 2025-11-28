import random
import numpy as np
from sklearn.cluster import KMeans
from campaigns.models import Campaign

AVG_MONTHLY_SALARY_UAH = 15000
WORKING_DAYS_PER_MONTH = 22
HOURS_PER_DAY = 8
AVG_HOURLY_WAGE = AVG_MONTHLY_SALARY_UAH / (WORKING_DAYS_PER_MONTH * HOURS_PER_DAY)  # ~85₴/h

def recommend_tiers():
    all_camps = list(Campaign.objects.all())
    open_camps = [c for c in all_camps if not c.is_closed]
    rem_values = np.array([[max(c.goal - c.saved, 0)] for c in open_camps])

    if len(rem_values) >= 3:
        kmeans = KMeans(n_clusters=3, random_state=42).fit(rem_values)
        centers = kmeans.cluster_centers_.flatten()
        c_min, c_max = centers.min(), centers.max()
        if c_max - c_min > 0:
            norm_centers = [ (c - c_min) / (c_max - c_min) + 0.5 for c in centers ]
        else:
            norm_centers = [1.0 for _ in centers]
    else:
        norm_centers = [0.6, 1.0, 1.4]
        kmeans = None

    recs = {}
    for c in all_camps:
        if not c.is_closed and kmeans is not None:
            cluster = kmeans.predict([[max(c.goal - c.saved, 0)]])[0]
            factor = norm_centers[cluster]
        else:
            factor = norm_centers[1]  # середній фактор за замовчуванням

        base_min = AVG_HOURLY_WAGE * random.uniform(0.2, 0.8)
        base_mid = AVG_HOURLY_WAGE * random.uniform(3, 5)
        base_big = AVG_HOURLY_WAGE * random.uniform(8, 12)

        def jitter(val):
            return int(round(val * factor * random.uniform(0.9, 1.1)))

        recs[c.id] = {
            'min': max(10, jitter(base_min)),
            'mid': max(10, jitter(base_mid)),
            'big': max(10, jitter(base_big)),
        }

    return recs
