import React, { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Typography } from "@mui/material";
import ChartTooltip from "./ChartTooltip";

function formatShort(n) {
  if (n == null || isNaN(n)) return "";
  const abs = Math.abs(n);
  if (abs >= 1_000_000_000) return (n / 1_000_000_000).toFixed(1) + "B";
  if (abs >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (abs >= 1_000) return (n / 1_000).toFixed(1) + "k";
  return Math.round(n).toString();
}

function makeBins(values = [], binCount = 12) {
  if (!values || values.length === 0) return [];
  const arr = values.map((v) => Number(v) || 0);
  const max = Math.max(...arr);
  const min = Math.min(...arr);
  const range = max - min || 1;
  const binSize = range / binCount;
  const bins = Array.from({ length: binCount }, (_, i) => ({
    rawLow: Math.round(min + i * binSize),
    rawHigh: Math.round(min + (i + 1) * binSize),
    name: `${formatShort(Math.round(min + i * binSize))}–${formatShort(Math.round(min + (i + 1) * binSize))}`,
    count: 0,
  }));
  arr.forEach((v) => {
    let idx = Math.floor((v - min) / binSize);
    if (idx < 0) idx = 0;
    if (idx >= binCount) idx = binCount - 1;
    bins[idx].count += 1;
  });
  return bins;
}

export default function EtaHistogram({ data = [], binCount = 12, height = 250 }) {
  const bins = useMemo(() => makeBins(data, binCount), [data, binCount]);

  if (!data || data.length === 0)
    return <Typography>Немає даних для гістограми</Typography>;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={bins}>
        <XAxis dataKey="name" interval={0} tick={{ fontSize: 12 }} />
        <YAxis />
        <Tooltip
          content={<ChartTooltip unit="дні" desc="Прогнозована кількість днів до завершення кампаній (істина — орієнтовна)" />}
        />
        <Bar dataKey="count" />
      </BarChart>
    </ResponsiveContainer>
  );
}
