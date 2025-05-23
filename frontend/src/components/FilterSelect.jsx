import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

export default function FilterSelect({ mode, onChange, sx }) {
  return (
    <FormControl variant="outlined" size="small" sx={sx}>
      <InputLabel id="filter-label">Опції</InputLabel>
      <Select
        labelId="filter-label"
        value={mode}
        label="View"
        onChange={e => onChange(e.target.value)}
      >
        <MenuItem value="recommend">Рекомендація суми донату</MenuItem>
        <MenuItem value="custom">Ввести суму донату</MenuItem>
        <MenuItem value="progress">Найближче до мети</MenuItem>
        <MenuItem value="furthest">Найдальше до мети</MenuItem>
        <MenuItem value="closed">Закриті збори</MenuItem>
      </Select>
    </FormControl>
  );
}