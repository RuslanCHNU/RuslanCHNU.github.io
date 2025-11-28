import statistics
from django.utils import timezone
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import numpy as np
from sklearn.cluster import KMeans

from .models import Campaign, CampaignSnapshot
from .ml import time_predict
from .ml.recommendation import recommend_tiers

CACHE_TTL = 60 * 60  # кеш на 1 годину


def _get_local_rate_for_campaign(campaign, snapshot_window=7):
    now = timezone.now()
    snaps = list(campaign.snapshots.all()[:snapshot_window])  
    if len(snaps) >= 2:
        snaps_chrono = list(reversed(snaps))
        total_delta = 0.0
        total_days = 0.0
        for i in range(1, len(snaps_chrono)):
            prev = snaps_chrono[i - 1]
            cur = snaps_chrono[i]
            delta_money = cur.saved - prev.saved
            delta_days = max((cur.timestamp - prev.timestamp).total_seconds() / 86400.0, 1/24.0)
            total_delta += delta_money
            total_days += delta_days
        if total_days > 0:
            return max(total_delta / total_days, 0.0)
    days_elapsed = max((now - campaign.created_at).days, 1)
    if campaign.saved and campaign.saved > 0 and campaign.goal and campaign.goal > 0:
        return campaign.saved / days_elapsed
    if campaign.saved and campaign.saved > 0:
        return campaign.saved / days_elapsed
    return 0.0


class StatisticsOverview(APIView):
    def get(self, request):
        cache_key = "stats_overview_v1"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        campaigns = list(Campaign.objects.all())
        total = len(campaigns)
        open_qs = Campaign.objects.filter(is_closed=False)
        open_count = open_qs.count()

        avg_progress = 0.0
        if total > 0:
            vals = [ (c.saved / c.goal * 100) for c in campaigns if c.goal and c.goal > 0 ]
            avg_progress = round(sum(vals) / len(vals), 2) if vals else 0.0

        local_rates = []
        for c in open_qs:
            r = _get_local_rate_for_campaign(c)
            local_rates.append(r)
        if local_rates:
            try:
                global_rate = float(statistics.median(local_rates))
            except Exception:
                global_rate = float(sum(local_rates) / len(local_rates))
        else:
            global_rate = 0.0

        now = timezone.now()
        seven_days_ago = now - timezone.timedelta(days=7)
        collected_last_7d = 0.0
        for c in open_qs:
            snaps = list(c.snapshots.all())
            if not snaps:
                r = _get_local_rate_for_campaign(c)
                collected_last_7d += r * 7
                continue
            newest = snaps[0]
            older = None
            for s in snaps:
                if s.timestamp <= seven_days_ago:
                    older = s
                    break
            if older:
                collected_last_7d += max(0, newest.saved - older.saved)
            else:
                days_elapsed = max((now - c.created_at).days, 1)
                r = _get_local_rate_for_campaign(c)
                collected_last_7d += r * min(7, days_elapsed)

        overview = {
            "total_campaigns": total,
            "open_campaigns": open_count,
            "avg_progress_pct": avg_progress,
            "global_rate_median": round(global_rate, 2),
            "collected_last_7d": int(round(collected_last_7d)),
        }
        cache.set(cache_key, overview, CACHE_TTL)
        return Response(overview)


class EtaHistogramView(APIView):
    def get(self, request):
        cache_key = "stats_eta_hist_v1"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        preds = time_predict.predict_times()
        values = list(preds.values())
        cache.set(cache_key, values, CACHE_TTL)
        return Response({"etas": values})


class RateHistogramView(APIView):
    def get(self, request):
        cache_key = "stats_rate_hist_v1"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        rates = []
        for c in Campaign.objects.filter(is_closed=False):
            r = _get_local_rate_for_campaign(c)
            rates.append(r)
        cache.set(cache_key, rates, CACHE_TTL)
        return Response({"rates": rates})


class RemainsClustersView(APIView):
    def get(self, request):
        cache_key = "stats_remains_clusters_v1"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        open_campaigns = list(Campaign.objects.filter(is_closed=False))
        items = []
        rem_values = []
        for c in open_campaigns:
            rem = max(c.goal - c.saved, 0)
            items.append({"id": c.id, "remain": int(rem)})
            rem_values.append([rem])

        result = {"items": items, "labels": [], "centers": []}
        if len(rem_values) >= 3:
            arr = np.array(rem_values)
            try:
                kmeans = KMeans(n_clusters=3, random_state=42).fit(arr)
                labels = kmeans.labels_.tolist()
                centers = [int(round(cc[0])) for cc in kmeans.cluster_centers_]
                for i, it in enumerate(items):
                    it["cluster"] = int(labels[i])
                result["labels"] = labels
                result["centers"] = sorted(centers)
            except Exception as e:
                result["labels"] = [0] * len(items)
                result["centers"] = []
        else:
            result["labels"] = [0] * len(items)
            result["centers"] = []

        cache.set(cache_key, result, CACHE_TTL)
        return Response(result)


class RecommendDistributionView(APIView):
    def get(self, request):
        cache_key = "stats_recommend_dist_v1"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        recs = recommend_tiers()
        mins, mids, bigs = [], [], []
        for cid, v in recs.items():
            mins.append(v.get("min", 0))
            mids.append(v.get("mid", 0))
            bigs.append(v.get("big", 0))
        result = {"min": mins, "mid": mids, "big": bigs}
        cache.set(cache_key, result, CACHE_TTL)
        return Response(result)


class CampaignHistoryView(APIView):
    def get(self, request, pk):
        try:
            c = Campaign.objects.get(pk=pk)
        except Campaign.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        snaps = c.snapshots.all()[:200]
        data = [
            {"timestamp": s.timestamp, "saved": s.saved, "goal": s.goal}
            for s in snaps
        ]
        return Response(data)

from rest_framework.permissions import IsAdminUser

class RecomputeStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        keys = [
            "stats_overview_v1",
            "stats_eta_hist_v1",
            "stats_rate_hist_v1",
            "stats_remains_clusters_v1",
            "stats_recommend_dist_v1",
        ]
        for k in keys:
            cache.delete(k)
        return Response({"detail": "Кеш статистики очищено. Дані будуть перераховані при наступному запиті."})
