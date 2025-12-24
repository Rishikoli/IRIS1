import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface AnomalyHeatmapProps {
  data: {
    anomalyData: Array<{
      dimension: string;
      category: string;
      value: number;
      severity: 'low' | 'medium' | 'high';
    }>;
  };
  dimensions: string[];
  companyName?: string;
}

export default function AnomalyHeatmap({ data, dimensions, companyName = 'Company' }: AnomalyHeatmapProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data?.anomalyData?.length) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll('*').remove();

    const svg = d3.select(chartRef.current);
    const margin = { top: 60, right: 40, bottom: 140, left: 150 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Set up chart dimensions
    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Create matrix data structure
    const categories = ['Q1', 'Q2', 'Q3', 'Q4', 'YTD'];
    const matrixData: Array<{ x: string, y: string, value: number, severity: string }> = [];

    // Generate sample data if not provided
    dimensions.forEach(dimension => {
      categories.forEach(category => {
        const existingData = data.anomalyData.find(d => d.dimension === dimension && d.category === category);
        if (existingData) {
          matrixData.push({
            x: category,
            y: dimension,
            value: existingData.value,
            severity: existingData.severity
          });
        } else {
          // Generate sample data
          const value = Math.random() * 100;
          const severity = value > 70 ? 'high' : value > 40 ? 'medium' : 'low';
          matrixData.push({
            x: category,
            y: dimension,
            value: Math.round(value),
            severity
          });
        }
      });
    });

    // Create scales
    const xScale = d3.scaleBand()
      .domain(categories)
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleBand()
      .domain(dimensions)
      .range([0, height])
      .padding(0.1);

    // Color scale based on severity
    const colorScale = d3.scaleOrdinal<string>()
      .domain(['low', 'medium', 'high'])
      .range(['#22c55e', '#f59e0b', '#ef4444']);

    // Create heatmap cells
    g.selectAll('.cell')
      .data(matrixData)
      .enter().append('rect')
      .attr('class', 'cell')
      .attr('x', d => xScale(d.x) || 0)
      .attr('y', d => yScale(d.y) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', d => colorScale(d.severity))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .attr('rx', 4)
      .style('opacity', 0.8)
      .on('mouseover', function (event, d) {
        d3.select(this).style('opacity', 1);

        // Create tooltip
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'rgba(0, 0, 0, 0.8)')
          .style('color', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('font-size', '12px')
          .style('pointer-events', 'none')
          .style('opacity', 0);

        tooltip.transition()
          .duration(200)
          .style('opacity', 1);

        tooltip.html(`
          <strong>${d.y} - ${d.x}</strong><br/>
          Value: ${d.value}<br/>
          Severity: ${d.severity.toUpperCase()}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function () {
        d3.select(this).style('opacity', 0.8);
        d3.selectAll('.tooltip').remove();
      });



    // Add x-axis
    g.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .attr('fill', '#64748b')
      .attr('font-size', '12px')
      .attr('font-weight', '500');

    // Add y-axis
    g.append('g')
      .call(d3.axisLeft(yScale))
      .selectAll('text')
      .attr('fill', '#64748b')
      .attr('font-size', '12px')
      .attr('font-weight', '500');

    // Add x-axis label
    g.append('text')
      .attr('x', width / 2)
      .attr('y', height + 40)
      .attr('text-anchor', 'middle')
      .attr('fill', '#64748b')
      .attr('font-size', '12px')
      .attr('font-weight', '500')
      .text('Time Period');

    // Add y-axis label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -110)
      .attr('text-anchor', 'middle')
      .attr('fill', '#64748b')
      .attr('font-size', '12px')
      .attr('font-weight', '500')
      .text('Financial Dimensions');

    // Add title
    svg.append('text')
      .attr('x', (width + margin.left + margin.right) / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .attr('fill', '#1e293b')
      .text('Anomaly Detection Heatmap');

    // Add legend (Moved to Bottom to prevent overlap)
    const legend = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${height + margin.top + 80})`); // Position below chart

    const legendData = [
      { severity: 'low', label: 'Low Risk', color: '#22c55e' },
      { severity: 'medium', label: 'Medium Risk', color: '#f59e0b' },
      { severity: 'high', label: 'High Risk', color: '#ef4444' }
    ];

    legend.selectAll('.legend-item')
      .data(legendData)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(${i * 100}, 0)`) // Horizontal layout
      .each(function (d) {
        const item = d3.select(this);

        item.append('rect')
          .attr('width', 15)
          .attr('height', 15)
          .attr('fill', d.color)
          .attr('rx', 2);

        item.append('text')
          .attr('x', 20)
          .attr('y', 12)
          .attr('fill', '#64748b')
          .attr('font-size', '11px')
          .attr('font-weight', '500')
          .text(d.label);
      });

    // Add cell values (Normalized)
    g.selectAll('.cell-text')
      .data(matrixData)
      .enter().append('text')
      .attr('class', 'cell-text')
      .attr('x', d => (xScale(d.x) || 0) + xScale.bandwidth() / 2)
      .attr('y', d => (yScale(d.y) || 0) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '12px')
      .attr('font-weight', '600')
      .text(d => {
        // Normalize: if < 1, assume ratio (0.8 -> 80), else assume percentage (92 -> 92)
        const val = d.value <= 1 ? d.value * 100 : d.value;
        return val.toFixed(0);
      });

  }, [data, dimensions, companyName]);

  if (!data?.anomalyData?.length && !dimensions?.length) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-red-200 to-red-300 flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">🔥</span>
          </div>
          <p className="text-gray-500">No anomaly data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="neumorphic-card rounded-2xl p-6" style={{
      background: 'rgba(255, 255, 255, 0.9)',
      boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
      border: '2px solid rgba(255, 107, 157, 0.2)'
    }}>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center">
          <span className="text-white text-lg">🔥</span>
        </div>
        <div>
          <h3 className="text-xl font-bold" style={{ color: '#1e293b' }}>Anomaly Detection Heatmap</h3>
          <p className="text-sm" style={{ color: '#64748b' }}>Visual representation of irregularities across financial dimensions</p>
        </div>
      </div>
      <svg ref={chartRef} className="w-full h-auto"></svg>
      <div className="mt-4 text-sm" style={{ color: '#64748b' }}>
        <p><strong>Interpretation:</strong> Darker colors indicate higher anomaly severity. Hover over cells for detailed information.</p>
        <p><strong>Dimensions:</strong> Revenue, Expenses, Assets, and Liabilities across quarterly periods.</p>
      </div>
    </div>
  );
}
