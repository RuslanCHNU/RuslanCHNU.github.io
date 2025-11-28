import React, { useState, useMemo } from "react";
import { Link as RouterLink } from "react-router-dom";
import Button from "@mui/material/Button";

import {
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  useMediaQuery,
} from "@mui/material";
import {
  useCampaigns,
  useRecommendations,
  useTimePredictions,
} from "./hooks/useMl";
import DonationCard from "./components/DonationCard";
import FilterSelect from "./components/FilterSelect";
import { useTheme } from "@mui/material/styles";

export default function App() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const { data: campaigns = [], isLoading: loadingCamp } = useCampaigns();
  const { data: recs = {}, refetch: refetchRecs } = useRecommendations();
  const { data: times = {} } = useTimePredictions();

  const [mode, setMode] = useState("progress");
  const [customValue, setCustomValue] = useState("");
  const [recTier, setRecTier] = useState("min");
  const [lastSpecial, setLastSpecial] = useState({
    type: "recommend",
    tier: "min",
    value: null,
  });

  const handleModeChange = (newMode) => {
    setMode(newMode);
    if (newMode === "recommend") {
      setLastSpecial({ type: "recommend", tier: recTier, value: null });
    } else if (newMode === "custom" && customValue) {
      const val = parseInt(customValue, 10);
      setLastSpecial({
        type: "custom",
        tier: null,
        value: isNaN(val) ? null : val,
      });
    }
  };

  const handleTierSelect = (tier) => {
    if (recTier === tier) refetchRecs();
    else setRecTier(tier);
    setLastSpecial({ type: "recommend", tier, value: null });
    setMode("recommend");
  };

  const handleCustomChange = (val) => {
    setCustomValue(val);
    const num = parseInt(val, 10);
    if (!isNaN(num)) {
      setLastSpecial({ type: "custom", tier: null, value: num });
      setMode("custom");
    }
  };

  const filtered = useMemo(() => {
    if (!Array.isArray(campaigns)) return [];
    if (mode === "closed") {
      return campaigns.filter((c) => c.is_closed);
    }
    return campaigns.filter((c) => !c.is_closed);
  }, [campaigns, mode]);

  const sorted = useMemo(() => {
    const arr = [...filtered];
    switch (mode) {
      case "furthest":
        return arr.sort((a, b) => (times[b.id] || 0) - (times[a.id] || 0));
      case "progress":
        return arr.sort((a, b) => b.progress_pct - a.progress_pct);
      default:
        return arr;
    }
  }, [filtered, times, mode]);

  if (loadingCamp) return <Typography>Loading campaigns…</Typography>;

  return (
    <Box>
      <Box
        sx={{
          position: "relative",
          width: "100%",
          backgroundColor: theme.palette.primary.light,
          py: 2,
          mb: 2,
        }}
      >
        <Box sx={{ textAlign: "center" }}>
          <Typography variant="h4" color="white" sx={{ fontWeight: "700" }}>
            Агрегатор зборів
          </Typography>
        </Box>

        <Box
          sx={{
            position: "absolute",
            right: 16,
            top: "50%",
            transform: "translateY(-50%)",
          }}
        >
          <Button
            component={RouterLink}
            to="/stats"
            sx={{
              backgroundColor: "transparent",
              color: "rgba(255,255,255,0.9)",
              boxShadow: "none",
              textTransform: "none",
              "&:hover": {
                backgroundColor: "rgba(255,255,255,0.92)",
                color: theme.palette.primary.main,
                boxShadow: 3,
              },
            }}
          >
            Статистика
          </Button>
        </Box>
      </Box>

      <Box sx={{ px: 2 }}>
        <Stack
          direction={isMobile ? "column" : "row"}
          alignItems={isMobile ? "flex-start" : "center"}
          justifyContent={isMobile ? "flex-start" : "center"}
          spacing={2}
          sx={{ mb: 2 }}
        >
          <FilterSelect
            mode={mode}
            onChange={handleModeChange}
            sx={{ width: isMobile ? "100%" : 200 }}
          />

          {mode === "recommend" && (
            <FormControl
              size="small"
              sx={{ width: isMobile ? "100%" : 200, ml: isMobile ? 0 : 2 }}
            >
              <InputLabel id="tier-label">Варіанти</InputLabel>
              <Select
                labelId="tier-label"
                value={recTier}
                label="Tier"
                onChange={(e) => handleTierSelect(e.target.value)}
              >
                <MenuItem value="min">Мала сума</MenuItem>
                <MenuItem value="mid">Середня сума</MenuItem>
                <MenuItem value="big">Велика сума</MenuItem>
              </Select>
            </FormControl>
          )}

          {mode === "custom" && (
            <TextField
              label="Введіть число (₴)"
              variant="outlined"
              size="small"
              value={customValue}
              onChange={(e) => handleCustomChange(e.target.value)}
              sx={{ width: isMobile ? "100%" : 200, ml: isMobile ? 0 : 2 }}
            />
          )}
        </Stack>

        <Box
          sx={{
            display: "flex",
            flexWrap: "wrap",
            gap: 2,
            justifyContent: "center",
          }}
        >
          {sorted.map((c) => {
            let amount;
            if (lastSpecial.type === "custom" && lastSpecial.value != null)
              amount = lastSpecial.value;
            else if (lastSpecial.type === "recommend")
              amount = recs[c.id]?.[lastSpecial.tier] ?? recs[c.id]?.mid;
            else if (mode === "progress")
              amount = recs[c.id]?.mid ?? c.goal - c.saved;
            else amount = recs[c.id]?.mid;

            return (
              <DonationCard
                key={c.id}
                campaign={c}
                recommendation={amount}
                etaDays={times[c.id] ?? null}
              />
            );
          })}
        </Box>
      </Box>
    </Box>
  );
}
