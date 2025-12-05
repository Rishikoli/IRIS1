"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface MScoreChartProps {
  data: any;
}

export default function MScoreChart({ data }: MScoreChartProps) {
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
    const width = 500 - margin.left - margin.right;
    const height = 350 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const mScore = parseFloat(data.m_score) || 0;

    // M-Score risk zones (Beneish M-Score)
    const zones = [
      { range: [-10, -2.22], label: 'Likely Manipulator', color: '#ef4444', description: 'High manipulation risk' },
      { range: [-2.22, -1.78], label: 'Conservative', color: '#4ade80', description: 'Low manipulation risk' },
      { range: [-1.78, 10], label: 'Aggressive', color: '#f59e0b', description: 'Moderate manipulation risk' }
    ];

    // Scale for Y-axis (M-Score values)
    const yScale = d3.scaleLinear()
      .domain([-5, 5]) // Extended range for better visualization
      .range([height, 0]);

    // Draw zone backgrounds
    zones.forEach((zone, index) => {
      const yStart = yScale(zone.range[0]);
      const yEnd = yScale(zone.range[1]);

      svg.append("rect")
        .attr("x", 0)
        .attr("y", Math.min(yStart, yEnd))
        .attr("width", width)
        .attr("height", Math.abs(yEnd - yStart))
        .attr("fill", zone.color)
        .attr("opacity", 0.1);

      // Add zone labels
      svg.append("text")
        .attr("x", width + 10)
        .attr("y", (yStart + yEnd) / 2)
        .attr("text-anchor", "start")
        .style("font-size", "12px")
        .style("fill", zone.color)
        .style("font-weight", "bold")
        .text(zone.label);

      svg.append("text")
        .attr("x", width + 10)
        .attr("y", (yStart + yEnd) / 2 + 15)
        .attr("text-anchor", "start")
        .style("font-size", "10px")
        .style("fill", "#64748b")
        .text(zone.description);
    });



    // Draw Y-axis
    svg.append("g")
      .call(d3.axisLeft(yScale).ticks(6))
      .selectAll("text")
      .style("font-size", "12px");

    // Draw horizontal grid lines
    svg.selectAll(".grid-line")
      .data([-2.22, -1.78])
      .enter()
      .append("line")
      .attr("class", "grid-line")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", d => yScale(d))
      .attr("y2", d => yScale(d))
      .style("stroke", "#64748b")
      .style("stroke-width", 1)
      .style("stroke-dasharray", "3,3");

    // Draw current M-Score line
    const scoreY = yScale(mScore);

    svg.append("line")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", scoreY)
      .attr("y2", scoreY)
      .style("stroke", "#FF6B9D")
      .style("stroke-width", 3)
      .style("stroke-dasharray", "none");

    // Add score indicator circle
    svg.append("circle")
      .attr("cx", width / 2)
      .attr("cy", scoreY)
      .attr("r", 8)
      .attr("fill", "#FF6B9D")
      .style("filter", "drop-shadow(0 0 5px rgba(255, 107, 157, 0.5))");

    // Add score value label
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", scoreY - 15)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .style("fill", "#FF6B9D")
      .text(mScore.toFixed(2));

    // Add manipulation probability label
    const manipulationRisk = mScore > -1.78 ? 'HIGH' : 'LOW';
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", scoreY + 20)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .style("fill", mScore > -1.78 ? '#ef4444' : '#4ade80')
      .text(`${manipulationRisk} RISK`);

    // Add chart title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .style("fill", "#1e293b")
      .text("Beneish M-Score Analysis");

    // Add axis label
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("M-Score Value");
  };

  const mScore = parseFloat(data.m_score) || 0;
  const manipulationProbability = mScore > -1.78 ? 'High' : 'Low';
  const riskColor = mScore > -1.78 ? '#ef4444' : '#4ade80';

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>Beneish M-Score</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>
          Earnings manipulation detection using Beneish M-Score model
        </p>
      </div>

      <div className="neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* M-Score Details */}
      <div className="mt-6 neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>M-Score Analysis Details</h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 rounded-xl" style={{
            background: `rgba(${riskColor.includes('#ef4444') ? '239, 68, 68' : '74, 222, 128'}, 0.1)`,
            border: `2px solid ${riskColor}30`
          }}>
            <div className="text-2xl font-bold" style={{ color: riskColor }}>{mScore.toFixed(2)}</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>M-Score</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: `rgba(${riskColor.includes('#ef4444') ? '239, 68, 68' : '74, 222, 128'}, 0.1)`,
            border: `2px solid ${riskColor}30`
          }}>
            <div className="text-lg font-bold" style={{ color: riskColor }}>{manipulationProbability} RISK</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Manipulation Risk</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: `rgba(${riskColor.includes('#ef4444') ? '239, 68, 68' : '74, 222, 128'}, 0.1)`,
            border: `2px solid ${riskColor}30`
          }}>
            <div className="text-sm font-bold" style={{ color: riskColor }}>
              {mScore > -1.78 ? 'Likely earnings manipulation' : 'Conservative accounting practices'}
            </div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Interpretation</div>
          </div>
        </div>

        {/* Score Indicators */}
        <div className="space-y-3">
          <h5 className="font-semibold" style={{ color: '#1e293b' }}>M-Score Indicators</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(data.indicators || {}).slice(0, 6).map(([indicator, value]: [string, any]) => (
              <div key={indicator} className="flex items-center justify-between p-3 rounded-xl" style={{
                background: 'rgba(255, 255, 255, 0.7)',
                boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
              }}>
                <span className="font-medium" style={{ color: '#64748b' }}>
                  {indicator.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </span>
                <span className={`font-bold ${parseFloat(value) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {parseFloat(value).toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Zone Explanations */}
        <div className="mt-6 space-y-3">
          <h5 className="font-semibold" style={{ color: '#1e293b' }}>Risk Interpretation Guide</h5>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-xl" style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '2px solid rgba(239, 68, 68, 0.3)'
            }}>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="font-semibold text-red-700">Likely Manipulator</span>
              </div>
              <p className="text-xs" style={{ color: '#64748b' }}>M-Score &gt; -1.78</p>
              <p className="text-xs mt-1" style={{ color: '#64748b' }}>High probability of earnings manipulation</p>
            </div>

            <div className="p-3 rounded-xl" style={{
              background: 'rgba(74, 222, 128, 0.1)',
              border: '2px solid rgba(74, 222, 128, 0.3)'
            }}>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="font-semibold text-green-700">Conservative</span>
              </div>
              <p className="text-xs" style={{ color: '#64748b' }}>M-Score &lt; -2.22</p>
              <p className="text-xs mt-1" style={{ color: '#64748b' }}>Low probability of manipulation</p>
            </div>

            <div className="p-3 rounded-xl" style={{
              background: 'rgba(245, 158, 11, 0.1)',
              border: '2px solid rgba(245, 158, 11, 0.3)'
            }}>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span className="font-semibold text-yellow-700">Aggressive</span>
              </div>
              <p className="text-xs" style={{ color: '#64748b' }}>M-Score -2.22 to -1.78</p>
              <p className="text-xs mt-1" style={{ color: '#64748b' }}>Moderate manipulation risk</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
