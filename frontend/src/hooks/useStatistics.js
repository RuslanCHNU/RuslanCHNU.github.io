import { useQuery } from "@tanstack/react-query";
import { api } from "../api";

export function useStatistics() {
  const overview = useQuery({
    queryKey: ["stats", "overview"],
    queryFn: async () => {
      const { data } = await api.get("statistics/overview/");
      return data;
    },
    staleTime: 1000 * 60 * 5,
  });

  const etaHist = useQuery({
    queryKey: ["stats", "eta_hist"],
    queryFn: async () => {
      const { data } = await api.get("statistics/eta_hist/");
      return data?.etas ?? data ?? [];
    },
    staleTime: 1000 * 60 * 5,
  });

  const rateHist = useQuery({
    queryKey: ["stats", "rate_hist"],
    queryFn: async () => {
      const { data } = await api.get("statistics/rate_hist/");
      return data?.rates ?? data ?? [];
    },
    staleTime: 1000 * 60 * 5,
  });

  const remainsClusters = useQuery({
    queryKey: ["stats", "remains_clusters"],
    queryFn: async () => {
      const { data } = await api.get("statistics/remains_clusters/");
      return data;
    },
    staleTime: 1000 * 60 * 5,
  });

  const recommendDist = useQuery({
    queryKey: ["stats", "recommend_dist"],
    queryFn: async () => {
      const { data } = await api.get("statistics/recommend_dist/");
      return data;
    },
    staleTime: 1000 * 60 * 5,
  });

  return {
    overview,
    etaHist,
    rateHist,
    remainsClusters,
    recommendDist,
    isLoading:
      overview.isLoading ||
      etaHist.isLoading ||
      rateHist.isLoading ||
      remainsClusters.isLoading ||
      recommendDist.isLoading,
    isError:
      overview.isError ||
      etaHist.isError ||
      rateHist.isError ||
      remainsClusters.isError ||
      recommendDist.isError,
  };
}
