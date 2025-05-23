from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from campaigns.views import CampaignViewSet
from campaigns.views import RecommendationView, TimePredictView

router = routers.DefaultRouter()
router.register(r'campaigns', CampaignViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/recommend/', RecommendationView.as_view()),
    path('api/predict-time/', TimePredictView.as_view()),
]
