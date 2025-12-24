"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ZScoreChartProps {
  data: any;
}

export default function ZScoreChart({ data }: ZScoreChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);
  const trendRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;
    drawGaugeChart();
  }, [data]);

  useEffect(() => {
    if (!data?.historical_z_scores || !trendRef.current) return;
    drawTrendChart();
  }, [data]);

  const drawGaugeChart = () => {
    if (!data || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    // Increased logical dimensions for chunkier look
    const margin = { top: 50, right: 80, bottom: 80, left: 80 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Z-Score zones
    const zones = [
      { range: [-20, 1.8], label: 'Distress', color: '#ef4444', opacity: 0.15 },
      { range: [1.8, 3.0], label: 'Grey', color: '#f59e0b', opacity: 0.15 },
      { range: [3.0, 20], label: 'Safe', color: '#4ade80', opacity: 0.15 }
    ];

    const zScore = parseFloat(data.z_score) || 0;

    // Scale for Y-axis (Z-Score values)
    const minDomain = Math.min(-2, zScore - 2);
    const maxDomain = Math.max(6, zScore + 2);

    const xScale = d3.scaleLinear()
      .domain([minDomain, maxDomain])
      .range([0, width]);

    // Draw zone backgrounds (Horizontal layout)
    zones.forEach((zone) => {
      const xMin = Math.max(zone.range[0], minDomain);
      const xMax = Math.min(zone.range[1], maxDomain);

      if (xMin < xMax) {
        svg.append("rect")
          .attr("x", xScale(xMin))
          .attr("y", 0)
          .attr("width", xScale(xMax) - xScale(xMin))
          .attr("height", height * 0.6) // Taller bars (60% of height)
          .attr("fill", zone.color)
          .attr("opacity", zone.opacity)
          .attr("rx", 6);

        // Add zone labels
        if (xScale(xMax) - xScale(xMin) > 40) {
          svg.append("text")
            .attr("x", xScale(xMin) + (xScale(xMax) - xScale(xMin)) / 2)
            .attr("y", -15) // Moved up slightly
            .attr("text-anchor", "middle")
            .style("font-size", "14px") // Larger font
            .style("fill", zone.color)
            .style("font-weight", "bold")
            .text(zone.label);
        }
      }
    });

    // Draw main axis line
    const axisY = height * 0.3; // Center line within the bars
    svg.append("line")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", axisY)
      .attr("y2", axisY)
      .style("stroke", "#94a3b8")
      .style("stroke-width", 2);

    // Grid lines
    [1.8, 3.0].forEach(val => {
      if (val >= minDomain && val <= maxDomain) {
        svg.append("line")
          .attr("x1", xScale(val))
          .attr("x2", xScale(val))
          .attr("y1", 0)
          .attr("y2", height * 0.6)
          .style("stroke", "#64748b")
          .style("stroke-width", 2)
          .style("stroke-dasharray", "4,4");

        svg.append("text")
          .attr("x", xScale(val))
          .attr("y", height * 0.6 + 25)
          .attr("text-anchor", "middle")
          .style("font-size", "12px")
          .style("fill", "#64748b")
          .style("font-weight", "bold")
          .text(val.toString());
      }
    });

    // Current Score Indicator
    const scoreX = xScale(zScore);

    // Draw needle/marker
    svg.append("circle")
      .attr("cx", scoreX)
      .attr("cy", axisY)
      .attr("r", 12) // Larger dot
      .attr("fill", "#7B68EE")
      .attr("stroke", "#fff")
      .attr("stroke-width", 3)
      .style("filter", "drop-shadow(0 0 6px rgba(123, 104, 238, 0.6))");

    // Score label
    svg.append("text")
      .attr("x", scoreX)
      .attr("y", axisY - 30)
      .attr("text-anchor", "middle")
      .style("font-size", "20px") // Larger score font
      .style("font-weight", "bold")
      .style("fill", "#7B68EE")
      .text(zScore.toFixed(2));

    // Risk level label below
    const riskLevel = zScore < 1.8 ? 'DISTRESS' : zScore < 3.0 ? 'GREY' : 'SAFE';
    const riskColor = zScore < 1.8 ? '#ef4444' : zScore < 3.0 ? '#f59e0b' : '#4ade80';

    svg.append("text")
      .attr("x", scoreX)
      .attr("y", axisY + 45)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .style("fill", riskColor)
      .text(riskLevel);
  };

  const drawTrendChart = () => {
    if (!data?.historical_z_scores || !trendRef.current) return;

    // Clear previous
    d3.select(trendRef.current).selectAll("*").remove();

    const history = data.historical_z_scores;
    if (history.length < 2) return;

    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const width = 600 - margin.left - margin.right;
    const height = 200 - margin.top - margin.bottom;

    const svg = d3.select(trendRef.current)
      .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3.scalePoint()
      .domain(history.map((d: any) => d.period))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([
        Math.min(0, d3.min(history, (d: any) => Number(d.z_score)) as number - 1),
        Math.max(5, d3.max(history, (d: any) => Number(d.z_score)) as number + 1)
      ])
      .range([height, 0]);

    // Line generator
    const line = d3.line<any>()
      .x(d => xScale(d.period)!)
      .y(d => yScale(d.z_score))
      .curve(d3.curveMonotoneX);

    // Add X Axis
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickSize(0).tickPadding(10))
      .selectAll("text")
      .style("fill", "#64748b")
      .style("font-size", "10px");

    // Add Y Axis
    svg.append("g")
      .call(d3.axisLeft(yScale).ticks(5))
      .selectAll("text")
      .style("fill", "#64748b")
      .style("font-size", "10px");

    // Add Grid
    svg.append("g")
      .attr("class", "grid")
      .call(d3.axisLeft(yScale).ticks(5).tickSize(-width).tickFormat(() => ""))
      .style("stroke-opacity", 0.1);

    // Add Threshold zones (background)
    // Distress < 1.8
    svg.append("rect")
      .attr("x", 0)
      .attr("y", yScale(1.8))
      .attr("width", width)
      .attr("height", yScale(0) - yScale(1.8)) // Approx
      .attr("fill", "#ef4444")
      .attr("opacity", 0.05);

    // Draw path
    svg.append("path")
      .datum(history)
      .attr("fill", "none")
      .attr("stroke", "#7B68EE")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add dots
    svg.selectAll(".dot")
      .data(history)
      .enter()
      .append("circle")
      .attr("class", "dot")
      .attr("cx", (d: any) => xScale(d.period)!)
      .attr("cy", (d: any) => yScale(d.z_score))
      .attr("r", 4)
      .attr("fill", "#fff")
      .attr("stroke", "#7B68EE")
      .attr("stroke-width", 2);
  };

  const zScore = parseFloat(data.z_score) || 0;
  const riskColor = zScore < 1.8 ? '#ef4444' : zScore < 3.0 ? '#f59e0b' : '#4ade80';

  return (
    <div className="w-full space-y-6">

      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-bold mb-1" style={{ color: '#1e293b' }}>Altman Z-Score Analysis</h3>
          <p className="text-sm" style={{ color: '#64748b' }}>
            Bankruptcy prediction model based on 5 key financial ratios
          </p>
        </div>
        <div className="px-4 py-2 rounded-xl text-center" style={{
          background: `rgba(${riskColor === '#ef4444' ? '239,68,68' : riskColor === '#f59e0b' ? '245,158,11' : '74,222,128'}, 0.1)`,
          border: `1px solid ${riskColor}`
        }}>
          <div className="text-xl font-bold" style={{ color: riskColor }}>{zScore.toFixed(2)}</div>
          <div className="text-xs font-bold uppercase" style={{ color: riskColor }}>
            {zScore < 1.8 ? 'Distress' : zScore < 3.0 ? 'Grey Zone' : 'Safe'}
          </div>
        </div>
      </div>

      {/* Main Gauge */}
      <div className="neumorphic-card rounded-2xl p-6 flex justify-center items-center" style={{ background: 'rgba(255,255,255,0.6)' }}>
        <svg ref={chartRef} className="w-full max-w-4xl h-80"></svg>
      </div>

      {/* Component Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Detailed Components Table */}
        <div className="neumorphic-card rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.8)' }}>
          <h4 className="text-sm font-bold uppercase text-slate-500 mb-4 tracking-wider">Score Components</h4>
          <div className="space-y-4">
            {[
              { label: 'A. Working Capital / Assets', value: data.components?.working_capital_ratio, weight: '1.2x', desc: 'Liquidity' },
              { label: 'B. Retained Earnings / Assets', value: data.components?.retained_earnings_ratio, weight: '1.4x', desc: 'Accumulated Profit' },
              { label: 'C. EBIT / Assets', value: data.components?.ebit_ratio, weight: '3.3x', desc: 'Operating Efficiency' },
              { label: 'D. Equity / Total Liabilities', value: data.components?.equity_to_debt_ratio, weight: '0.6x', desc: 'Market Leverage' },
              { label: 'E. Sales / Assets', value: data.components?.sales_ratio, weight: '1.0x', desc: 'Asset Turnover' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors">
                <div>
                  <div className="text-sm font-semibold text-slate-700">{item.label}</div>
                  <div className="text-xs text-slate-400">{item.desc} (Weight: {item.weight})</div>
                </div>
                <div className="text-right">
                  <div className="font-mono font-medium text-slate-800">{Number(item.value || 0).toFixed(3)}</div>
                  <div className="text-xs text-blue-500">
                    +{(Number(item.value || 0) * parseFloat(item.weight)).toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Historical Trend */}
        <div className="neumorphic-card rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.8)' }}>
          <h4 className="text-sm font-bold uppercase text-slate-500 mb-4 tracking-wider">Historical Trend</h4>
          {data.historical_z_scores && data.historical_z_scores.length > 1 ? (
            <svg ref={trendRef} className="w-full h-64"></svg>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
              Insufficient historical data for trend analysis
            </div>
          )}
        </div>
      </div>

      {/* Interpretation */}
      <div className="p-4 rounded-xl bg-blue-50 border border-blue-100 text-sm text-blue-800">
        <strong>Analyst Note: </strong>
        {data.interpretation}
      </div>

    </div>
  );
}
