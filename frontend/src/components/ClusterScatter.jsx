// frontend/src/components/ClusterScatter.jsx
import React from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import ChartTooltip from "./ChartTooltip";

function shortNumber(v) {
  if (v == null || isNaN(v)) return "";
  const abs = Math.abs(v);
  if (abs >= 1_000_000_000) return (v / 1_000_000_000).toFixed(1) + "B";
  if (abs >= 1_000_000) return (v / 1_000_000).toFixed(1) + "M";
  if (abs >= 1_000) return (v / 1_000).toFixed(1) + "k";
  return v.toLocaleString();
}

export default function ClusterScatter({ data, height = 300 }) {
  const theme = useTheme();

  if (!data || !data.items) return <Typography>Немає даних кластерів</Typography>;

  const items = data.items.map((it, idx) => ({
    x: idx,
    y: it.remain,
    cluster: it.cluster ?? 0,
    id: it.id,
  }));

  const centers = (data.centers || []).map((c) => Number(c));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart>
        <CartesianGrid />
        <XAxis dataKey="x" name="index" tickCount={8} />
        <YAxis dataKey="y" name="remain" tickFormatter={shortNumber} />
        <Tooltip
          content={<ChartTooltip unit="грн" desc="Залишкова сума до мети: скільки гривень потрібно ще зібрати." />}
        />
        {centers.map((center, i) => (
          <ReferenceLine
            key={`center-${i}`}
            y={center}
            stroke={theme.palette.primary.main}
            strokeDasharray="6 6"
            strokeOpacity={0.95}
            strokeWidth={2}
          />
        ))}
        <Scatter name="campaigns" data={items} fill={theme.palette.primary.light || "#8884d8"} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
