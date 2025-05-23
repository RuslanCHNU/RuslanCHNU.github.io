from django.shortcuts import render

from rest_framework import viewsets
from .models import Campaign
from .serializers import CampaignSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .ml.recommendation import recommend_tiers
from .ml.time_predict import predict_times

class RecommendationView(APIView):
    def get(self, request):
        recs = recommend_tiers()
        return Response(recs)

class TimePredictView(APIView):
    def get(self, request):
        times = predict_times()
        return Response(times)

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    filterset_fields = ['is_closed']

