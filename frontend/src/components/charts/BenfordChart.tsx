"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface BenfordChartProps {
  data: any;
}

export default function BenfordChart({ data }: BenfordChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    drawChart();
  }, [data]);

  const drawChart = () => {
    if (!data || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 40, right: 40, bottom: 60, left: 60 };
    const width = 500 - margin.left - margin.right;
    const height = 350 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Benford's Law expected distribution
    const benfordExpected = {
      '1': 30.1, '2': 17.6, '3': 12.5, '4': 9.7, '5': 7.9,
      '6': 6.7, '7': 5.8, '8': 5.1, '9': 4.6
    };

    // Extract actual data from API response
    const digitAnalysis = data.digit_analysis || {};
    const actualData = [];

    for (let digit = 1; digit <= 9; digit++) {
      const expected = (benfordExpected as any)[digit.toString()];
      const actual = digitAnalysis[digit]?.actual || 0;
      const deviation = digitAnalysis[digit]?.deviation || 0;

      actualData.push({
        digit: digit.toString(),
        expected: expected,
        actual: actual,
        deviation: deviation
      });
    }

    // Set up scales
    const xScale = d3.scaleBand()
      .domain(actualData.map(d => d.digit))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(actualData, d => Math.max(d.expected, d.actual)) || 35])
      .range([height, 0]);

    // Color scale for bars
    const colorScale = d3.scaleOrdinal()
      .domain(['expected', 'actual'])
      .range(['#7B68EE', '#FF6B9D']);

    // Draw bars for expected values
    svg.selectAll(".expected-bar")
      .data(actualData)
      .enter()
      .append("rect")
      .attr("class", "expected-bar")
      .attr("x", d => xScale(d.digit) || 0)
      .attr("y", d => yScale(d.expected))
      .attr("width", xScale.bandwidth() / 2)
      .attr("height", d => height - yScale(d.expected))
      .attr("fill", colorScale('expected') as string)
      .attr("opacity", 0.7)
      .attr("rx", 2);

    // Draw bars for actual values
    svg.selectAll(".actual-bar")
      .data(actualData)
      .enter()
      .append("rect")
      .attr("class", "actual-bar")
      .attr("x", d => (xScale(d.digit) || 0) + xScale.bandwidth() / 2)
      .attr("y", d => yScale(d.actual))
      .attr("width", xScale.bandwidth() / 2)
      .attr("height", d => height - yScale(d.actual))
      .attr("fill", colorScale('actual') as string)
      .attr("rx", 2);

    // Add value labels
    svg.selectAll(".expected-label")
      .data(actualData)
      .enter()
      .append("text")
      .attr("class", "expected-label")
      .attr("x", d => (xScale(d.digit) || 0) + xScale.bandwidth() / 4)
      .attr("y", d => yScale(d.expected) - 5)
      .attr("text-anchor", "middle")
      .style("font-size", "10px")
      .style("font-weight", "bold")
      .style("fill", "#fff")
      .text(d => d.expected.toFixed(1));

    svg.selectAll(".actual-label")
      .data(actualData)
      .enter()
      .append("text")
      .attr("class", "actual-label")
      .attr("x", d => (xScale(d.digit) || 0) + (3 * xScale.bandwidth() / 4))
      .attr("y", d => yScale(d.actual) - 5)
      .attr("text-anchor", "middle")
      .style("font-size", "10px")
      .style("font-weight", "bold")
      .style("fill", "#fff")
      .text(d => d.actual.toFixed(1));

    // Draw axes
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .style("font-size", "12px");

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
      .text("Benford's Law Distribution Analysis");

    // Add axis labels
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Frequency (%)");

    svg.append("text")
      .attr("y", height + 40)
      .attr("x", width / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Leading Digit");

    // Add legend
    const legend = svg.selectAll(".legend")
      .data(['Expected (Benford)', 'Actual (Company)'])
      .enter()
      .append("g")
      .attr("class", "legend")
      .attr("transform", (d, i) => `translate(${width - 120},${-30 + i * 20})`);

    legend.append("rect")
      .attr("width", 12)
      .attr("height", 12)
      .style("fill", d => colorScale(d) as string);

    legend.append("text")
      .attr("x", 15)
      .attr("y", 10)
      .text(d => d)
      .style("font-size", "11px")
      .style("fill", "#64748b");
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>Benford's Law Analysis</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>
          Statistical analysis of leading digit distribution for fraud detection
        </p>
      </div>

      <div className="neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* Analysis Summary */}
      <div className="mt-6 neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>Benford's Law Compliance</h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 rounded-xl" style={{
            background: 'rgba(123, 104, 238, 0.1)',
            border: '2px solid rgba(123, 104, 238, 0.3)'
          }}>
            <div className="text-2xl font-bold" style={{ color: '#7B68EE' }}>{data.overall_score || 'N/A'}%</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Compliance Score</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: 'rgba(75, 222, 128, 0.1)',
            border: '2px solid rgba(75, 222, 128, 0.3)'
          }}>
            <div className="text-2xl font-bold text-green-600">
              {Object.values(data.digit_analysis || {}).filter((d: any) => Math.abs(d.deviation || 0) < 2).length}/9
            </div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Digits in Range</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '2px solid rgba(239, 68, 68, 0.3)'
          }}>
            <div className="text-2xl font-bold text-red-600">
              {Object.values(data.digit_analysis || {}).filter((d: any) => Math.abs(d.deviation || 0) > 3).length}
            </div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Significant Deviations</div>
          </div>
        </div>

        {/* Digit Analysis Table */}
        <div className="space-y-3">
          <h5 className="font-semibold" style={{ color: '#1e293b' }}>Digit-by-Digit Analysis</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(data.digit_analysis || {}).map(([digit, analysis]: [string, any]) => (
              <div key={digit} className="p-3 rounded-xl" style={{
                background: 'rgba(255, 255, 255, 0.7)',
                boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                border: `2px solid ${Math.abs(analysis.deviation || 0) > 3 ? 'rgba(239, 68, 68, 0.3)' : 'rgba(75, 222, 128, 0.3)'}`
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-lg" style={{ color: '#1e293b' }}>Digit {digit}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    Math.abs(analysis.deviation || 0) > 3 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                  }`}>
                    {Math.abs(analysis.deviation || 0) > 3 ? 'High Deviation' : 'Normal'}
                  </span>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span style={{ color: '#64748b' }}>Expected:</span>
                    <span className="font-semibold" style={{ color: '#1e293b' }}>{analysis.expected?.toFixed(1) || 'N/A'}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span style={{ color: '#64748b' }}>Actual:</span>
                    <span className="font-semibold" style={{ color: '#1e293b' }}>{analysis.actual?.toFixed(1) || 'N/A'}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span style={{ color: '#64748b' }}>Deviation:</span>
                    <span className={`font-semibold ${analysis.deviation >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {analysis.deviation >= 0 ? '+' : ''}{analysis.deviation?.toFixed(1) || 'N/A'}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
