import React from "react";
import { Grid, Card, CardContent, Typography, Box } from "@mui/material";
import { useTheme } from "@mui/material/styles";

export default function OverviewCards({ data = {}, sx }) {
  const theme = useTheme();
  const {
    total_campaigns = 0,
    open_campaigns = 0,
    avg_progress_pct = 0,
    global_rate_median = 0,
    collected_last_7d = 0,
  } = data || {};

  const cards = [
    { title: "Усього кампаній", value: total_campaigns },
    { title: "Відкриті кампанії", value: open_campaigns },
    { title: "Середній прогрес (%)", value: `${avg_progress_pct}` },
    { title: "Медіанна швидкість (₴/день)", value: `${global_rate_median}` },
    { title: "Зібрано за 7 днів (прибл.)", value: `${collected_last_7d} ₴` },
  ];

  return (
    <Grid container spacing={2} justifyContent="center" sx={sx}>
      {cards.map((c) => (
        <Grid item xs={12} sm={6} md={2} key={c.title} sx={{ display: "flex", justifyContent: "center" }}>
          <Card
            variant="outlined"
            sx={{
              width: "100%",
              minWidth: 180,
              maxWidth: 320,
              transition: "transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease",
              border: `1px solid transparent`,
              "&:hover": {
                transform: "translateY(-6px)",
                boxShadow: 6,
                borderColor: theme.palette.primary.main,
              },
              display: "flex",
              alignItems: "stretch",
            }}
          >
            <CardContent sx={{ width: "100%" }}>
              <Typography variant="subtitle2" color="textSecondary">
                {c.title}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="h6">{c.value}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
