"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface HorizontalAnalysisChartProps {
  data: any;
}

export default function HorizontalAnalysisChart({ data }: HorizontalAnalysisChartProps) {
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

    // Extract growth data
    const growthData = data.income_statement || {};

    const metrics = Object.keys(growthData).filter(key => key.includes('growth'));
    const chartData = metrics.map(metric => ({
      metric: metric.replace('_growth_pct', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: parseFloat(growthData[metric]) || 0
    }));

    // Set up scales
    const xScale = d3.scaleBand()
      .domain(chartData.map(d => d.metric))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([d3.min(chartData, d => d.value) || -50, d3.max(chartData, d => d.value) || 50])
      .range([height, 0]);

    // Color scale based on positive/negative growth
    const colorScale = d3.scaleOrdinal()
      .domain(['positive', 'negative'])
      .range(['#4ade80', '#ef4444']);

    // Draw bars
    svg.selectAll(".bar")
      .data(chartData)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", d => xScale(d.metric) || 0)
      .attr("y", d => d.value >= 0 ? yScale(d.value) : yScale(0))
      .attr("width", xScale.bandwidth())
      .attr("height", d => Math.abs(yScale(d.value) - yScale(0)))
      .attr("fill", d => (d.value >= 0 ? colorScale('positive') : colorScale('negative')) as string)
      .attr("rx", 4);

    // Add value labels on bars
    svg.selectAll(".label")
      .data(chartData)
      .enter()
      .append("text")
      .attr("class", "label")
      .attr("x", d => (xScale(d.metric) || 0) + xScale.bandwidth() / 2)
      .attr("y", d => d.value >= 0 ? yScale(d.value) - 5 : yScale(d.value) + 15)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .style("fill", "#fff")
      .text(d => `${d.value.toFixed(1)}%`);

    // Draw axes
    svg.append("g")
      .attr("transform", `translate(0,${yScale(0)})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .style("text-anchor", "middle")
      .style("font-size", "10px");

    svg.append("g")
      .call(d3.axisLeft(yScale).ticks(5))
      .selectAll("text")
      .style("font-size", "12px");

    // Add zero line
    svg.append("line")
      .attr("x1", 0)
      .attr("y1", yScale(0))
      .attr("x2", width)
      .attr("y2", yScale(0))
      .style("stroke", "#64748b")
      .style("stroke-width", 2)
      .style("stroke-dasharray", "5,5");

    // Add chart title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .style("fill", "#1e293b")
      .text("Horizontal Analysis - Growth Trends");

    // Add axis labels
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -60)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Growth Rate (%)");

    svg.append("text")
      .attr("y", height + 40)
      .attr("x", width / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Financial Metrics");
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>Horizontal Analysis</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>
          Year-over-year growth trends for key financial metrics
        </p>
      </div>

      <div className="neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* Growth Details Table */}
      <div className="mt-6 neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>Growth Analysis Details</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(data.income_statement || {}).map(([key, value]: [string, any]) => {
            if (!key.includes('growth')) return null;

            const isPositive = parseFloat(value) >= 0;
            return (
              <div key={key} className="flex items-center justify-between p-4 rounded-xl" style={{
                background: 'rgba(255, 255, 255, 0.7)',
                boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                border: `2px solid ${isPositive ? 'rgba(75, 222, 128, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
              }}>
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="font-medium" style={{ color: '#1e293b' }}>
                    {key.replace('_growth_pct', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {value}%
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {isPositive ? 'Growth' : 'Decline'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
