"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface FinancialRatiosChartProps {
  data: any;
}

export default function FinancialRatiosChart({ data }: FinancialRatiosChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    drawChart();
  }, [data]);

  const drawChart = () => {
    if (!data || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 40, right: 120, bottom: 60, left: 80 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Extract data from the nested structure
    const ratiosData: any = {};
    const years = Object.keys(data.financial_ratios || {});

    years.forEach(year => {
      if (data.financial_ratios[year]) {
        Object.keys(data.financial_ratios[year]).forEach(ratio => {
          if (!ratiosData[ratio]) ratiosData[ratio] = [];
          ratiosData[ratio].push({
            year: year,
            value: parseFloat(data.financial_ratios[year][ratio]) || 0
          });
        });
      }
    });

    // Prepare data for visualization
    const ratioNames = Object.keys(ratiosData);
    const chartData = ratioNames.map(ratio => ({
      ratio: ratio.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      values: ratiosData[ratio]
    }));

    // Set up scales
    const xScale = d3.scaleBand()
      .domain(years)
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(chartData, (d: any) => d3.max(d.values, (v: any) => v.value as number)) || 100])
      .range([height, 0]);

    // Color scale for different ratios
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    // Draw axes
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .style("text-anchor", "middle")
      .style("font-size", "12px");

    svg.append("g")
      .call(d3.axisLeft(yScale))
      .selectAll("text")
      .style("font-size", "12px");

    // Draw lines for each ratio
    chartData.forEach((ratioData, index) => {
      const line = d3.line<any>()
        .x(d => xScale(d.year) || 0 + xScale.bandwidth() / 2)
        .y(d => yScale(d.value))
        .curve(d3.curveMonotoneX);

      // Draw the line
      svg.append("path")
        .datum(ratioData.values)
        .attr("fill", "none")
        .attr("stroke", colorScale(index.toString()))
        .attr("stroke-width", 3)
        .attr("d", line);

      // Add data points
      svg.selectAll(`.dot-${index}`)
        .data(ratioData.values)
        .enter()
        .append("circle")
        .attr("class", `dot-${index}`)
        .attr("cx", (d: any) => xScale(d.year) || 0 + xScale.bandwidth() / 2)
        .attr("cy", (d: any) => yScale(d.value))
        .attr("r", 5)
        .attr("fill", colorScale(index.toString()))
        .style("cursor", "pointer")
        .append("title")
        .text((d: any) => `${ratioData.ratio}: ${d.value}% (${d.year})`);
    });

    // Add legend
    const legend = svg.selectAll(".legend")
      .data(chartData)
      .enter()
      .append("g")
      .attr("class", "legend")
      .attr("transform", (d, i) => `translate(${width + 20},${i * 20})`);

    legend.append("rect")
      .attr("width", 15)
      .attr("height", 15)
      .style("fill", (d, i) => colorScale(i.toString()));

    legend.append("text")
      .attr("x", 20)
      .attr("y", 12)
      .text(d => d.ratio)
      .style("font-size", "12px")
      .style("fill", "#64748b");

    // Add chart title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .style("fill", "#1e293b")
      .text("Financial Ratios Trend Analysis");

    // Add axis labels
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -60)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Ratio Value (%)");

    svg.append("text")
      .attr("y", height + 40)
      .attr("x", width / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Year");
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>Financial Ratios Trend</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>
          Multi-year trend analysis of key financial ratios
        </p>
      </div>

      <div className="neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* Ratio Details Table */}
      <div className="mt-6 neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>Ratio Details</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(data.financial_ratios || {}).map(([year, ratios]: [string, any]) => (
            <div key={year} className="p-4 rounded-xl" style={{
              background: 'rgba(255, 255, 255, 0.7)',
              boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
            }}>
              <h5 className="font-semibold mb-3" style={{ color: '#1e293b' }}>{year}</h5>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span style={{ color: '#64748b' }}>Gross Margin:</span>
                  <span className="font-semibold" style={{ color: '#1e293b' }}>{ratios.gross_margin_pct || 'N/A'}%</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#64748b' }}>Net Margin:</span>
                  <span className="font-semibold" style={{ color: '#1e293b' }}>{ratios.net_margin_pct || 'N/A'}%</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#64748b' }}>ROE:</span>
                  <span className="font-semibold" style={{ color: '#1e293b' }}>{ratios.roe || 'N/A'}%</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#64748b' }}>ROA:</span>
                  <span className="font-semibold" style={{ color: '#1e293b' }}>{ratios.roa || 'N/A'}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
