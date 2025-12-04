"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface AnomalyDetectionChartProps {
  data: any;
}

export default function AnomalyDetectionChart({ data }: AnomalyDetectionChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    drawChart();
  }, [data]);

  const drawChart = () => {
    if (!data || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 40, right: 40, bottom: 60, left: 80 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Extract anomaly data
    const anomalies = data.anomalies_by_metric || {};
    const metrics = Object.keys(anomalies);

    if (metrics.length === 0) {
      // No anomalies to display
      svg.append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("fill", "#4ade80")
        .text("✅ No anomalies detected");
      return;
    }

    // Prepare data for visualization
    const chartData = metrics.map(metric => ({
      metric: metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      count: anomalies[metric] || 0,
      severity: anomalies[metric] > 2 ? 'High' : anomalies[metric] > 1 ? 'Medium' : 'Low'
    }));

    // Set up scales
    const xScale = d3.scaleBand()
      .domain(chartData.map(d => d.metric))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(chartData, d => d.count) || 5])
      .range([height, 0]);

    // Color scale based on severity
    const colorScale = d3.scaleOrdinal()
      .domain(['Low', 'Medium', 'High'])
      .range(['#4ade80', '#f59e0b', '#ef4444']);

    // Draw bars
    svg.selectAll(".bar")
      .data(chartData)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", d => xScale(d.metric) || 0)
      .attr("y", d => yScale(d.count))
      .attr("width", xScale.bandwidth())
      .attr("height", d => height - yScale(d.count))
      .attr("fill", d => colorScale(d.severity) as string)
      .attr("rx", 4);

    // Add value labels on bars
    svg.selectAll(".label")
      .data(chartData)
      .enter()
      .append("text")
      .attr("class", "label")
      .attr("x", d => (xScale(d.metric) || 0) + xScale.bandwidth() / 2)
      .attr("y", d => yScale(d.count) - 5)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .style("fill", "#fff")
      .text(d => d.count);

    // Draw axes
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .style("text-anchor", "middle")
      .style("font-size", "10px");

    svg.append("g")
      .call(d3.axisLeft(yScale).ticks(5))
      .selectAll("text")
      .style("font-size", "12px");

    // Add chart title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .style("fill", "#1e293b")
      .text("Anomaly Detection by Metric");

    // Add axis labels
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -60)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Number of Anomalies");

    svg.append("text")
      .attr("y", height + 40)
      .attr("x", width / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Financial Metrics");

    // Add legend
    const legendData = [
      { severity: 'Low', count: chartData.filter(d => d.severity === 'Low').length },
      { severity: 'Medium', count: chartData.filter(d => d.severity === 'Medium').length },
      { severity: 'High', count: chartData.filter(d => d.severity === 'High').length }
    ];

    const legend = svg.selectAll(".legend")
      .data(legendData)
      .enter()
      .append("g")
      .attr("class", "legend")
      .attr("transform", (d, i) => `translate(${width - 80},${-30 + i * 20})`);

    legend.append("rect")
      .attr("width", 15)
      .attr("height", 15)
      .style("fill", d => colorScale(d.severity) as string);

    legend.append("text")
      .attr("x", 20)
      .attr("y", 12)
      .text(d => `${d.severity} (${d.count})`)
      .style("font-size", "12px")
      .style("fill", "#64748b");
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>Anomaly Detection</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>
          Statistical anomalies detected across financial metrics
        </p>
      </div>

      <div className="neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* Anomaly Details */}
      <div className="mt-6 neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>Anomaly Summary</h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 rounded-xl" style={{
            background: 'rgba(75, 222, 128, 0.1)',
            border: '2px solid rgba(75, 222, 128, 0.3)'
          }}>
            <div className="text-2xl font-bold text-green-600">{data.total_anomalies || 0}</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Total Anomalies</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: 'rgba(245, 158, 11, 0.1)',
            border: '2px solid rgba(245, 158, 11, 0.3)'
          }}>
            <div className="text-2xl font-bold text-yellow-600">{data.moderate_anomalies || 0}</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Moderate Risk</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '2px solid rgba(239, 68, 68, 0.3)'
          }}>
            <div className="text-2xl font-bold text-red-600">{data.critical_anomalies || 0}</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Critical Risk</div>
          </div>
        </div>

        {/* Detailed Anomaly List */}
        {data.anomalies_by_metric && Object.keys(data.anomalies_by_metric).length > 0 && (
          <div className="space-y-3">
            <h5 className="font-semibold" style={{ color: '#1e293b' }}>Detailed Breakdown</h5>
            {Object.entries(data.anomalies_by_metric).map(([metric, count]: [string, any]) => (
              <div key={metric} className="flex items-center justify-between p-4 rounded-xl" style={{
                background: 'rgba(255, 255, 255, 0.7)',
                boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
              }}>
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    count > 2 ? 'bg-red-500' : count > 1 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <span className="font-medium" style={{ color: '#1e293b' }}>
                    {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-bold" style={{ color: '#1e293b' }}>{count}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    count > 2 ? 'bg-red-100 text-red-700' :
                    count > 1 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {count > 2 ? 'High' : count > 1 ? 'Medium' : 'Low'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
