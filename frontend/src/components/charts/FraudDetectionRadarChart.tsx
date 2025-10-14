import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface FraudDetectionRadarChartProps {
  data: {
    altmanScore?: number;
    beneishScore?: number;
    benfordCompliance?: number;
    anomalies?: number;
    riskLevel?: string;
  };
  companyName?: string;
}

export default function FraudDetectionRadarChart({ data, companyName = 'Company' }: FraudDetectionRadarChartProps) {
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

    // Radar chart configuration for fraud detection
    const features = [
      'Financial Health',
      'Earnings Quality',
      'Data Integrity',
      'Anomaly Risk',
      'Fraud Risk'
    ];

    // Safe data extraction with fallbacks
    const safeData = {
      altmanScore: data.altmanScore ?? 2.0,
      beneishScore: data.beneishScore ?? 0,
      benfordCompliance: data.benfordCompliance ?? 85,
      anomalies: data.anomalies ?? 0,
      riskLevel: data.riskLevel ?? 'MODERATE'
    };

    // Normalize data for radar chart (0-100 scale)
    const chartData = [
      Math.min(Math.max(safeData.altmanScore * 33.3, 0), 100), // Altman Z-Score normalized
      Math.min(Math.max((2.0 - Math.abs(safeData.beneishScore)) * 50, 0), 100), // Beneish M-Score (inverted, lower is better)
      safeData.benfordCompliance, // Benford's Law compliance
      Math.min(Math.max(100 - safeData.anomalies * 10, 0), 100), // Anomaly risk (inverted)
      safeData.riskLevel === 'LOW' ? 90 : safeData.riskLevel === 'MODERATE' ? 60 : 30 // Overall fraud risk based on risk level
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
        .attr('stroke', 'rgba(255, 107, 157, 0.2)')
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
      .attr('x2', (d: string, i: number) => rScale(100) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y2', (d: string, i: number) => rScale(100) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('stroke', 'rgba(255, 107, 157, 0.3)')
      .attr('stroke-width', 2);

    // Add axis labels
    axis.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '11px')
      .attr('font-weight', '500')
      .attr('fill', '#64748b')
      .text((d: string) => d.split(' ')[0]) // Shortened labels
      .attr('x', (d: string, i: number) => rScale(110) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d: string, i: number) => rScale(110) * Math.sin(angleSlice * i - Math.PI / 2));

    // Create radar area
    const radarLine = d3.lineRadial<number>()
      .radius((d: number, i: number) => rScale(chartData[i]))
      .angle((d: number, i: number) => angleSlice * i)
      .curve(d3.curveLinearClosed);

    // Determine color based on overall fraud risk
    const avgRisk = chartData.reduce((a, b) => a + b, 0) / chartData.length;
    const radarColor = avgRisk > 70 ? 'rgba(255, 107, 157, 0.8)' : avgRisk > 50 ? 'rgba(255, 107, 157, 0.6)' : 'rgba(255, 107, 157, 0.4)';

    // Add the radar area
    g.append('path')
      .datum(chartData)
      .attr('d', radarLine)
      .attr('fill', radarColor)
      .attr('fill-opacity', 0.3)
      .attr('stroke', 'rgba(255, 107, 157, 0.8)')
      .attr('stroke-width', 3)
      .attr('filter', 'drop-shadow(0 4px 8px rgba(255, 107, 157, 0.3))');

    // Add data points
    g.selectAll('.radar-point')
      .data(chartData)
      .enter()
      .append('circle')
      .attr('class', 'radar-point')
      .attr('r', 4)
      .attr('cx', (d: number, i: number) => rScale(d) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (d: number, i: number) => rScale(d) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('fill', 'rgba(255, 107, 157, 1)')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .attr('filter', 'drop-shadow(0 2px 4px rgba(255, 107, 157, 0.5))');

    // Add center circle for better visual appeal
    g.append('circle')
      .attr('r', 8)
      .attr('fill', 'rgba(255, 107, 157, 0.3)')
      .attr('stroke', 'rgba(255, 107, 157, 0.6)')
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
      .attr('fill', radarColor)
      .attr('stroke', 'rgba(255, 107, 157, 0.8)')
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
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-200 to-pink-300 flex items-center justify-center mx-auto mb-4">
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
      border: '2px solid rgba(255, 107, 157, 0.2)'
    }}>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-red-600 flex items-center justify-center">
          <span className="text-white text-lg">🔍</span>
        </div>
        <div>
          <h3 className="text-xl font-bold" style={{ color: '#1e293b' }}>Investment Fraud Risk Radar</h3>
          <p className="text-sm" style={{ color: '#64748b' }}>Fraud indicators relevant to investment decisions</p>
        </div>
      </div>
      <svg ref={chartRef} className="w-full h-auto"></svg>
      <div className="mt-4 text-sm" style={{ color: '#64748b' }}>
        <p>📊 <strong>Financial Health:</strong> Altman Z-Score based stability</p>
        <p>⚖️ <strong>Earnings Quality:</strong> Beneish M-Score manipulation risk</p>
        <p>📈 <strong>Data Integrity:</strong> Benford's Law compliance</p>
        <p>🔍 <strong>Anomaly Risk:</strong> Irregular pattern detection</p>
        <p>🚨 <strong>Fraud Risk:</strong> Overall fraud vulnerability</p>
      </div>
    </div>
  );
}
