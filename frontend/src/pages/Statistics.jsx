import React, { useState } from "react";
import { Box, Typography,  Paper, Button, Stack } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { useStatistics } from "../hooks/useStatistics";
import OverviewCards from "../components/OverviewCards";
import EtaHistogram from "../components/EtaHistogram";
import RateHistogram from "../components/RateHistogram";
import ClusterScatter from "../components/ClusterScatter";
import { Link as RouterLink } from "react-router-dom";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";

export default function StatisticsPage() {
  const theme = useTheme();
  const {
    overview,
    etaHist,
    rateHist,
    remainsClusters,
    recommendDist,
    isLoading,
    isError,
  } = useStatistics();

  const [selected, setSelected] = useState("eta");

  if (isLoading) return <Typography>Завантаження статистики…</Typography>;
  if (isError) return <Typography>Помилка при завантаженні статистики.</Typography>;

  const handleSelect = (e, v) => {
    if (v) setSelected(v);
  };

  return (
    <Box sx={{ px: 2, py: 2 }}>
      <Box sx={{ position: "relative", mb: 3 }}>
        <Box sx={{ textAlign: "center" }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            Статистика
          </Typography>
        </Box>

        <Box sx={{ position: "absolute", left: 16, top: "50%", transform: "translateY(-50%)" }}>
          <Button component={RouterLink} to="/" variant="outlined" color="primary">
            Назад
          </Button>
        </Box>
      </Box>

      <OverviewCards data={overview.data} sx={{ mb: 3 }} />

      <Stack direction="row" spacing={1} sx={{ mb: 2, justifyContent: "center" }}>
        <ToggleButtonGroup value={selected} exclusive onChange={handleSelect}>
          <ToggleButton
            value="eta"
            sx={{
              "&.Mui-selected": {
                backgroundColor: theme.palette.primary.main,
                color: "#fff",
              },
              "&.Mui-selected:hover": {
                backgroundColor: theme.palette.primary.dark,
              },
            }}
          >
            Прогноз (дні)
          </ToggleButton>

          <ToggleButton
            value="rate"
            sx={{
              "&.Mui-selected": {
                backgroundColor: theme.palette.primary.main,
                color: "#fff",
              },
              "&.Mui-selected:hover": {
                backgroundColor: theme.palette.primary.dark,
              },
            }}
          >
            Швидкість (₴/день)
          </ToggleButton>

          <ToggleButton
            value="remains"
            sx={{
              "&.Mui-selected": {
                backgroundColor: theme.palette.primary.main,
                color: "#fff",
              },
              "&.Mui-selected:hover": {
                backgroundColor: theme.palette.primary.dark,
              },
            }}
          >
            Залишки + KMeans
          </ToggleButton>

          <ToggleButton
            value="recs"
            sx={{
              "&.Mui-selected": {
                backgroundColor: theme.palette.primary.main,
                color: "#fff",
              },
              "&.Mui-selected:hover": {
                backgroundColor: theme.palette.primary.dark,
              },
            }}
          >
            Рекомендації
          </ToggleButton>
        </ToggleButtonGroup>
      </Stack>

      <Box>
        <Paper sx={{ p: 2, mb: 2 }}>
          {selected === "eta" && <EtaHistogram data={etaHist.data ?? []} height={480} />}
          {selected === "rate" && <RateHistogram data={rateHist.data ?? []} height={480} />}
          {selected === "remains" && <ClusterScatter data={remainsClusters.data} height={480} />}
            {selected === "recs" && recommendDist.data && (
            <Box>
                <Typography variant="subtitle1">Мінімальні</Typography>
                <RateHistogram
                data={recommendDist.data.min ?? []}
                height={230}
                unit="грн"
                desc="Рекомендована мінімальна сума пожертви: кількість кампаній в кожному діапазоні сум."
                />
                <Typography variant="subtitle1">Середні</Typography>
                <RateHistogram
                data={recommendDist.data.mid ?? []}
                height={230}
                unit="грн"
                desc="Рекомендована середня сума пожертви: кількість кампаній в кожному діапазоні сум."
                />
                <Typography variant="subtitle1">Великі</Typography>
                <RateHistogram
                data={recommendDist.data.big ?? []}
                height={230}
                unit="грн"
                desc="Рекомендована велика сума пожертви: кількість кампаній в кожному діапазоні сум."
                />
            </Box>
            )}

        </Paper>
      </Box>

    </Box>
  );
}
