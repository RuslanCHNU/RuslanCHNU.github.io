// frontend/src/components/ChartTooltip.jsx
import React from "react";
import { Box, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";

/**
 * Універсальний тултіп для Recharts.
 * payload[0].payload очікується у форматі:
 *  - для гістограм: { name: "0–10", count: 5, rawLow, rawHigh }
 *  - для scatter: { x, y, id, cluster }
 *
 * Props:
 *  - active, payload, label (передає Recharts)
 *  - unit: рядок (наприклад "грн/день" або "дні")
 *  - desc: короткий опис (виводиться зверху)
 */
export default function ChartTooltip({ active, payload, label, unit = "", desc = "" }) {
  const theme = useTheme();

  if (!active || !payload || payload.length === 0) return null;

  const p = payload[0];
  const data = p.payload || {};

  // Якщо це гістограма (має count або name)
  if (typeof data.count !== "undefined" || data.name) {
    const name = data.name ?? label ?? "";
    const count = data.count ?? p.value ?? 0;
    return (
      <Box sx={{ p: 1, bgcolor: "background.paper", boxShadow: 3, borderRadius: 1, minWidth: 220 }}>
        {desc && <Typography variant="subtitle2" sx={{ mb: 0.5 }}>{desc}</Typography>}
        <Typography variant="body2">Діапазон: <strong>{name}</strong></Typography>
        <Typography variant="body2">Кількість кампаній: <strong>{count}</strong></Typography>
        <Typography variant="caption" color="text.secondary">Одиниця: {unit || "—"}</Typography>
      </Box>
    );
  }

  // Якщо це scatter (має y та/або cluster)
  if (typeof data.y !== "undefined") {
    const id = data.id ?? data.campaignId ?? label ?? "—";
    const cluster = data.cluster ?? "—";
    const yVal = data.y;
    return (
      <Box sx={{ p: 1, bgcolor: "background.paper", boxShadow: 3, borderRadius: 1, minWidth: 220 }}>
        {desc && <Typography variant="subtitle2" sx={{ mb: 0.5 }}>{desc}</Typography>}
        <Typography variant="body2">Кампанія: <strong>{id}</strong></Typography>
        <Typography variant="body2">Залишок: <strong>{Number(yVal).toLocaleString()} ₴</strong></Typography>
        <Typography variant="body2">Кластер: <strong>{cluster}</strong></Typography>
        <Typography variant="caption" color="text.secondary">Одиниця: {unit || "грн"}</Typography>
      </Box>
    );
  }

  // fallback
  return (
    <Box sx={{ p: 1, bgcolor: "background.paper", boxShadow: 3, borderRadius: 1 }}>
      <Typography variant="body2">Значення: {p.value}</Typography>
      <Typography variant="caption" color="text.secondary">Одиниця: {unit || "—"}</Typography>
    </Box>
  );
}
