import React from 'react';
import { useQuery } from 'react-query';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchNBAData } from '../services/api';
import '../styles/analysis.css';

const ClusterAnalysis = () => {
  const { data: nbaData, isLoading, error } = useQuery('nbaData', fetchNBAData);

  // Handle loading state
  if (isLoading) {
    return (
      <div className="analysis-container">
        <div className="loading">Loading data...</div>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div className="analysis-container">
        <div className="error">
          Error loading data: {error.message}
        </div>
      </div>
    );
  }

  // Handle case where data is not available
  if (!nbaData || Object.keys(nbaData).length === 0) {
    return (
      <div className="analysis-container">
        <div className="error">No data available</div>
      </div>
    );
  }

  // Process the data only if it exists
  console.log('NBA Data:', nbaData);
  const processedData = Object.entries(nbaData).reduce((acc, [season, teams]) => {
    const seasonTeams = teams.map(team => ({
      name: team.team,
      relativeOffensive: team.relative_offensive_rating,
      relativeDefensive: -team.relative_defensive_rating,
      conference: team.conference,
      season: season
    }));
    return [...acc, ...seasonTeams];
  }, []);

  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Team Performance Clusters</h2>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart
            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
          >
            <CartesianGrid />
            <XAxis 
              dataKey="relativeOffensive" 
              name="Relative Offensive Rating"
              label={{ value: "Relative Offensive Rating", position: "bottom" }}
            />
            <YAxis 
              dataKey="relativeDefensive" 
              name="Relative Defensive Rating"
              label={{ value: "Relative Defensive Rating", angle: -90, position: "left" }}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              content={({ payload, label }) => {
                if (payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="custom-tooltip" style={{ 
                      backgroundColor: 'white', 
                      padding: '10px',
                      border: '1px solid #ccc'
                    }}>
                      <p><strong>{data.name}</strong></p>
                      <p>Season: {data.season}</p>
                      <p>Off. Rating: {data.relativeOffensive.toFixed(2)}</p>
                      <p>Def. Rating: {data.relativeDefensive.toFixed(2)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Scatter
              name="Western Conference"
              data={processedData.filter(d => d.conference === 'Western')}
              fill="#3182ce"
              shape="circle"
            />
            <Scatter
              name="Eastern Conference"
              data={processedData.filter(d => d.conference === 'Eastern')}
              fill="#e53e3e"
              shape="circle"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ClusterAnalysis;