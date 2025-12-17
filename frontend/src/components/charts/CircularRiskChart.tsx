"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface CircularRiskChartProps {
    value: number;
    min?: number;
    max?: number;
    label?: string;
    size?: number;
}

export default function CircularRiskChart({
    value,
    min = 0,
    max = 100,
    label = "Risk Score",
    size = 300
}: CircularRiskChartProps) {
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
        const strokeWidth = 25; // Thicker stroke as per image

        const svg = d3.select(chartRef.current)
            .attr("viewBox", `0 0 ${size} ${size}`)
            .attr("preserveAspectRatio", "xMidYMid meet")
            .append("g")
            .attr("transform", `translate(${size / 2},${size / 2})`);

        // Scale
        const scale = d3.scaleLinear()
            .domain([min, max])
            .range([0, 2 * Math.PI]);

        // Background Circle (Track)
        const trackArc = d3.arc()
            .innerRadius(radius - strokeWidth)
            .outerRadius(radius)
            .startAngle(0)
            .endAngle(2 * Math.PI);

        svg.append("path")
            .attr("d", trackArc as any)
            .attr("fill", "#334155") // slate-700
            .attr("opacity", 0.3);

        // Determine color based on value
        let colorHex = "#3b82f6"; // blue-500
        if (value >= 80) colorHex = "#ef4444"; // red-500
        else if (value >= 60) colorHex = "#f97316"; // orange-500
        else if (value >= 40) colorHex = "#eab308"; // yellow-500
        else if (value >= 20) colorHex = "#22c55e"; // green-500

        // Progress Arc
        const progressArc = d3.arc()
            .innerRadius(radius - strokeWidth)
            .outerRadius(radius)
            .startAngle(0)
            .endAngle(scale(Math.min(Math.max(value, min), max)))
            .cornerRadius(12); // Rounded caps

        // Add glow filter
        const defs = svg.append("defs");
        const filter = defs.append("filter")
            .attr("id", "glow");
        filter.append("feGaussianBlur")
            .attr("stdDeviation", "3.5")
            .attr("result", "coloredBlur");
        const feMerge = filter.append("feMerge");
        feMerge.append("feMergeNode")
            .attr("in", "coloredBlur");
        feMerge.append("feMergeNode")
            .attr("in", "SourceGraphic");

        svg.append("path")
            .attr("d", progressArc as any)
            .attr("fill", colorHex)
            .style("filter", "url(#glow)");

        // Center Text Group
        const centerGroup = svg.append("g")
            .attr("text-anchor", "middle");

        // Value
        centerGroup.append("text")
            .attr("y", 10)
            .style("font-size", "64px")
            .style("font-weight", "bold")
            .style("fill", colorHex)
            .text(value.toFixed(1));

        // Label
        centerGroup.append("text")
            .attr("y", 45)
            .style("font-size", "16px")
            .style("font-weight", "500")
            .style("fill", "#94a3b8") // slate-400
            .text(label);

        // "100" Badge (Max Score Indicator)
        const badgeAngle = Math.PI / 4; // 45 degrees
        const badgeRadius = radius + 15;
        const badgeX = Math.sin(badgeAngle) * badgeRadius;
        const badgeY = -Math.cos(badgeAngle) * badgeRadius;

        const badgeGroup = svg.append("g")
            .attr("transform", `translate(${badgeX}, ${badgeY})`);

        badgeGroup.append("circle")
            .attr("r", 12)
            .attr("fill", "#ffffff")
            .attr("stroke", "#e2e8f0")
            .attr("stroke-width", 1);

        badgeGroup.append("text")
            .attr("y", 4)
            .attr("text-anchor", "middle")
            .style("font-size", "10px")
            .style("font-weight", "bold")
            .style("fill", "#64748b") // slate-500
            .text("100");
    };

    return (
        <div className="w-full flex justify-center">
            <svg ref={chartRef} style={{ width: '100%', maxWidth: `${size}px`, height: 'auto' }}></svg>
        </div>
    );
}
