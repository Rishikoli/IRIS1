"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface VerticalAnalysisChartProps {
  data: any;
}

export default function VerticalAnalysisChart({ data }: VerticalAnalysisChartProps) {
  const chartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    drawChart();
  }, [data]);

  const drawChart = () => {
    if (!data || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 40, right: 40, bottom: 60, left: 120 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Extract data from income statement and balance sheet
    const incomeData = data.income_statement || {};
    const balanceData = data.balance_sheet || {};

    // Prepare data for visualization
    const incomeItems = [
      { name: 'Revenue', value: incomeData.revenue_pct || 0, category: 'Income Statement' },
      { name: 'Cost of Goods Sold', value: incomeData.cogs_pct || 0, category: 'Income Statement' },
      { name: 'Gross Profit', value: incomeData.gross_profit_pct || 0, category: 'Income Statement' },
      { name: 'Operating Expenses', value: incomeData.operating_expenses_pct || 0, category: 'Income Statement' },
      { name: 'Operating Income', value: incomeData.operating_income_pct || 0, category: 'Income Statement' },
      { name: 'Net Income', value: incomeData.net_income_pct || 0, category: 'Income Statement' }
    ];

    const balanceItems = [
      { name: 'Total Assets', value: balanceData.total_assets_pct || 0, category: 'Balance Sheet' },
      { name: 'Current Assets', value: balanceData.current_assets_pct || 0, category: 'Balance Sheet' },
      { name: 'Fixed Assets', value: balanceData.fixed_assets_pct || balanceData.non_current_assets_pct || 0, category: 'Balance Sheet' },
      { name: 'Total Liabilities', value: balanceData.total_liabilities_pct || 0, category: 'Balance Sheet' },
      { name: 'Current Liabilities', value: balanceData.current_liabilities_pct || 0, category: 'Balance Sheet' },
      { name: 'Shareholders Equity', value: balanceData.shareholders_equity_pct || 0, category: 'Balance Sheet' }
    ];

    const allData = [...incomeItems, ...balanceItems];

    // Set up scales
    const yScale = d3.scaleBand()
      .domain(allData.map(d => d.name))
      .range([0, height])
      .padding(0.1);

    const xScale = d3.scaleLinear()
      .domain([0, 100])
      .range([0, width]);

    // Color scale based on category
    const colorScale = d3.scaleOrdinal()
      .domain(['Income Statement', 'Balance Sheet'])
      .range(['#7B68EE', '#FF6B9D']);

    // Draw horizontal bars
    svg.selectAll(".bar")
      .data(allData)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("y", d => yScale(d.name) || 0)
      .attr("height", yScale.bandwidth())
      .attr("x", 0)
      .attr("width", d => xScale(d.value))
      .attr("fill", d => colorScale(d.category) as string)
      .attr("rx", 4);

    // Add value labels on bars
    svg.selectAll(".label")
      .data(allData)
      .enter()
      .append("text")
      .attr("class", "label")
      .attr("y", d => (yScale(d.name) || 0) + yScale.bandwidth() / 2)
      .attr("x", d => xScale(d.value) + 5)
      .attr("dy", "0.35em")
      .style("font-size", "12px")
      .style("fill", "#1e293b")
      .text(d => `${d.value.toFixed(1)}%`);

    // Draw axes
    svg.append("g")
      .call(d3.axisLeft(yScale))
      .selectAll("text")
      .style("font-size", "11px");

    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).ticks(5))
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
      .text("Vertical Analysis - Structure Breakdown");

    // Add axis labels
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -60)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Financial Statement Items");

    svg.append("text")
      .attr("y", height + 40)
      .attr("x", width / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("fill", "#64748b")
      .text("Percentage of Total (%)");

    // Add legend
    const legend = svg.selectAll(".legend")
      .data(['Income Statement', 'Balance Sheet'])
      .enter()
      .append("g")
      .attr("class", "legend")
      .attr("transform", (d, i) => `translate(${width - 100},${-30 + i * 20})`);

    legend.append("rect")
      .attr("width", 15)
      .attr("height", 15)
      .style("fill", d => colorScale(d) as string);

    legend.append("text")
      .attr("x", 20)
      .attr("y", 12)
      .text(d => d)
      .style("font-size", "12px")
      .style("fill", "#64748b");
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>Vertical Analysis</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>
          Financial statement structure as percentage of totals
        </p>
      </div>

      <div className="neumorphic-card rounded-2xl p-6" style={{
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
      }}>
        <svg ref={chartRef} className="w-full h-auto"></svg>
      </div>

      {/* Detailed Breakdown */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Income Statement Breakdown */}
        <div className="neumorphic-card rounded-2xl p-6" style={{
          background: 'rgba(255, 255, 255, 0.9)',
          boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
        }}>
          <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>Income Statement Structure</h4>
          <div className="space-y-3">
            {Object.entries(data.income_statement || {}).map(([key, value]: [string, any]) => (
              <div key={key} className="flex justify-between items-center p-3 rounded-xl" style={{
                background: 'rgba(255, 255, 255, 0.7)',
                boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
              }}>
                <span className="font-medium" style={{ color: '#64748b' }}>
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </span>
                <span className="font-bold" style={{ color: '#1e293b' }}>{value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Balance Sheet Breakdown */}
        <div className="neumorphic-card rounded-2xl p-6" style={{
          background: 'rgba(255, 255, 255, 0.9)',
          boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)'
        }}>
          <h4 className="text-lg font-semibold mb-4" style={{ color: '#1e293b' }}>Balance Sheet Structure</h4>
          <div className="space-y-3">
            {Object.entries(data.balance_sheet || {}).map(([key, value]: [string, any]) => (
              <div key={key} className="flex justify-between items-center p-3 rounded-xl" style={{
                background: 'rgba(255, 255, 255, 0.7)',
                boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
              }}>
                <span className="font-medium" style={{ color: '#64748b' }}>
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </span>
                <span className="font-bold" style={{ color: '#1e293b' }}>{value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
