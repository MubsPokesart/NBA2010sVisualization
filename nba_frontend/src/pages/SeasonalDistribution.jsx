import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { fetchSeasons, fetchSeasonStats } from '../services/api';
import '../styles/analysis.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const SeasonalDistribution = () => {
  const [selectedSeason, setSelectedSeason] = useState('2018-19');
  const { data: seasons } = useQuery('seasons', fetchSeasons);
  const { data: seasonData, isLoading } = useQuery(
    ['seasonStats', selectedSeason],
    () => fetchSeasonStats(selectedSeason)
  );

  if (isLoading) return <div className="loading">Loading data...</div>;

  if (!seasonData) return <div className="error">No data available</div>;

  // Process data for Western Conference
  const westData = seasonData
    .filter(team => team.conference === 'Western')
    .map(team => team.relative_net_rating);

  // Process data for Eastern Conference
  const eastData = seasonData
    .filter(team => team.conference === 'Eastern')
    .map(team => team.relative_net_rating);

  // Calculate statistics for both conferences
  const calculateStats = (data) => {
    const sorted = [...data].sort((a, b) => a - b);
    return {
      min: sorted[0],
      q1: sorted[Math.floor(sorted.length * 0.25)],
      median: sorted[Math.floor(sorted.length * 0.5)],
      q3: sorted[Math.floor(sorted.length * 0.75)],
      max: sorted[sorted.length - 1],
      mean: data.reduce((a, b) => a + b, 0) / data.length
    };
  };

  const westStats = calculateStats(westData);
  const eastStats = calculateStats(eastData);

  // Create histogram data
  const createHistogram = (data, bins = 10) => {
    const min = Math.min(...data);
    const max = Math.max(...data);
    const binWidth = (max - min) / bins;
    const histogram = new Array(bins).fill(0);
    
    data.forEach(value => {
      const binIndex = Math.min(Math.floor((value - min) / binWidth), bins - 1);
      histogram[binIndex]++;
    });

    return {
      bins: histogram,
      binLabels: Array.from({ length: bins }, (_, i) => 
        `${(min + i * binWidth).toFixed(1)}-${(min + (i + 1) * binWidth).toFixed(1)}`
      )
    };
  };

  const westHistogram = createHistogram(westData);
  const eastHistogram = createHistogram(eastData);

  const chartData = {
    labels: westHistogram.binLabels,
    datasets: [
      {
        label: 'Western Conference',
        data: westHistogram.bins,
        backgroundColor: 'rgba(49, 130, 206, 0.5)',
        borderColor: '#3182ce',
        borderWidth: 1
      },
      {
        label: 'Eastern Conference',
        data: eastHistogram.bins,
        backgroundColor: 'rgba(229, 62, 62, 0.5)',
        borderColor: '#e53e3e',
        borderWidth: 1
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Distribution of Net Ratings by Conference'
      },
      tooltip: {
        callbacks: {
          title: (items) => `Rating Range: ${items[0].label}`,
          label: (context) => `${context.dataset.label}: ${context.formattedValue} teams`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Teams'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Relative Net Rating'
        }
      }
    }
  };

  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Conference Rating Distribution</h2>
      
      <div className="mb-4">
        <select 
          className="analysis-select"
          value={selectedSeason}
          onChange={(e) => setSelectedSeason(e.target.value)}
        >
          {seasons?.map(season => (
            <option key={season} value={season}>{season}</option>
          ))}
        </select>
      </div>

      <div className="chart-container">
        <Bar options={options} data={chartData} />
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <h3 className="font-bold text-blue-700 mb-2">Western Conference Stats</h3>
          <p>Mean: {westStats.mean.toFixed(2)}</p>
          <p>Median: {westStats.median.toFixed(2)}</p>
          <p>Range: {westStats.min.toFixed(2)} to {westStats.max.toFixed(2)}</p>
          <p>IQR: {westStats.q1.toFixed(2)} to {westStats.q3.toFixed(2)}</p>
        </div>
        <div className="bg-red-50 p-4 rounded">
          <h3 className="font-bold text-red-700 mb-2">Eastern Conference Stats</h3>
          <p>Mean: {eastStats.mean.toFixed(2)}</p>
          <p>Median: {eastStats.median.toFixed(2)}</p>
          <p>Range: {eastStats.min.toFixed(2)} to {eastStats.max.toFixed(2)}</p>
          <p>IQR: {eastStats.q1.toFixed(2)} to {eastStats.q3.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
};

export default SeasonalDistribution;