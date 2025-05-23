import React from 'react';
import { Card, CardContent, CardMedia, Typography, Button, LinearProgress, Box } from '@mui/material';

export default function DonationCard({ campaign, recommendation, etaDays }) {
  const pct = campaign.progress_pct;
  const labelAmount = recommendation;

  const handleDonate = () => {
    const url = `${campaign.external_url}?amount=${labelAmount}`;
    window.open(url, '_blank');
  };

  return (
    <Card
      sx={{
        width: { xs: '100%', sm: 340 },
        display: 'flex',
        flexDirection: 'column',
        transition: 'box-shadow 0.3s',
        '&:hover': { boxShadow: 10 },
      }}
    >
      {campaign.image_url && (
        <CardMedia
          component="img"
          height="200"
          image={campaign.image_url}
          alt={campaign.name}
        />
      )}
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Typography
          variant="h6"
          sx={{
            display: '-webkit-box',
            WebkitLineClamp: 1,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            minHeight: '2rem',
          }}
        >
          {campaign.name}
        </Typography>
        <Box sx={{ mt: 1, flexGrow: 0 }}>
          <Typography variant="body2">Мета: {campaign.goal.toLocaleString()}₴</Typography>
          <Typography variant="body2">Зібрано: {campaign.saved.toLocaleString()}₴</Typography>
          <LinearProgress variant="determinate" value={pct} sx={{ my: 1 }} />
          <Typography variant="body2" color="textSecondary">
            {pct}% зібрано
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Прогнозовано днів до закриття: {etaDays}
          </Typography>
        </Box>
      </CardContent>
      <Box sx={{ p: 2, pt: 0 }}>
        <Button variant="contained" fullWidth onClick={handleDonate}>
          Задонатити {labelAmount.toLocaleString()}₴
        </Button>
      </Box>
    </Card>
  );
}