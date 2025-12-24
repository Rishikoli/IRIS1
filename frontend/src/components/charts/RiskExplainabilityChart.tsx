'use client';

import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
    Cell
} from 'recharts';

interface ExplainabilityProps {
    shapValues: Record<string, number>;
}

export default function RiskExplainabilityChart({ shapValues }: ExplainabilityProps) {
    // 1. Transform shapValues dict to array for Recharts
    // format: [{ factor: "Financial", impact: 15 }, { factor: "Market", impact: -5 }]
    const data = Object.entries(shapValues)
        .filter(([key]) => key !== 'base_value') // Exclude base value from bars
        .map(([key, value]) => ({
            factor: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), // "financial_stability" -> "Financial Stability"
            impact: value
        }))
        .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact)); // Sort by magnitude

    // Custom tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const value = payload[0].value;
            const isRiskIncreasing = value > 0;

            return (
                <div className="bg-slate-900/90 border border-slate-700 p-3 rounded-lg shadow-xl backdrop-blur-md">
                    <p className="font-semibold text-slate-100">{label}</p>
                    <div className="flex items-center gap-2 mt-1">
                        <span className={isRiskIncreasing ? "text-red-400" : "text-green-400"}>
                            {value > 0 ? "+" : ""}{value} Points
                        </span>
                        <span className="text-xs text-slate-400">
                            {isRiskIncreasing ? "(Increasing Risk)" : "(Reducing Risk)"}
                        </span>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="w-full h-[300px] mt-4">
            <div className="mb-2 text-center">
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">Why is the score {shapValues.base_value ? Math.round(data.reduce((acc, curr) => acc + curr.impact, shapValues.base_value)) : 'calculated'}?</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">Deviation from Neutral Baseline ({shapValues.base_value || 50})</p>
            </div>

            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    layout="vertical"
                    data={data}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                    <XAxis
                        type="number"
                        domain={['dataMin - 5', 'dataMax + 5']}
                        stroke="#64748b"
                        tick={{ fill: '#64748b', fontSize: 10 }}
                    />
                    <YAxis
                        dataKey="factor"
                        type="category"
                        width={120}
                        stroke="#64748b"
                        tick={{ fill: '#475569', fontSize: 11 }}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }} />
                    <ReferenceLine x={0} stroke="#94a3b8" />
                    <Bar dataKey="impact" name="Risk Impact" radius={[0, 4, 4, 0]}>
                        {data.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.impact > 0 ? '#ef4444' : '#22c55e'}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
