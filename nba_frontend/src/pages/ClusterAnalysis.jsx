import React from 'react';
import { useQuery } from 'react-query';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchNBAData } from '../services/api';
import '../styles/analysis.css';

const ClusterAnalysis = () => {
  const { data: nbaData, isLoading } = useQuery('nbaData', fetchNBAData);

  if (isLoading) return <div className="loading">Loading data...</div>;

  const processedData = Object.values(nbaData).flat().map(team => ({
    name: team.team,
    relativeOffensive: team.relative_offensive_rating,
    relativeDefensive: team.relative_defensive_rating,
    conference: team.conference
  }));

  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Team Performance Clusters</h2>
      <div className="chart-container">
        <ResponsiveContainer>
          <ScatterChart>
            <CartesianGrid />
            <XAxis dataKey="relativeOffensive" name="Relative Offensive Rating" />
            <YAxis dataKey="relativeDefensive" name="Relative Defensive Rating" />
            <Tooltip />
            <Scatter
              data={processedData.filter(d => d.conference === 'Western')}
              fill="#3182ce"
              name="Western Conference"
            />
            <Scatter
              data={processedData.filter(d => d.conference === 'Eastern')}
              fill="#e53e3e"
              name="Eastern Conference"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ClusterAnalysis;