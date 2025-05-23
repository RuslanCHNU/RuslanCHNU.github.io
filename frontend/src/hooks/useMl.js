import { useQuery } from "@tanstack/react-query";
import { api } from "../api";

export function useCampaigns() {
  return useQuery({
    queryKey: ["campaigns"],
    queryFn: () => api.get("campaigns/").then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });
}

export function useRecommendations() {
  return useQuery({
    queryKey: ["recommend"],
    queryFn: () => api.get("recommend/").then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });
}

export function useTimePredictions() {
  return useQuery({
    queryKey: ["predict-time"],
    queryFn: () => api.get("predict-time/").then((res) => res.data),
    staleTime: 5 * 60 * 1000,
  });
}
