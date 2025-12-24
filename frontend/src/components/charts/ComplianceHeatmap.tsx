
import React from 'react';

interface ComplianceHeatmapProps {
    scores: Record<string, any>; // { "tax_law": 90, "labor_law": 50 ... }
}

const ComplianceHeatmap: React.FC<ComplianceHeatmapProps> = ({ scores }) => {
    if (!scores || Object.keys(scores).length === 0) return null;

    const items = Object.entries(scores).map(([key, value]) => {
        // Handle nested score objects vs direct numbers
        const score = typeof value === 'object' && value !== null ? (value.score || 0) : Number(value);
        const name = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        // Color Logic
        let bgClass = 'bg-red-500';
        if (score >= 80) bgClass = 'bg-emerald-500';
        else if (score >= 60) bgClass = 'bg-yellow-500';

        return { key, name, score, bgClass };
    });

    return (
        <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                <span>🧩</span> Regulatory Heatmap
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {items.map((item) => (
                    <div
                        key={item.key}
                        className={`
                            relative group cursor-pointer overflow-hidden rounded-xl p-4 
                            transition-all duration-300 hover:scale-105 hover:shadow-lg
                            ${item.bgClass} bg-opacity-10 border hover:border-opacity-100
                        `}
                        style={{ borderColor: 'currentColor' }} // Inherit color for border
                    >
                        {/* Background Fill for visual progress */}
                        <div
                            className={`absolute bottom-0 left-0 w-full opacity-20 ${item.bgClass}`}
                            style={{ height: `${item.score}%` }}
                        />

                        <div className="relative z-10 flex flex-col h-full justify-between">
                            <span className="text-xs font-bold text-slate-600 uppercase tracking-wide opacity-80">
                                {item.name}
                            </span>

                            <div className="flex items-end justify-between mt-2">
                                <span className={`text-2xl font-black ${item.bgClass.replace('bg-', 'text-')}`}>
                                    {item.score.toFixed(0)}
                                </span>
                                <span className="text-[10px] bg-white px-1.5 py-0.5 rounded text-slate-500 font-mono">
                                    /100
                                </span>
                            </div>
                        </div>

                        {/* Hover Tooltip (Simple) */}
                        <div className="absolute inset-0 bg-black/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                            <span className="text-white font-bold text-sm">View Details</span>
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-4 flex gap-4 text-xs text-slate-400 justify-end">
                <span className="flex items-center gap-1"><div className="w-2 h-2 rounded bg-emerald-500"></div> Compliant 80+</span>
                <span className="flex items-center gap-1"><div className="w-2 h-2 rounded bg-yellow-500"></div> Warning 60-79</span>
                <span className="flex items-center gap-1"><div className="w-2 h-2 rounded bg-red-500"></div> Violation &lt;60</span>
            </div>
        </div>
    );
};

export default ComplianceHeatmap;
