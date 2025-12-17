"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ZScoreChartProps {
  data: any;
}

export default function ZScoreChart({ data }: ZScoreChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    drawChart();
  }, [data]);

  const drawChart = () => {
    if (!data || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 40, right: 120, bottom: 60, left: 60 }; // Increased right margin for labels
    const width = 800 - margin.left - margin.right; // Increased base width for better aspect ratio
    const height = 400 - margin.top - margin.bottom; // Increased base height

    const svg = d3.select(chartRef.current)
      .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Z-Score zones covering negative values
    const zones = [
      { range: [-20, 1.8], label: 'Distress Zone', color: '#ef4444', description: 'High bankruptcy risk' },
      { range: [1.8, 3.0], label: 'Grey Zone', color: '#f59e0b', description: 'Moderate risk' },
      { range: [3.0, 20], label: 'Safe Zone', color: '#4ade80', description: 'Low bankruptcy risk' }
    ];

    const zScore = parseFloat(data.z_score) || 0;

    // Scale for Y-axis (Z-Score values)
    // Dynamic domain to ensure the score is always visible
    const minDomain = Math.min(-5, zScore - 1);
    const maxDomain = Math.max(8, zScore + 1);

    const yScale = d3.scaleLinear()
      .domain([minDomain, maxDomain])
      .range([height, 0]);

    // Draw zone backgrounds
    zones.forEach((zone, index) => {
      // Clamp zone ranges to the visible domain for drawing
      const zMin = Math.max(zone.range[0], minDomain);
      const zMax = Math.min(zone.range[1], maxDomain);

      if (zMin < zMax) {
        const yStart = yScale(zMin);
        const yEnd = yScale(zMax);

        svg.append("rect")
          .attr("x", 0)
          .attr("y", yEnd)
          .attr("width", width)
          .attr("height", Math.abs(yStart - yEnd))
          .attr("fill", zone.color)
          .attr("opacity", 0.1);

        // Add zone labels - positioned at the midpoint of the visible zone part
        // Only show label if the zone is significantly visible
        if (Math.abs(yStart - yEnd) > 20) {
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
        }
      }
    });

    // Draw Y-axis
    svg.append("g")
      .call(d3.axisLeft(yScale).ticks(10))
      .selectAll("text")
      .style("font-size", "12px");

    // Draw horizontal grid lines for thresholds
    svg.selectAll(".grid-line")
      .data([1.8, 3.0])
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

    // Draw zero line if visible
    if (minDomain < 0 && maxDomain > 0) {
      svg.append("line")
        .attr("x1", 0)
        .attr("x2", width)
        .attr("y1", yScale(0))
        .attr("y2", yScale(0))
        .style("stroke", "#94a3b8")
        .style("stroke-width", 1);
    }

    // Draw current Z-Score line
    const scoreY = yScale(zScore);

    svg.append("line")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", scoreY)
      .attr("y2", scoreY)
      .style("stroke", "#7B68EE")
      .style("stroke-width", 3)
      .style("stroke-dasharray", "none");

    // Add score indicator circle
    svg.append("circle")
      .attr("cx", width / 2)
      .attr("cy", scoreY)
      .attr("r", 8)
      .attr("fill", "#7B68EE")
      .style("filter", "drop-shadow(0 0 5px rgba(123, 104, 238, 0.5))");

    // Add score value label
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", scoreY - 15)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .style("fill", "#7B68EE")
      .text(zScore.toFixed(2));

    // Add risk level label
    const riskLevel = zScore < 1.8 ? 'DISTRESS' : zScore < 3.0 ? 'GREY' : 'SAFE';
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", scoreY + 20)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .style("fill", zScore < 1.8 ? '#ef4444' : zScore < 3.0 ? '#f59e0b' : '#4ade80')
      .text(riskLevel);

    // Add chart title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .style("fill", "#1e293b")
      .text("Altman Z-Score Analysis");

    // Add axis label
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Z-Score Value");
  };

  const zScore = parseFloat(data.z_score) || 0;
  const riskLevel = zScore < 1.8 ? 'High' : zScore < 3.0 ? 'Medium' : 'Low';
  const riskColor = zScore < 1.8 ? '#ef4444' : zScore < 3.0 ? '#f59e0b' : '#4ade80';

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>Altman Z-Score</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>
          Bankruptcy risk assessment using Altman's Z-Score model
        </p>
      </div>

      <div className="neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* Z-Score Details */}
      <div className="mt-6 neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>Z-Score Analysis Details</h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 rounded-xl" style={{
            background: `rgba(${riskColor.includes('#ef4444') ? '239, 68, 68' : riskColor.includes('#f59e0b') ? '245, 158, 11' : '74, 222, 128'}, 0.1)`,
            border: `2px solid ${riskColor}30`
          }}>
            <div className="text-2xl font-bold" style={{ color: riskColor }}>{zScore.toFixed(2)}</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Z-Score</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: `rgba(${riskColor.includes('#ef4444') ? '239, 68, 68' : riskColor.includes('#f59e0b') ? '245, 158, 11' : '74, 222, 128'}, 0.1)`,
            border: `2px solid ${riskColor}30`
          }}>
            <div className="text-lg font-bold" style={{ color: riskColor }}>{riskLevel} RISK</div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Risk Level</div>
          </div>

          <div className="text-center p-4 rounded-xl" style={{
            background: `rgba(${riskColor.includes('#ef4444') ? '239, 68, 68' : riskColor.includes('#f59e0b') ? '245, 158, 11' : '74, 222, 128'}, 0.1)`,
            border: `2px solid ${riskColor}30`
          }}>
            <div className="text-sm font-bold" style={{ color: riskColor }}>
              {zScore < 1.8 ? 'Bankruptcy likely within 2 years' :
                zScore < 3.0 ? 'Financial distress possible' : 'Strong financial health'}
            </div>
            <div className="text-sm font-medium" style={{ color: '#64748b' }}>Interpretation</div>
          </div>
        </div>

        {/* Zone Explanations */}
        <div className="space-y-3">
          <h5 className="font-semibold" style={{ color: '#1e293b' }}>Risk Zone Explanations</h5>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-xl" style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '2px solid rgba(239, 68, 68, 0.3)'
            }}>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="font-semibold text-red-700">Distress Zone</span>
              </div>
              <p className="text-xs" style={{ color: '#64748b' }}>Z-Score &lt; 1.8</p>
              <p className="text-xs mt-1" style={{ color: '#64748b' }}>High probability of bankruptcy</p>
            </div>

            <div className="p-3 rounded-xl" style={{
              background: 'rgba(245, 158, 11, 0.1)',
              border: '2px solid rgba(245, 158, 11, 0.3)'
            }}>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span className="font-semibold text-yellow-700">Grey Zone</span>
              </div>
              <p className="text-xs" style={{ color: '#64748b' }}>Z-Score 1.8 - 3.0</p>
              <p className="text-xs mt-1" style={{ color: '#64748b' }}>Moderate bankruptcy risk</p>
            </div>

            <div className="p-3 rounded-xl" style={{
              background: 'rgba(74, 222, 128, 0.1)',
              border: '2px solid rgba(74, 222, 128, 0.3)'
            }}>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="font-semibold text-green-700">Safe Zone</span>
              </div>
              <p className="text-xs" style={{ color: '#64748b' }}>Z-Score &gt; 3.0</p>
              <p className="text-xs mt-1" style={{ color: '#64748b' }}>Low bankruptcy risk</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
