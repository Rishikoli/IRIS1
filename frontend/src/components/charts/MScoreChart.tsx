"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface MScoreChartProps {
  data: any;
}

export default function MScoreChart({ data }: MScoreChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);
  const trendRef = useRef<SVGSVGElement>(null);

  // Safely extract data handling potential structure variations
  // Backend returns: results["beneish_m_score"]["beneish_m_score"]["m_score"]
  // So 'data' passed here is usually 'analysisData.beneish_m_score' 
  // which might be the wrapper or the inner object depending on how it's passed.
  // We'll normalize it.

  const mData = data?.beneish_m_score || data || {};
  const mScore = typeof mData.m_score === 'number' ? mData.m_score : parseFloat(mData.m_score || 0);
  const variables = mData.variables || {};
  const history = mData.historical_m_scores || [];

  useEffect(() => {
    if (chartRef.current) {
      drawGaugeChart();
    }
  }, [data, mScore]);

  useEffect(() => {
    if (trendRef.current && history.length > 1) {
      drawTrendChart();
    }
  }, [history]);

  const drawGaugeChart = () => {
    if (!chartRef.current) return;
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 40, right: 40, bottom: 60, left: 40 };
    // Increased size to match ZScoreChart aesthetics
    const width = 800 - margin.left - margin.right;
    const height = 180 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Define Zones
    // Risk Thresholds: > -1.78 is Manipulator, < -2.22 is Conservative (Safe)
    // We visualize from -6 (Safe) to +2 (High Risk)
    const xScale = d3.scaleLinear()
      .domain([-6, 2])
      .range([0, width]);

    // Zones
    const zones = [
      { min: -6, max: -2.22, color: "#10B981", label: "Conservative Check" }, // Green
      { min: -2.22, max: -1.78, color: "#F59E0B", label: "Grey Zone" },       // Yellow
      { min: -1.78, max: 2, color: "#EF4444", label: "Likely Manipulator" }   // Red
    ];

    // Bars
    // Note: Inverted logic compared to Z-Score? 
    // M-Score: Lower is Better (More negative). Higher (positive/less negative) is bad.

    svg.selectAll("rect.zone")
      .data(zones)
      .enter()
      .append("rect")
      .attr("x", d => xScale(d.min))
      .attr("y", 0)
      .attr("width", d => xScale(d.max) - xScale(d.min))
      .attr("height", height)
      .attr("fill", d => d.color)
      .attr("rx", 4)
      .attr("opacity", 0.2);

    // Zone Labels
    svg.selectAll("text.label")
      .data(zones)
      .enter()
      .append("text")
      .attr("x", d => xScale(d.min) + (xScale(d.max) - xScale(d.min)) / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .style("fill", d => d.color)
      .text(d => d.label);

    // Current Score Marker
    // Clamped score for visual purposes
    const clampedScore = Math.max(-6, Math.min(2, mScore));
    const xPos = xScale(clampedScore);

    // Line
    svg.append("line")
      .attr("x1", xPos)
      .attr("x2", xPos)
      .attr("y1", -5)
      .attr("y2", height + 5)
      .style("stroke", "#1E293B")
      .style("stroke-width", 3);

    // Circle
    svg.append("circle")
      .attr("cx", xPos)
      .attr("cy", height / 2)
      .attr("r", 8)
      .style("fill", "#1E293B")
      .style("stroke", "#fff")
      .style("stroke-width", 2);

    // Score Text
    svg.append("text")
      .attr("x", xPos)
      .attr("y", height + 30)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .style("fill", "#1E293B")
      .text(`Score: ${mScore.toFixed(2)}`);

  };

  const drawTrendChart = () => {
    if (!trendRef.current || history.length < 2) return;
    d3.select(trendRef.current).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 500 - margin.left - margin.right;
    const height = 250 - margin.top - margin.bottom;

    const svg = d3.select(trendRef.current)
      .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Parse dates
    const parseTime = d3.timeParse("%Y-%m-%d");
    const trendData = history.map((d: any) => ({
      date: parseTime(d.period) || new Date(d.period),
      value: Number(d.m_score)
    }));

    // X Scale
    const x = d3.scaleTime()
      .domain(d3.extent(trendData, (d: any) => d.date) as [Date, Date])
      .range([0, width]);

    // Y Scale
    const y = d3.scaleLinear()
      .domain([
        Math.min(-4, d3.min(trendData, (d: any) => d.value) as number),
        Math.max(0, d3.max(trendData, (d: any) => d.value) as number)
      ])
      .range([height, 0]);

    // Grid lines
    svg.append("g")
      .attr("class", "grid")
      .attr("opacity", 0.1)
      .call(d3.axisLeft(y).tickSize(-width).tickFormat(() => ""));

    // Axes
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(5))
      .style("font-size", "11px");

    svg.append("g")
      .call(d3.axisLeft(y))
      .style("font-size", "11px");

    // Threshold Line (-1.78)
    const thresholdY = y(-1.78);
    if (thresholdY >= 0 && thresholdY <= height) {
      svg.append("line")
        .attr("x1", 0)
        .attr("x2", width)
        .attr("y1", thresholdY)
        .attr("y2", thresholdY)
        .attr("stroke", "#EF4444")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4,4");

      svg.append("text")
        .attr("x", width - 5)
        .attr("y", thresholdY - 5)
        .attr("text-anchor", "end")
        .style("font-size", "10px")
        .style("fill", "#EF4444")
        .text("Manipulation Threshold (-1.78)");
    }

    // Line
    const line = d3.line<any>()
      .x(d => x(d.date))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);

    svg.append("path")
      .datum(trendData)
      .attr("fill", "none")
      .attr("stroke", "#6366f1")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Dots
    svg.selectAll(".dot")
      .data(trendData)
      .enter()
      .append("circle")
      .attr("cx", (d: any) => x(d.date))
      .attr("cy", (d: any) => y(d.value))
      .attr("r", 4)
      .attr("fill", "#fff")
      .attr("stroke", "#6366f1")
      .attr("stroke-width", 2);
  };

  const riskColor = mScore > -1.78 ? '#EF4444' : '#10B981';
  const riskLabel = mScore > -1.78 ? 'HIGH RISK' : 'LOW RISK';
  const riskDesc = mScore > -1.78 ? 'Potential Earnings Manipulation' : 'Conservative Accounting';

  // Variable definitions for tooltip/labels
  const variableDefinitions: any = {
    DSRI: "Days Sales in Receivables Index",
    GMI: "Gross Margin Index",
    AQI: "Asset Quality Index",
    SGI: "Sales Growth Index",
    DEPI: "Depreciation Index",
    SGAI: "SG&A Index",
    LVGI: "Leverage Index",
    TATA: "Total Accruals to Total Assets"
  };

  return (
    <div className="w-full space-y-8">

      {/* Header Section */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-slate-800">Beneish M-Score Analysis</h3>
          <p className="text-slate-500">
            Forensic model identifying potential earnings manipulation through 8 financial ratios.
          </p>
        </div>
        <div className={`px-6 py-3 rounded-2xl border-2 flex flex-col items-center min-w-[180px]`}
          style={{ borderColor: riskColor, backgroundColor: `${riskColor}10` }}>
          <span className="text-3xl font-bold" style={{ color: riskColor }}>{mScore.toFixed(2)}</span>
          <span className="text-sm font-bold tracking-wider" style={{ color: riskColor }}>{riskLabel}</span>
        </div>
      </div>

      {/* Main Gauge Chart */}
      <div className="neumorphic-card rounded-3xl p-6 bg-white/50">
        <svg ref={chartRef} className="w-full h-auto max-h-[220px]"></svg>
        <div className="text-center mt-2 text-slate-600 italic text-sm">
          Interpretation: {riskDesc}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Component Breakdown Table */}
        <div className="neumorphic-card rounded-2xl p-6">
          <h4 className="text-lg font-bold text-slate-700 mb-4">8-Variable Breakdown</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 text-slate-500 font-medium">
                <tr>
                  <th className="p-3 rounded-l-lg">Metric</th>
                  <th className="p-3">Full Name</th>
                  <th className="p-3 text-right">Value</th>
                  <th className="p-3 text-right rounded-r-lg">Normal Range</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {Object.entries(variables).map(([key, rawVal]: [string, any]) => {
                  const val = Number(rawVal);
                  // Rough "safe" thresholds for visual coloring (simplified)
                  const isHigh = val > 1.2;
                  return (
                    <tr key={key} className="hover:bg-slate-50/50 transition-colors">
                      <td className="p-3 font-semibold text-slate-700">{key}</td>
                      <td className="p-3 text-slate-500">{variableDefinitions[key] || key}</td>
                      <td className={`p-3 text-right font-mono font-bold ${isHigh ? 'text-amber-500' : 'text-slate-700'}`}>
                        {val.toFixed(3)}
                      </td>
                      <td className="p-3 text-right text-xs text-slate-400">~1.0</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Historical Trend */}
        <div className="neumorphic-card rounded-2xl p-6 flex flex-col">
          <h4 className="text-lg font-bold text-slate-700 mb-4">Historical Trend</h4>
          <div className="flex-1 flex items-center justify-center min-h-[250px]">
            {history.length > 1 ? (
              <svg ref={trendRef} className="w-full h-full"></svg>
            ) : (
              <div className="text-slate-400 text-center">
                <span className="text-4xl block mb-2">📉</span>
                Insufficient data for trend analysis<br />
                (Need at least 2 comparison periods)
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
