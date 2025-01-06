import React from 'react';
import { useQuery } from 'react-query';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { fetchNBAData } from '../services/api';
import '../styles/analysis.css';

const ClusterAnalysis = () => {
  const { data: nbaData, isLoading, error } = useQuery('nbaData', fetchNBAData);

  if (isLoading) {
    return (
      <div className="analysis-container">
        <div className="loading">Loading data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-container">
        <div className="error">
          Error loading data: {error.message}
        </div>
      </div>
    );
  }

  if (!nbaData || Object.keys(nbaData).length === 0) {
    return (
      <div className="analysis-container">
        <div className="error">No data available</div>
      </div>
    );
  }

  const processedData = Object.entries(nbaData).flatMap(([season, teams]) =>
    teams.map(team => ({
      name: team.team,
      season,
      conference: team.conference,
      relativeOffensive: parseFloat(team.relative_offensive_rating),
      relativeDefensive: -1 * parseFloat(team.relative_defensive_rating)
    }))
  );

  const offensiveExtent = [
    Math.floor(Math.min(...processedData.map(d => d.relativeOffensive))),
    Math.ceil(Math.max(...processedData.map(d => d.relativeOffensive)))
  ];
  
  const defensiveExtent = [
    Math.floor(Math.min(...processedData.map(d => d.relativeDefensive))),
    Math.ceil(Math.max(...processedData.map(d => d.relativeDefensive)))
  ];

  const tooltipStyle = {
    backgroundColor: '#fff',
    padding: '12px',
    border: '1px solid #ccc',
    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
  };

  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Team Performance Clusters (Relative Ratings)</h2>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart
            margin={{ top: 20, right: 20, bottom: 50, left: 50 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="relativeOffensive" 
              type="number"
              domain={offensiveExtent}
              label={{ 
                value: "Relative Offensive Rating", 
                position: "bottom",
                offset: 30
              }}
              tickCount={10}
            />
            <YAxis 
              dataKey="relativeDefensive" 
              type="number"
              domain={defensiveExtent}
              label={{ 
                value: "Relative Defensive Rating", 
                angle: -90, 
                position: "left",
                offset: 20
              }}
              tickCount={10}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              content={({ payload }) => {
                if (payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div style={tooltipStyle}>
                      <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>{data.name}</p>
                      <p style={{ marginBottom: '4px' }}>Season: {data.season}</p>
                      <p style={{ marginBottom: '4px' }}>Conference: {data.conference}</p>
                      <p style={{ marginBottom: '4px' }}>Relative Off. Rating: {data.relativeOffensive.toFixed(2)}</p>
                      <p>Relative Def. Rating: {data.relativeDefensive.toFixed(2)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Scatter
              name="Western Conference"
              data={processedData.filter(d => d.conference === 'Western')}
              fill="#3182ce"
            />
            <Scatter
              name="Eastern Conference"
              data={processedData.filter(d => d.conference === 'Eastern')}
              fill="#e53e3e"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <div style={{ paddingTop: '4rem' }}>
        <p>* Each point represents a team's relative performance in a specific season</p>
        <p>* Higher offensive rating and lower defensive rating indicate better performance</p>
        <p>* Defensive Rating is Inverted for Scatterplot Inutivity</p>
      </div>
    </div>
  );
};

export default ClusterAnalysis;