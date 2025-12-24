"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface BenfordChartProps {
  data: any;
}

export default function BenfordChart({ data }: BenfordChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  // Safely extract data
  const benfordData = data?.benford_analysis || data || {};

  // Backend returns: observed_frequencies (array), expected_frequencies (array)
  const observedFn = benfordData.observed_frequencies || [];
  const expectedFn = benfordData.expected_frequencies || [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6];

  // Prepare combined data for D3
  const chartData = Array.from({ length: 9 }, (_, i) => {
    const digit = i + 1;
    const obs = Number(observedFn[i] || 0);
    const exp = Number(expectedFn[i] || 0);
    return {
      digit: digit.toString(),
      actual: obs,
      expected: exp,
      deviation: obs - exp
    };
  });

  const chiSquare = benfordData.chi_square_statistic || 0;
  const isAnomalous = benfordData.is_anomalous || false;

  useEffect(() => {
    if (!chartRef.current) return;
    drawChart();
  }, [data]);

  const drawChart = () => {
    if (!chartRef.current) return;
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 40, right: 30, bottom: 50, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3.scaleBand()
      .range([0, width])
      .domain(chartData.map(d => d.digit))
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, Math.max(
        40, // Minimum Y axis to 40%
        d3.max(chartData, d => Math.max(d.actual, d.expected)) || 0
      )])
      .range([height, 0]);

    // Grid lines
    svg.append("g")
      .attr("class", "grid")
      .attr("opacity", 0.1)
      .call(d3.axisLeft(y).tickSize(-width).tickFormat(() => ""));

    // Expected Line (Benford)
    const line = d3.line<any>()
      .x(d => (x(d.digit) || 0) + x.bandwidth() / 2)
      .y(d => y(d.expected))
      .curve(d3.curveMonotoneX);

    svg.append("path")
      .datum(chartData)
      .attr("fill", "none")
      .attr("stroke", "#7B68EE")
      .attr("stroke-width", 3)
      .attr("stroke-dasharray", "5,5")
      .attr("d", line);

    // Expected Points
    svg.selectAll(".dot-exp")
      .data(chartData)
      .enter()
      .append("circle")
      .attr("cx", d => (x(d.digit) || 0) + x.bandwidth() / 2)
      .attr("cy", d => y(d.expected))
      .attr("r", 4)
      .attr("fill", "#7B68EE");

    // Actual Bars
    svg.selectAll(".bar")
      .data(chartData)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d.digit) || 0)
      .attr("width", x.bandwidth())
      .attr("y", d => y(d.actual))
      .attr("height", d => height - y(d.actual))
      .attr("fill", "#FF6B9D")
      .attr("rx", 4)
      .attr("opacity", 0.8);

    // Labels
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .style("font-size", "14px");

    svg.append("text")
      .attr("transform", `translate(${width / 2}, ${height + 40})`)
      .style("text-anchor", "middle")
      .text("Leading Digit");

    svg.append("g")
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d + "%"))
      .style("font-size", "12px");

    // Legend
    const legend = svg.append("g")
      .attr("transform", `translate(${width - 200}, -20)`);

    // Legend content...
    legend.append("rect").attr("width", 15).attr("height", 15).attr("fill", "#FF6B9D").attr("rx", 2);
    legend.append("text").attr("x", 20).attr("y", 12).text("Actual Frequency").style("font-size", "12px").style("fill", "#64748b");

    legend.append("line").attr("x1", 0).attr("x2", 15).attr("y1", 28).attr("y2", 28).attr("stroke", "#7B68EE").attr("stroke-width", 3).attr("stroke-dasharray", "3,3");
    legend.append("text").attr("x", 20).attr("y", 32).text("Benford's Law (Expected)").style("font-size", "12px").style("fill", "#64748b");

  };

  return (
    <div className="w-full space-y-8">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-slate-800">Benford's Law Analysis</h3>
          <p className="text-slate-500">
            Forensic analysis of leading digit distribution to detect potential anomalies or manual manipulation.
          </p>
        </div>
        <div className={`px-6 py-3 rounded-2xl border-2 flex flex-col items-center min-w-[180px]`}
          style={{
            borderColor: isAnomalous ? '#EF4444' : '#10B981',
            backgroundColor: isAnomalous ? '#EF444410' : '#10B98110'
          }}>
          <span className="text-xl font-bold" style={{ color: isAnomalous ? '#EF4444' : '#10B981' }}>
            {isAnomalous ? 'ANOMALOUS' : 'NORMAL'}
          </span>
          <span className="text-xs font-bold tracking-wider text-slate-500">DISTRIBUTION</span>
        </div>
      </div>

      <div className="neumorphic-card rounded-3xl p-6 bg-white/50">
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="neumorphic-card p-5 rounded-xl text-center">
          <div className="text-3xl font-bold text-slate-700">{Number(chiSquare).toFixed(2)}</div>
          <div className="text-sm text-slate-500 uppercase tracking-wide font-semibold mt-1">Chi-Square Score</div>
        </div>
        <div className="neumorphic-card p-5 rounded-xl text-center">
          <div className="text-3xl font-bold text-slate-700">{benfordData.total_numbers_analyzed || 0}</div>
          <div className="text-sm text-slate-500 uppercase tracking-wide font-semibold mt-1">Data Points Analyzed</div>
        </div>
        <div className="neumorphic-card p-5 rounded-xl text-center">
          <div className="text-3xl font-bold text-slate-700">{benfordData.confidence_level ? (benfordData.confidence_level * 100) + '%' : '95%'}</div>
          <div className="text-sm text-slate-500 uppercase tracking-wide font-semibold mt-1">Confidence Level</div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="neumorphic-card rounded-2xl p-6">
        <h4 className="text-lg font-bold text-slate-700 mb-4">Digit Analysis Breakdown</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500 font-medium">
              <tr>
                <th className="p-3 rounded-l-lg">Digit</th>
                <th className="p-3 text-right">Actual Freq.</th>
                <th className="p-3 text-right">Expected Freq.</th>
                <th className="p-3 text-right rounded-r-lg">Deviation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {chartData.map((d) => (
                <tr key={d.digit} className="hover:bg-slate-50/50">
                  <td className="p-3 font-bold text-slate-700">{d.digit}</td>
                  <td className="p-3 text-right font-mono">{d.actual.toFixed(1)}%</td>
                  <td className="p-3 text-right font-mono text-slate-400">{d.expected.toFixed(1)}%</td>
                  <td className={`p-3 text-right font-bold ${Math.abs(d.deviation) > 5 ? 'text-red-500' : 'text-slate-600'}`}>
                    {d.deviation > 0 ? '+' : ''}{d.deviation.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
