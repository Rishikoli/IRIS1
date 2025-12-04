import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ScoreDistributionProps {
  data: {
    forensicScores: number[];
    companyScore: number;
  };
  benchmarks: {
    industry_avg: number;
    peer_avg: number;
  };
  companyName?: string;
}

export default function ScoreDistribution({ data, benchmarks, companyName = 'Company' }: ScoreDistributionProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data?.forensicScores?.length) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll('*').remove();

    const svg = d3.select(chartRef.current);
    const margin = { top: 40, right: 40, bottom: 60, left: 60 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Set up chart dimensions
    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Create histogram data
    const scores = data.forensicScores;
    const x = d3.scaleLinear()
      .domain([0, 100])
      .range([0, width]);

    const histogram = d3.histogram()
      .value((d: number) => d)
      .domain(x.domain() as [number, number])
      .thresholds(x.ticks(20));

    const bins = histogram(scores);

    const y = d3.scaleLinear()
      .domain([0, d3.max(bins, d => d.length) || 0])
      .nice()
      .range([height, 0]);

    // Create bars
    g.selectAll('.bar')
      .data(bins)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', (d: any) => x(d.x0))
      .attr('width', (d: any) => Math.max(0, x(d.x1) - x(d.x0) - 1))
      .attr('y', (d: any) => y(d.length))
      .attr('height', (d: any) => height - y(d.length))
      .attr('fill', 'rgba(123, 104, 238, 0.7)')
      .attr('stroke', 'rgba(123, 104, 238, 0.9)')
      .attr('stroke-width', 1)
      .attr('rx', 2);

    // Add x-axis
    g.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(d3.axisBottom(x))
      .append('text')
      .attr('x', width / 2)
      .attr('y', 40)
      .attr('fill', '#64748b')
      .attr('font-size', '12px')
      .attr('font-weight', '500')
      .attr('text-anchor', 'middle')
      .text('Forensic Score');

    // Add y-axis
    g.append('g')
      .call(d3.axisLeft(y))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -40)
      .attr('x', -height / 2)
      .attr('fill', '#64748b')
      .attr('font-size', '12px')
      .attr('font-weight', '500')
      .attr('text-anchor', 'middle')
      .text('Frequency');

    // Add benchmark lines
    if (benchmarks.industry_avg) {
      g.append('line')
        .attr('x1', x(benchmarks.industry_avg))
        .attr('x2', x(benchmarks.industry_avg))
        .attr('y1', 0)
        .attr('y2', height)
        .attr('stroke', '#f59e0b')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');

      g.append('text')
        .attr('x', x(benchmarks.industry_avg))
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .attr('fill', '#f59e0b')
        .attr('font-size', '10px')
        .attr('font-weight', '600')
        .text('Industry Avg');
    }

    if (benchmarks.peer_avg) {
      g.append('line')
        .attr('x1', x(benchmarks.peer_avg))
        .attr('x2', x(benchmarks.peer_avg))
        .attr('y1', 0)
        .attr('y2', height)
        .attr('stroke', '#06b6d4')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');

      g.append('text')
        .attr('x', x(benchmarks.peer_avg))
        .attr('y', -25)
        .attr('text-anchor', 'middle')
        .attr('fill', '#06b6d4')
        .attr('font-size', '10px')
        .attr('font-weight', '600')
        .text('Peer Avg');
    }

    // Add company score line
    if (data.companyScore) {
      g.append('line')
        .attr('x1', x(data.companyScore))
        .attr('x2', x(data.companyScore))
        .attr('y1', 0)
        .attr('y2', height)
        .attr('stroke', '#ef4444')
        .attr('stroke-width', 3);

      g.append('text')
        .attr('x', x(data.companyScore))
        .attr('y', height + 20)
        .attr('text-anchor', 'middle')
        .attr('fill', '#ef4444')
        .attr('font-size', '12px')
        .attr('font-weight', '700')
        .text(`${companyName}: ${data.companyScore}`);
    }

    // Add title
    svg.append('text')
      .attr('x', (width + margin.left + margin.right) / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .attr('fill', '#1e293b')
      .text('Forensic Score Distribution');

  }, [data, benchmarks, companyName]);

  if (!data?.forensicScores?.length) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-200 to-purple-300 flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">📊</span>
          </div>
          <p className="text-gray-500">No forensic score data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="neumorphic-card rounded-2xl p-6" style={{
      background: 'rgba(255, 255, 255, 0.9)',
      boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
      border: '2px solid rgba(123, 104, 238, 0.2)'
    }}>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
          <span className="text-white text-lg">📊</span>
        </div>
        <div>
          <h3 className="text-xl font-bold" style={{ color: '#1e293b' }}>Forensic Score Distribution</h3>
          <p className="text-sm" style={{ color: '#64748b' }}>Histogram of forensic test results vs benchmarks</p>
        </div>
      </div>
      <svg ref={chartRef} className="w-full h-auto"></svg>
      <div className="mt-4 flex justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-yellow-500 rounded"></div>
          <span style={{ color: '#64748b' }}>Industry Average</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-cyan-500 rounded"></div>
          <span style={{ color: '#64748b' }}>Peer Average</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-red-500 rounded"></div>
          <span style={{ color: '#64748b' }}>Company Score</span>
        </div>
      </div>
    </div>
  );
}
