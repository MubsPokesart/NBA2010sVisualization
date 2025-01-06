import React from 'react';
import { useQuery } from 'react-query';
import { fetchNBAData } from '../services/api';
import { calculateStats } from '../utils/statistics';
import '../styles/comparison.css';

const ConferenceComparison = () => {
  const { data: nbaData, isLoading, error } = useQuery('nbaData', fetchNBAData);

  if (isLoading) return <div className="loading">Loading data...</div>;
  if (error) return <div className="error">Error loading data: {error.message}</div>;

  const seasons = Object.keys(nbaData);
  const metrics = ['Offensive Rating', 'Defensive Rating', 'Net Rating'];
  const data = seasons.map(season => calculateStats(nbaData[season]));

  // Function to format the cell value based on metric type
  const formatCellValue = (value, metricIndex) => {
    // For defensive rating (index 1), invert the sign since lower is better
    const adjustedValue = metricIndex === 1 ? -value : value;
    return `${adjustedValue > 0 ? '+' : ''}${adjustedValue.toFixed(2)}`;
  };

  // Function to determine cell class based on metric type
  const getCellClass = (cellData, metricIndex) => {
    if (cellData.pValue >= 0.05) return '';
    
    // For defensive rating (index 1), invert the logic since lower is better
    if (metricIndex === 1) {
      return cellData.diff < 0 ? 'significant-positive' : 'significant-negative';
    }
    return cellData.diff > 0 ? 'significant-positive' : 'significant-negative';
  };

  return (
    <div className="analysis-container">
      {/* Header Section */}
      <div className="analysis-header">
        <h2 className="analysis-title">Conference Statistical Comparison</h2>
        <p className="analysis-description">
          Analyzing the performance gap between Eastern and Western conferences across multiple seasons
          through key statistical metrics.
        </p>
      </div>

      {/* Methodology Section */}
      <div className="analysis-section">
        <h3 className="section-title">Understanding the Analysis</h3>
        <div className="legend-container">
          <h4>Statistical Significance:</h4>
          <p>Cells are color-coded based on statistical significance (p less than 0.05):</p>
          <div className="legend">
            <div className="legend-item">
              <div className="legend-color significant-positive"></div>
              <span>Western Conference Advantage</span>
            </div>
            <div className="legend-item">
              <div className="legend-color significant-negative"></div>
              <span>Eastern Conference Advantage</span>
            </div>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="analysis-section">
        <h3 className="section-title">Season-by-Season Comparison</h3>
        <p className="section-description">
          Positive values indicate Western Conference advantage (except for Defensive Rating, where negative values indicate advantage)
        </p>
        
        <div className="heatmap-container">
          <table>
            <thead>
              <tr>
                <th className="metric-header">Metric</th>
                {seasons.map(season => (
                  <th key={season} className="season-header">
                    {season}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric, i) => (
                <tr key={metric}>
                  <td className="metric-name">{metric}</td>
                  {data.map((seasonData, j) => {
                    const cellData = seasonData[i];
                    const className = `heatmap-cell ${getCellClass(cellData, i)}`;
                    return (
                      <td key={j} className={className}>
                        {formatCellValue(cellData.diff, i)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Findings */}
      <div className="analysis-section">
        <h3 className="section-title">Key Observations</h3>
        <div className="key-findings">
          <ul>
            <li>The Western Conference has shown a consistent offensive advantage across most seasons, indicated by positive offensive rating differences.</li>
            <li>For defensive ratings, negative values indicate better performance (fewer points allowed). The Eastern Conference shows stronger defensive performance when values are more negative.</li>
            <li>Net rating differences highlight the overall competitive gap between conferences, with positive values indicating Western Conference advantage.</li>
          </ul>
        </div>
      </div>

      {/* Footer Note */}
      <div className="analysis-footer">
        <p>Note: All metrics are calculated using team-level advanced statistics.</p>
      </div>
    </div>
  );
};

export default ConferenceComparison;