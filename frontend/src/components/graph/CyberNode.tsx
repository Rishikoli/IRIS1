
import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { ShieldAlert, Building2, User, HelpCircle, Zap } from 'lucide-react';

const CyberNode = ({ data, selected }: any) => {
    // Determine Type & Style
    const isShell = data.type === 'shell' || data.isShell;
    const isCompany = data.type === 'company';
    const isPerson = data.type === 'person';

    // Risk Level Colors
    const riskScore = data.riskScore || data.risk_score || 0;
    const isHighRisk = riskScore > 75;

    let borderColor = 'border-slate-200';
    let glowColor = 'shadow-sm';
    let icon = <HelpCircle size={16} className="text-slate-400" />;
    let labelColor = 'text-slate-700';
    let bgColor = 'bg-white';

    if (isShell || isHighRisk) {
        borderColor = 'border-red-400';
        glowColor = selected ? 'shadow-[0_0_15px_rgba(239,68,68,0.4)]' : (isShell ? 'shadow-[0_0_8px_rgba(239,68,68,0.2)]' : 'shadow-sm');
        icon = <ShieldAlert size={16} className="text-red-500 animate-pulse" />;
        labelColor = 'text-red-700';
        bgColor = 'bg-red-50/80';
    } else if (isCompany) {
        borderColor = 'border-blue-400';
        glowColor = selected ? 'shadow-[0_0_15px_rgba(59,130,246,0.4)]' : 'shadow-sm';
        icon = <Building2 size={16} className="text-blue-500" />;
        labelColor = 'text-blue-700';
        bgColor = 'bg-blue-50/80';
    } else if (isPerson) {
        borderColor = 'border-emerald-400';
        glowColor = selected ? 'shadow-md' : 'shadow-sm';
        icon = <User size={16} className="text-emerald-500" />;
        labelColor = 'text-emerald-700';
        bgColor = 'bg-emerald-50/80';
    }

    return (
        <div className={`
            relative px-2 py-1.5 rounded-lg border flex flex-col items-center min-w-[100px] transition-all duration-300
            ${borderColor} ${bgColor} ${glowColor} backdrop-blur-sm
        `}>
            {/* Header: Icon + Label */}
            <div className="flex items-center gap-1.5 w-full">
                <div className="p-0.5 rounded-md bg-white border border-slate-100 shadow-sm">
                    {icon}
                </div>
                <div className={`text-[10px] font-bold font-sans truncate flex-1 ${labelColor}`}>
                    {data.label}
                </div>
            </div>

            {/* Content: Minimal Risk Indicator (Dot instead of full bar) */}
            {riskScore > 50 && (
                <div className="flex items-center justify-end w-full mt-1 gap-1">
                    <span className={`h-1.5 w-1.5 rounded-full ${isHighRisk ? 'bg-red-500 animate-pulse' : 'bg-orange-400'}`}></span>
                    <span className="text-[9px] font-mono text-slate-500">{riskScore}%</span>
                </div>
            )}

            {/* Tag for Shell - Smaller */}
            {isShell && (
                <div className="absolute -top-1.5 -right-1 bg-red-500 text-white text-[8px] font-bold px-1.5 py-0 rounded-full border border-white flex items-center gap-0.5 shadow-sm z-10">
                    <Zap size={6} fill="white" />
                </div>
            )}

            {/* Connection Handles - Smaller */}
            <Handle type="target" position={Position.Top} className="!bg-slate-400 !w-1.5 !h-1.5 !border-1 !border-white" />
            <Handle type="source" position={Position.Bottom} className="!bg-slate-400 !w-1.5 !h-1.5 !border-1 !border-white" />
        </div>
    );
};

export default memo(CyberNode);
