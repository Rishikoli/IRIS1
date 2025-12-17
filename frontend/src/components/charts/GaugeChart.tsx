"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface GaugeChartProps {
    value: number;
    min?: number;
    max?: number;
    label?: string;
    units?: string;
    size?: number;
}

export default function GaugeChart({
    value,
    min = 0,
    max = 100,
    label = "Risk Score",
    units = "",
    size = 300
}: GaugeChartProps) {
    const chartRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!chartRef.current) return;
        drawChart();
    }, [value, min, max, size]);

    const drawChart = () => {
        if (!chartRef.current) return;

        // Clear previous chart
        d3.select(chartRef.current).selectAll("*").remove();

        const margin = { top: 20, right: 20, bottom: 20, left: 20 };
        const width = size - margin.left - margin.right;
        const height = size - margin.top - margin.bottom;
        const radius = Math.min(width, height) / 2;

        const svg = d3.select(chartRef.current)
            .attr("viewBox", `0 0 ${size} ${size}`)
            .attr("preserveAspectRatio", "xMidYMid meet")
            .append("g")
            .attr("transform", `translate(${size / 2},${size / 2})`);

        // Scale for mapping value to angle
        // -135 degrees to +135 degrees (270 degree span)
        const scale = d3.scaleLinear()
            .domain([min, max])
            .range([-135 * (Math.PI / 180), 135 * (Math.PI / 180)]);

        // Background Arc
        const backgroundArc = d3.arc()
            .innerRadius(radius * 0.75)
            .outerRadius(radius * 0.85)
            .startAngle(-135 * (Math.PI / 180))
            .endAngle(135 * (Math.PI / 180))
            .cornerRadius(10);

        svg.append("path")
            .attr("d", backgroundArc as any)
            .attr("fill", "#e2e8f0") // slate-200 for light mode track
            .attr("stroke", "none");

        // Value Arc
        const valueAngle = scale(Math.min(Math.max(value, min), max));

        // Determine color based on value
        let color = "#3b82f6"; // blue-500
        if (value >= 80) color = "#ef4444"; // red-500
        else if (value >= 60) color = "#f97316"; // orange-500
        else if (value >= 40) color = "#ec4899"; // pink-500 (was yellow-500)
        else if (value >= 20) color = "#22c55e"; // green-500

        const valueArc = d3.arc()
            .innerRadius(radius * 0.75)
            .outerRadius(radius * 0.85)
            .startAngle(-135 * (Math.PI / 180))
            .endAngle(valueAngle)
            .cornerRadius(10);

        svg.append("path")
            .attr("d", valueArc as any)
            .attr("fill", color)
            .attr("stroke", "none")
            .style("filter", `drop-shadow(0 0 6px ${color}80)`);

        // Ticks (optional, for style)
        const ticks = scale.ticks(5);
        ticks.forEach(tick => {
            if (tick === min || tick === max) return; // Skip start/end if needed
            const angle = scale(tick);
            // Calculate position for tick marks if desired
        });

        // Needle
        const needleLength = radius * 0.7;
        const needleRadius = 5;

        // Needle Group
        const needle = svg.append("g")
            .attr("transform", `rotate(${valueAngle * (180 / Math.PI)})`);

        // Needle Line
        needle.append("path")
            .attr("d", `M0 -${needleRadius} L0 ${needleRadius} L${needleLength} 0 Z`)
            .attr("transform", "rotate(-90)") // Point up initially then rotate
            .attr("fill", "#475569"); // slate-600 for light mode

        // Center Circle
        svg.append("circle")
            .attr("r", 8)
            .attr("fill", "#475569"); // slate-600

        // Value Text
        svg.append("text")
            .attr("y", 40)
            .attr("text-anchor", "middle")
            .style("font-size", "48px")
            .style("font-weight", "bold")
            .style("fill", "#1e293b") // slate-800
            .text(Math.round(value));

        // Units/Label Text
        svg.append("text")
            .attr("y", 70)
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .style("fill", "#64748b") // slate-500
            .text(label);
    };

    return (
        <div className="w-full flex justify-center">
            <svg ref={chartRef} style={{ width: '100%', maxWidth: `${size}px`, height: 'auto' }}></svg>
        </div>
    );
}
