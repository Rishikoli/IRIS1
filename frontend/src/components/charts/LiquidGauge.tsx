
import React, { useEffect, useRef } from 'react';

interface LiquidGaugeProps {
    value: number; // 0 to 100
    title?: string;
}

const LiquidGauge: React.FC<LiquidGaugeProps> = ({ value, title = "Compliance Score" }) => {
    // Clamp value
    const percentage = Math.min(Math.max(value, 0), 100);

    // Determine color based on score
    const getColor = (s: number) => {
        if (s >= 80) return '#22c55e'; // Green
        if (s >= 60) return '#eab308'; // Yellow
        return '#ef4444'; // Red
    };

    const color = getColor(percentage);

    return (
        <div className="flex flex-col items-center justify-center">
            <div className="relative w-48 h-48 rounded-full bg-slate-100 shadow-inner border-4 border-white overflow-hidden">
                {/* Wave Container */}
                <div className="absolute bottom-0 left-0 w-full transition-all duration-1000 ease-out"
                    style={{ height: `${percentage}%` }}>

                    {/* Front Wave */}
                    <div className="absolute bottom-0 w-[200%] h-full opacity-60 animate-wave-slow"
                        style={{
                            background: color,
                            left: '-50%'
                        }}>
                    </div>

                    {/* Back Wave */}
                    <div className="absolute bottom-0 w-[200%] h-full opacity-40 animate-wave-fast"
                        style={{
                            background: color,
                            left: '-50%'
                        }}>
                    </div>
                </div>

                {/* Text Overlay */}
                <div className="absolute inset-0 flex flex-col items-center justify-center z-10 glass-effect">
                    <span className="text-4xl font-bold font-mono text-slate-800 drop-shadow-sm">
                        {percentage.toFixed(0)}%
                    </span>
                    <span className="text-xs font-semibold uppercase text-slate-500 mt-1">
                        {title}
                    </span>
                </div>
            </div>

            <style jsx>{`
                @keyframes wave {
                    0% { transform: translateX(0) translateZ(0) scaleY(1); }
                    50% { transform: translateX(-25%) translateZ(0) scaleY(0.85); }
                    100% { transform: translateX(-50%) translateZ(0) scaleY(1); }
                }
                .animate-wave-slow {
                    animation: wave 8s linear infinite;
                    border-radius: 40%;
                }
                .animate-wave-fast {
                    animation: wave 6s linear infinite;
                    border-radius: 45%;
                }
            `}</style>
        </div>
    );
};

export default LiquidGauge;
