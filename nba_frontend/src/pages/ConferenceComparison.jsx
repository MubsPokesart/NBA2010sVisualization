import React from 'react';
import { useQuery } from 'react-query';
import { fetchNBAData } from '../services/api';
import { calculateStats } from '../utils/statistics';
import '../styles/comparison.css';

const ConferenceComparison = () => {
  const { data: nbaData, isLoading } = useQuery('nbaData', fetchNBAData);

  if (isLoading) return <div className="loading">Loading data...</div>;

  const seasons = Object.keys(nbaData);
  const metrics = ['Offensive Rating', 'Defensive Rating', 'Net Rating'];
  const data = seasons.map(season => calculateStats(nbaData[season]));

  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Conference Statistical Comparison</h2>
      <div className="heatmap-container">
        <table>
          <thead>
            <tr>
              <th></th>
              {seasons.map(season => <th key={season}>{season}</th>)}
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, i) => (
              <tr key={metric}>
                <td>{metric}</td>
                {data.map((seasonData, j) => {
                  const cellData = seasonData[i];
                  const className = `heatmap-cell ${
                    cellData.pValue < 0.05 
                      ? cellData.diff > 0 
                        ? 'significant-positive'
                        : 'significant-negative'
                      : ''
                  }`;
                  return (
                    <td key={j} className={className}>
                      {cellData.diff.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ConferenceComparison;