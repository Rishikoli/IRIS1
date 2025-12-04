import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ForensicRadarChartProps {
  data: {
    altmanScore?: number;
    beneishScore?: number;
    benfordCompliance?: number;
    anomalies?: number;
  };
  companyName?: string;
}

export default function ForensicRadarChart({ data, companyName = 'Company' }: ForensicRadarChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll('*').remove();

    const svg = d3.select(chartRef.current);
    const width = 400;
    const height = 400;
    const margin = 60;
    const radius = Math.min(width, height) / 2 - margin;

    // Set up chart dimensions
    svg
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    const g = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    // Radar chart configuration
    const features = [
      'Altman Z-Score',
      'Beneish M-Score',
      'Benford\'s Law',
      'Anomaly Count',
      'Financial Health'
    ];

    const maxValues = [3.0, -2.0, 100, 10, 100]; // Maximum values for each metric

    // Prepare data for radar chart
    const chartData = [
      Math.min(data.altmanScore || 2.0, 3.0), // Altman Z-Score (0-3 range, higher is better)
      Math.max(data.beneishScore || 0, -2.0), // Beneish M-Score (negative is better, invert for radar)
      data.benfordCompliance || 85, // Benford's Law compliance
      Math.min(data.anomalies || 0, 10), // Anomaly count (lower is better, invert)
      Math.min((data.altmanScore || 2.0) * 33.3, 100) // Financial health score
    ];

    // Create scales
    const angleSlice = (Math.PI * 2) / features.length;

    const rScale = d3.scaleLinear()
      .range([0, radius])
      .domain([0, 100]);

    // Create grid circles
    const levels = 5;
    for (let level = 1; level <= levels; level++) {
      g.append('circle')
        .attr('r', (radius / levels) * level)
        .attr('fill', 'none')
        .attr('stroke', 'rgba(139, 92, 246, 0.2)')
        .attr('stroke-width', level === levels ? '2' : '1')
        .attr('stroke-dasharray', level < levels ? '5,5' : 'none');
    }

    // Create axes
    const axis = g.selectAll('.axis')
      .data(features)
      .enter()
      .append('g')
      .attr('class', 'axis');

    axis.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', (d, i) => rScale(100) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y2', (d, i) => rScale(100) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('stroke', 'rgba(139, 92, 246, 0.3)')
      .attr('stroke-width', 2);

    // Add axis labels
    axis.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '12px')
      .attr('font-weight', '500')
      .attr('fill', '#64748b')
      .text(d => d.split(' ')[0]) // Shortened labels
      .attr('x', (d, i) => rScale(110) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d, i) => rScale(110) * Math.sin(angleSlice * i - Math.PI / 2));

    // Create radar area data in the format [angle, radius]
    const radarData: [number, number][] = chartData.map((value, i) => [angleSlice * i, rScale(value)]);

    // Create radar area
    const radarLine = d3.lineRadial<[number, number]>()
      .radius(d => d[1])
      .angle(d => d[0])
      .curve(d3.curveLinearClosed);

    // Add the radar area
    g.append('path')
      .datum(radarData)
      .attr('d', radarLine)
      .attr('fill', 'rgba(139, 92, 246, 0.2)')
      .attr('fill-opacity', 0.6)
      .attr('stroke', 'rgba(139, 92, 246, 0.8)')
      .attr('stroke-width', 3)
      .attr('filter', 'drop-shadow(0 4px 8px rgba(139, 92, 246, 0.3))');

    // Add data points
    g.selectAll('.radar-point')
      .data(radarData)
      .enter()
      .append('circle')
      .attr('class', 'radar-point')
      .attr('r', 4)
      .attr('cx', d => d[1] * Math.cos(d[0] - Math.PI / 2))
      .attr('cy', d => d[1] * Math.sin(d[0] - Math.PI / 2))
      .attr('fill', 'rgba(139, 92, 246, 1)')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .attr('filter', 'drop-shadow(0 2px 4px rgba(139, 92, 246, 0.5))');

    // Add center circle for better visual appeal
    g.append('circle')
      .attr('r', 8)
      .attr('fill', 'rgba(139, 92, 246, 0.3)')
      .attr('stroke', 'rgba(139, 92, 246, 0.6)')
      .attr('stroke-width', 2);

    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .attr('fill', '#1e293b')
      .text(`${companyName} - Fraud Detection Radar`);

    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 120}, ${height - 100})`);

    legend.append('rect')
      .attr('width', 12)
      .attr('height', 12)
      .attr('fill', 'rgba(139, 92, 246, 0.2)')
      .attr('stroke', 'rgba(139, 92, 246, 0.8)')
      .attr('stroke-width', 2)
      .attr('rx', 2);

    legend.append('text')
      .attr('x', 18)
      .attr('y', 10)
      .attr('font-size', '12px')
      .attr('fill', '#64748b')
      .text('Fraud Risk Level');

  }, [data, companyName]);

  if (!data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-200 to-purple-300 flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">📊</span>
          </div>
          <p className="text-gray-500">No fraud detection data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="neumorphic-card rounded-2xl p-6" style={{
      background: 'rgba(255, 255, 255, 0.9)',
      boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
      border: '2px solid rgba(139, 92, 246, 0.2)'
    }}>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
          <span className="text-white text-lg">🔍</span>
        </div>
        <div>
          <h3 className="text-xl font-bold" style={{ color: '#1e293b' }}>Fraud Detection Radar</h3>
          <p className="text-sm" style={{ color: '#64748b' }}>Multi-dimensional fraud risk analysis</p>
        </div>
      </div>
      <svg ref={chartRef} className="w-full h-auto"></svg>
      <div className="mt-4 text-sm" style={{ color: '#64748b' }}>
        <p>📊 <strong>Altman Z-Score:</strong> Bankruptcy risk indicator</p>
        <p>⚖️ <strong>Beneish M-Score:</strong> Earnings manipulation detection</p>
        <p>📈 <strong>Benford's Law:</strong> Statistical fraud detection</p>
        <p>🔍 <strong>Anomalies:</strong> Irregular pattern count</p>
      </div>
    </div>
  );
}
