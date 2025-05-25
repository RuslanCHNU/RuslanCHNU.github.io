import random
import numpy as np
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from django.utils import timezone
from campaigns.models import Campaign
from sklearn.cluster import KMeans

class Command(BaseCommand):
    help = 'Генерація аналітичних графіків для кампаній'

    def handle(self, *args, **options):
        now = timezone.now()
        campaigns = list(Campaign.objects.all())

        self.generate_eta_plot(campaigns, now)
        self.generate_rate_plot(campaigns, now)
        self.generate_cluster_plot(campaigns)
        self.generate_recommendation_plots(campaigns)

    def generate_eta_plot(self, campaigns, now):
        etas = []
        for c in campaigns:
            days_elapsed = max((now - c.created_at).days, 1)
            remaining = max(c.goal - c.saved, 0)
            
            if remaining == 0:
                est = 0
            else:
                worst_rate = 10.0 if c.saved <= 0 else (c.saved / days_elapsed) * 0.15
                est = remaining / worst_rate
                est = max(1, min(est, 365))
                est += est * random.uniform(-0.1, 0.1)
            etas.append(est)

        plt.figure()
        plt.hist(etas, bins=20, color='skyblue', edgecolor='black')
        plt.title("Розподіл прогнозованих днів до завершення")
        plt.xlabel("Дні")
        plt.ylabel("Кількість кампаній")
        plt.tight_layout()
        plt.show()
        plt.close()

    def generate_rate_plot(self, campaigns, now):
        rates = []
        for c in campaigns:
            days_elapsed = max((now - c.created_at).days, 1)
            hist_rate = 0 if c.saved <= 0 else c.saved / days_elapsed
            rates.append(hist_rate)

        plt.figure()
        plt.hist(rates, bins=20, color='salmon', edgecolor='black')
        plt.title("Розподіл історичної швидкості збору коштів")
        plt.xlabel("Гривень на день")
        plt.ylabel("Кількість кампаній")
        plt.tight_layout()
        plt.show()
        plt.close()

    def generate_cluster_plot(self, campaigns):
        rem_values = np.array([[c.goal - c.saved] for c in campaigns if not c.is_closed])
        
        if len(rem_values) >= 3:
            km = KMeans(n_clusters=3, random_state=42).fit(rem_values)
            centers = km.cluster_centers_.flatten()
            labels = km.labels_

            plt.figure(figsize=(10, 6))
            plt.scatter(range(len(rem_values)), rem_values.flatten(), c=labels, cmap='viridis')
            for center in centers:
                plt.hlines(
                    center, 
                    xmin=0, 
                    xmax=len(rem_values)-1, 
                    colors='red', 
                    linestyles='dashed'
                )
            plt.title("Залишкові суми та центри кластерів KMeans")
            plt.xlabel("Індекс кампанії")
            plt.ylabel("Залишкова сума (грн)")
            plt.tight_layout()
            plt.show()
            plt.close()

    def generate_recommendation_plots(self, campaigns):
        from campaigns.ml.recommendation import recommend_tiers
        
        min_recs, mid_recs, big_recs = [], [], []
        recs = recommend_tiers()
        
        for c in campaigns:
            tier = recs[c.id]
            min_recs.append(tier['min'])
            mid_recs.append(tier['mid'])
            big_recs.append(tier['big'])

        self._plot_single_tier(min_recs, "мінімального")
        self._plot_single_tier(mid_recs, "середнього")
        self._plot_single_tier(big_recs, "високого")

    def _plot_single_tier(self, data, tier_name):
        plt.figure()
        plt.hist(data, bins=20, color='lightgreen', edgecolor='black')
        plt.title(f"Розподіл рекомендацій для {tier_name} рівня")
        plt.xlabel("Сума (грн)")
        plt.ylabel("Кількість кампаній")
        plt.tight_layout()
        plt.show()
        plt.close()