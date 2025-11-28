from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from campaigns.views import CampaignViewSet
from campaigns.views import RecommendationView, TimePredictView
from campaigns.views_stats import (
    StatisticsOverview, EtaHistogramView, RateHistogramView,
    RemainsClustersView, RecommendDistributionView, CampaignHistoryView
)
from campaigns.views_stats import RecomputeStatisticsView

router = routers.DefaultRouter()
router.register(r'campaigns', CampaignViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/recommend/', RecommendationView.as_view()),
    path('api/predict-time/', TimePredictView.as_view()),
    path('api/statistics/overview/', StatisticsOverview.as_view(), name='stats-overview'),
    path('api/statistics/eta_hist/', EtaHistogramView.as_view(), name='stats-eta-hist'),
    path('api/statistics/rate_hist/', RateHistogramView.as_view(), name='stats-rate-hist'),
    path('api/statistics/remains_clusters/', RemainsClustersView.as_view(), name='stats-remains-clusters'),
    path('api/statistics/recommend_dist/', RecommendDistributionView.as_view(), name='stats-recommend-dist'),
    path('api/campaigns/<int:pk>/history/', CampaignHistoryView.as_view(), name='campaign-history'),
    path('api/statistics/recompute/', RecomputeStatisticsView.as_view(), name='stats-recompute'),
]
