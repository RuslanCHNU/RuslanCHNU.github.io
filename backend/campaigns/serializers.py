from rest_framework import serializers
from .models import Campaign

class CampaignSerializer(serializers.ModelSerializer):
    progress_pct = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'site', 'name', 'goal', 'saved',
            'image_url', 'external_url', 'is_closed',
            'progress_pct',
        ]

    def get_progress_pct(self, obj):
        return round(obj.saved / obj.goal * 100, 1) if obj.goal else 0
