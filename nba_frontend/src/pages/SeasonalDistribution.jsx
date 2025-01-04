import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Chart } from 'react-chartjs-2';
import { fetchSeasons, fetchSeasonStats } from '../services/api';
import '../styles/analysis.css';

const SeasonalDistribution = () => {
  const [selectedSeason, setSelectedSeason] = useState('2018-19');
  const { data: seasons } = useQuery('seasons', fetchSeasons);
  const { data: seasonData, isLoading } = useQuery(
    ['seasonStats', selectedSeason],
    () => fetchSeasonStats(selectedSeason)
  );

  if (isLoading) return <div className="loading">Loading data...</div>;

  const westData = seasonData
    .filter(team => team.conference === 'Western')
    .map(team => team.relative_net_rating);

  const eastData = seasonData
    .filter(team => team.conference === 'Eastern')
    .map(team => team.relative_net_rating);

  const chartData = {
    labels: ['Western Conference', 'Eastern Conference'],
    datasets: [{
      label: 'Relative Net Rating Distribution',
      data: [westData, eastData],
      backgroundColor: ['#3182ce', '#e53e3e']
    }]
  };

  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Conference Rating Distribution</h2>
      <select 
        className="analysis-select"
        value={selectedSeason}
        onChange={(e) => setSelectedSeason(e.target.value)}
      >
        {seasons?.map(season => (
          <option key={season} value={season}>{season}</option>
        ))}
      </select>
      <div className="chart-container">
        <Chart type="violin" data={chartData} />
      </div>
    </div>
  );
};

export default SeasonalDistribution;