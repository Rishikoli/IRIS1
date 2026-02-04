"use client";

import React from 'react';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ZAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceArea,
    ReferenceLine,
    Cell
} from 'recharts';

interface SebiRiskCompositionProps {
    data: {
        mScore: number;       // X: Manipulation (>-1.78 is bad)
        zScore: number;       // Y: Distress (<1.8 is bad)
        concentration: number; // Z: Portfolio % (Size)
        name: string;
        sector: string;
    }[];
}

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <div className="bg-white/95 backdrop-blur-md p-4 rounded-xl shadow-xl border border-slate-200 text-sm">
                <h4 className="font-bold text-slate-800 mb-2">{data.name}</h4>
                <div className="space-y-1">
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Sector:</span>
                        <span className="font-medium">{data.sector}</span>
                    </div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Concentration:</span>
                        <span className="font-bold text-blue-600">{data.concentration}%</span>
                    </div>
                    <div className="border-t border-slate-100 my-2 pt-2"></div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">M-Score (Manip):</span>
                        <span className={`font-mono font-bold ${data.mScore > -1.78 ? 'text-red-500' : 'text-green-600'}`}>
                            {data.mScore.toFixed(2)}
                        </span>
                    </div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Z-Score (Risk):</span>
                        <span className={`font-mono font-bold ${data.zScore < 1.8 ? 'text-red-500' : 'text-green-600'}`}>
                            {data.zScore.toFixed(2)}
                        </span>
                    </div>
                </div>
            </div>
        );
    }
    return null;
};

export default function SebiRiskComposition({ data }: SebiRiskCompositionProps) {
    // Color logic based on Quadrants
    // Q1 (Top-Right): Safe (Low Manip, Low Risk) -> Green
    // Q2 (Top-Left): Manipulator? (High Manip, Low Risk) -> Orange
    // Q3 (Bottom-Left): DANGER (High Manip, High Disstress) -> Red
    // Q4 (Bottom-Right): Distress (Low Manip, High Distress) -> Yellow

    // Normalized logic for plotting:
    // X: Beniesh M-Score. -2.22 (Good) to -1.78 (Bad). Plot from -3 to 0.
    // Y: Altman Z-Score. 3.0 (Safe) to 1.8 (Grey) to 0 (Distress). Plot from 0 to 4.

    return (
        <div className="w-full h-[600px] neumorphic-card rounded-2xl bg-white/50 flex flex-col overflow-hidden">
            {/* Header Section: Title & Legend */}
            <div className="flex flex-col md:flex-row justify-between items-start p-6 bg-white/40 border-b border-slate-100/50">
                <div className="mb-4 md:mb-0">
                    <h3 className="text-lg font-bold text-slate-700 flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                        SEBI Risk Radar
                    </h3>
                    <p className="text-xs text-slate-500">Manipulation vs. Distress vs. Concentration</p>
                </div>

                {/* Legend as a relative block */}
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs border border-slate-200 bg-white/60 p-2 rounded-lg">
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-red-500"></span> <span className="text-slate-600">High Danger</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-orange-500"></span> <span className="text-slate-600">Manip Risk</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-yellow-400"></span> <span className="text-slate-600">Distress Risk</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-green-500"></span> <span className="text-slate-600">Strong / Safe</span>
                    </div>
                    <div className="col-span-2 mt-1 pt-1 border-t border-slate-200 text-slate-400 text-[10px] text-center">
                        Bubble Size = Concentration %
                    </div>
                </div>
            </div>

            {/* Chart Section */}
            <div className="flex-1 min-h-0 w-full p-2">
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 80 }}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />

                        <ReferenceArea x1={-1.78} x2={10} y1={0} y2={1.8} fill="#EF4444" fillOpacity={0.05} />
                        <ReferenceArea x1={-10} x2={-2.22} y1={3} y2={10} fill="#10B981" fillOpacity={0.05} />

                        <XAxis
                            type="number"
                            dataKey="mScore"
                            name="Manipulation"
                            domain={[-4, 0]}
                            label={{ value: 'Beneish M-Score (Right = Higher Manipulation Risk)', position: 'bottom', offset: 0 }}
                            tick={{ fontSize: 12 }}
                        />

                        <YAxis
                            type="number"
                            dataKey="zScore"
                            name="Distress"
                            domain={[0, 5]}
                            label={{
                                value: 'Altman Z-Score (Lower = Higher Bankruptcy Risk)',
                                angle: -90,
                                position: 'left',
                                style: { textAnchor: 'middle', fill: '#64748b' },
                                offset: 0
                            }}
                            tick={{ fontSize: 12 }}
                        />

                        <ZAxis type="number" dataKey="concentration" range={[100, 1000]} name="Concentration" />

                        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />

                        <ReferenceLine x={-1.78} stroke="#EF4444" strokeDasharray="3 3" label={{ position: 'top', value: 'Manip', fill: '#EF4444', fontSize: 10 }} />
                        <ReferenceLine y={1.8} stroke="#F59E0B" strokeDasharray="3 3" label={{ position: 'right', value: 'Distress', fill: '#F59E0B', fontSize: 10 }} />

                        <Scatter name="Portfolio" data={data} fill="#8884d8">
                            {data.map((entry, index) => {
                                const isManip = entry.mScore > -1.78;
                                const isDistress = entry.zScore < 1.8;
                                let color = '#10B981';

                                if (isManip && isDistress) color = '#EF4444';
                                else if (isManip) color = '#F97316';
                                else if (isDistress) color = '#EAB308';

                                return <Cell key={`cell-${index}`} fill={color} stroke="#fff" strokeWidth={2} />;
                            })}
                        </Scatter>
                    </ScatterChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
