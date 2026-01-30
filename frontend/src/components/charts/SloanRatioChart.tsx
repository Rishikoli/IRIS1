"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface SloanRatioChartProps {
    data: any;
}

export default function SloanRatioChart({ data }: SloanRatioChartProps) {
    const chartRef = useRef<SVGSVGElement>(null);
    const trendRef = useRef<SVGSVGElement>(null);

    // Normalize data structure
    // Backend returns: results["sloan_ratio"]["sloan_analysis"] = { "2024-03-31": { ... } }
    const sloanAnalysis = data?.sloan_analysis || data || {};

    // Convert object to array for trend analysis and sort by date
    const history = Object.entries(sloanAnalysis)
        .map(([date, details]: [string, any]) => ({
            period: date,
            ...details
        }))
        .sort((a, b) => new Date(a.period).getTime() - new Date(b.period).getTime());

    // Get latest period data
    const latestData = history.length > 0 ? history[history.length - 1] : null;
    const sloanPct = latestData ? latestData.sloan_ratio_pct : 0;

    // Variables for display
    const components = latestData ? {
        "Net Income": latestData.net_income,
        "Operating Cash Flow": latestData.operating_cash_flow,
        "Accruals (Diff)": latestData.accruals,
        "Total Assets": latestData.total_assets
    } : {};

    useEffect(() => {
        if (chartRef.current) {
            drawGaugeChart();
        }
    }, [data, sloanPct]);

    useEffect(() => {
        if (trendRef.current && history.length > 1) {
            drawTrendChart();
        }
    }, [history]);

    const drawGaugeChart = () => {
        if (!chartRef.current) return;
        d3.select(chartRef.current).selectAll("*").remove();

        const margin = { top: 40, right: 40, bottom: 60, left: 40 };
        const width = 800 - margin.left - margin.right;
        const height = 180 - margin.top - margin.bottom;

        const svg = d3.select(chartRef.current)
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Define Zones
        // Zones: -25% to +25% range for visualization
        const xScale = d3.scaleLinear()
            .domain([-25, 25])
            .range([0, width]);

        // Risk Zones
        const zones = [
            { min: -25, max: 5, color: "#10B981", label: "Safe Zone (< 5%)" },        // Green
            { min: 5, max: 10, color: "#F59E0B", label: "Moderate Risk (5-10%)" },    // Yellow
            { min: 10, max: 25, color: "#EF4444", label: "High Risk (> 10%)" }        // Red
        ];

        // Draw Zones
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
        const clampedScore = Math.max(-25, Math.min(25, sloanPct));
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
            .text(`${sloanPct.toFixed(2)}%`);
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

        const parseTime = d3.timeParse("%Y-%m-%d");
        const trendData = history.map((d: any) => ({
            date: parseTime(d.period) || new Date(d.period),
            value: Number(d.sloan_ratio_pct)
        }));

        const x = d3.scaleTime()
            .domain(d3.extent(trendData, (d: any) => d.date) as [Date, Date])
            .range([0, width]);

        const yValMin = d3.min(trendData, (d: any) => d.value) as number;
        const yValMax = d3.max(trendData, (d: any) => d.value) as number;
        // Ensure Y axis covers standard range appropriately
        const y = d3.scaleLinear()
            .domain([Math.min(-10, yValMin), Math.max(15, yValMax)])
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

        // Threshold Line (10%)
        const thresholdY = y(10);
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
                .text("High Risk (10%)");
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

    const riskColor = sloanPct > 10 ? '#EF4444' : (sloanPct > 5 ? '#F59E0B' : '#10B981');
    const riskLabel = sloanPct > 10 ? 'HIGH RISK' : (sloanPct > 5 ? 'MEDIUM RISK' : 'SAFE ZONE');
    const riskDesc = sloanPct > 10 ? 'High Accruals - Possible Earnings Manipulation' : 'Earnings Backed by Cash Flow';

    // Helper to format currency
    const formatCurrency = (val: number) => {
        if (val >= 1e9) return `$ ${(val / 1e9).toFixed(2)} B`;
        if (val >= 1e6) return `$ ${(val / 1e6).toFixed(2)} M`;
        return `$ ${val.toLocaleString()}`;
    };

    return (
        <div className="w-full space-y-8">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex-1">
                    <h3 className="text-2xl font-bold text-slate-800">Sloan Ratio Analysis</h3>
                    <p className="text-slate-500">
                        Measures the quality of earnings by comparing Net Income to Cash Flow.
                    </p>
                </div>
                <div className={`px-6 py-3 rounded-2xl border-2 flex flex-col items-center min-w-[180px]`}
                    style={{ borderColor: riskColor, backgroundColor: `${riskColor}10` }}>
                    <span className="text-3xl font-bold" style={{ color: riskColor }}>{sloanPct.toFixed(2)}%</span>
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
                    <h4 className="text-lg font-bold text-slate-700 mb-4">Calculation Breakdown</h4>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-slate-50 text-slate-500 font-medium">
                                <tr>
                                    <th className="p-3 rounded-l-lg">Component</th>
                                    <th className="p-3 text-right rounded-r-lg">Value</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {Object.entries(components).map(([key, rawVal]: [string, any]) => {
                                    const val = Number(rawVal);
                                    return (
                                        <tr key={key} className="hover:bg-slate-50/50 transition-colors">
                                            <td className="p-3 font-semibold text-slate-700">{key}</td>
                                            <td className="p-3 text-right font-mono font-bold text-slate-700">
                                                {formatCurrency(val)}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                    <div className="mt-4 p-4 bg-slate-50 rounded-xl text-xs text-slate-500">
                        <strong>Formula:</strong> (Net Income - Operating Cash Flow) / Total Assets
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
