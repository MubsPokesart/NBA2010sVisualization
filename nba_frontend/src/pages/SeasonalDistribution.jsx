import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { fetchSeasons, fetchSeasonStats } from '../services/api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import '../styles/analysis.css';

const SeasonalDistribution = () => {
  const [selectedSeason, setSelectedSeason] = useState(null);
  const { data: seasons, isLoading: loadingSeasons } = useQuery('seasons', fetchSeasons);
  const { data: seasonData, isLoading: loadingStats } = useQuery(
    ['seasonStats', selectedSeason],
    () => fetchSeasonStats(selectedSeason),
    { enabled: !!selectedSeason }
  );

  // Set initial selected season when seasons data loads
  React.useEffect(() => {
    if (seasons && seasons.length > 0 && !selectedSeason) {
      setSelectedSeason(seasons[0]);
    }
  }, [seasons, selectedSeason]);

  if (loadingSeasons || loadingStats) {
    return <div className="loading">Loading data...</div>;
  }

  if (!seasonData || !seasons) return <div className="error">No data available</div>;

  // Process data for violin plot
  const createViolinData = (data, conference) => {
    const ratings = data.filter(team => team.conference === conference)
                       .map(team => -team.relative_net_rating);
    
    // Calculate kernel density estimation
    const min = Math.min(...ratings);
    const max = Math.max(...ratings);
    const step = (max - min) / 20;
    const points = [];
    
    for (let x = min; x <= max; x += step) {
      let density = 0;
      ratings.forEach(rating => {
        const kernelValue = Math.exp(-Math.pow(rating - x, 2) / 2);
        density += kernelValue;
      });
      points.push({ density: density / ratings.length, rating: x });
    }
    
    // Mirror the points for violin plot
    return points.map(point => ({
      density: point.density,
      rating: point.rating,
      [`${conference}Positive`]: point.density,
      [`${conference}Negative`]: -point.density
    }));
  };

  const westData = createViolinData(seasonData, 'Western');
  const eastData = createViolinData(seasonData, 'Eastern');
  
  // Merge west and east data
  const mergedData = westData.map((westPoint, i) => ({
    ...westPoint,
    ...eastData[i]
  }));

  // Calculate means
  const westStats = seasonData.filter(team => team.conference === 'Western')
                    .map(team => team.relative_net_rating);
  const eastStats = seasonData.filter(team => team.conference === 'Eastern')
                    .map(team => team.relative_net_rating);
  
  const westMean = westStats.reduce((a, b) => a + b, 0) / westStats.length;
  const eastMean = eastStats.reduce((a, b) => a + b, 0) / eastStats.length;

  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Conference Net Rating Distribution</h2>
      
      <div className="mb-6">
        <select 
          className="w-48 p-2 border rounded"
          value={selectedSeason || ''}
          onChange={(e) => setSelectedSeason(e.target.value)}
        >
          {seasons.map(season => (
            <option key={season} value={season}>
              {season} Season
            </option>
          ))}
        </select>
      </div>

      <div className="bg-white p-6 rounded shadow">
        <ResponsiveContainer width="100%" height={600}>
          <AreaChart 
            data={mergedData} 
            layout="vertical"
            margin={{ top: 20, right: 120, bottom: 20, left: 120 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number"
              domain={['auto', 'auto']}
              label={{ 
                value: 'Density', 
                position: 'bottom',
                offset: 0
              }}
            />
            <YAxis 
              dataKey="rating" 
              type="number"
              label={{ 
                value: 'Net Rating', 
                angle: -90, 
                position: 'insideLeft', 
                offset: -35
              }}
            />
            <Tooltip 
              content={({ payload }) => {
                if (payload && payload.length) {
                  return (
                    <div className="bg-white p-2 border rounded shadow">
                      <p>Net Rating: {payload[0].payload.rating.toFixed(2)}</p>
                      <p>Density: {Math.abs(payload[0].value).toFixed(3)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area
              type="monotone"
              dataKey="WesternPositive"
              stackId="1"
              stroke="#3182ce"
              fill="#3182ce"
              fillOpacity={0.6}
              name="Western"
            />
            <Area
              type="monotone"
              dataKey="WesternNegative"
              stackId="2"
              stroke="#3182ce"
              fill="#3182ce"
              fillOpacity={0.6}
            />
            <Area
              type="monotone"
              dataKey="EasternPositive"
              stackId="3"
              stroke="#e53e3e"
              fill="#e53e3e"
              fillOpacity={0.6}
              name="Eastern"
            />
            <Area
              type="monotone"
              dataKey="EasternNegative"
              stackId="4"
              stroke="#e53e3e"
              fill="#e53e3e"
              fillOpacity={0.6}
            />
            <ReferenceLine 
              y={westMean} 
              stroke="#3182ce" 
              strokeDasharray="3 3"
              label={{ 
                value: 'West Mean', 
                position: 'right', 
                fill: '#3182ce' 
              }}
            />
            <ReferenceLine 
              y={eastMean} 
              stroke="#e53e3e" 
              strokeDasharray="3 3"
              label={{ 
                value: 'East Mean', 
                position: 'left', 
                fill: '#e53e3e' 
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-8">
        <div className="flex justify-center items-center gap-8">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-500 opacity-60 mr-2"></div>
            <span>Western Conference</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 opacity-60 mr-2"></div>
            <span>Eastern Conference</span>
          </div>
        </div>
        <p className="text-center mt-4 text-gray-600">
          * Violin plots show the distribution of team net ratings. Wider sections represent more teams with that rating.
        </p>
        <p className="text-center mt-2 text-gray-600">
          * Dashed lines indicate conference means.
        </p>
      </div>
    </div>
  );
};

export default SeasonalDistribution;