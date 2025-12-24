'use client';

import React from 'react';
import RiskExplainabilityChart from './charts/RiskExplainabilityChart';

interface ShellAIRiskAttributionProps {
    shapValues: Record<string, number>;
    title?: string;
}

export default function ShellAIRiskAttribution({
    shapValues,
    title = "Shell AI Risk Attribution (SHAP)"
}: ShellAIRiskAttributionProps) {

    if (!shapValues) {
        return null;
    }

    return (
        <div className="neumorphic-card rounded-3xl p-8 overflow-hidden relative" style={{
            background: 'var(--card)',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255,255,255,0.1)'
        }}>
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-purple-500/20 rounded-xl">
                    <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>
                <div>
                    <h3 className="text-xl font-bold" style={{ color: 'var(--foreground)' }}>{title}</h3>
                    <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>AI-driven factor analysis explaining the risk score</p>
                </div>
            </div>

            <div className="bg-slate-50/50 dark:bg-slate-900/30 rounded-2xl p-4 border border-slate-200 dark:border-slate-800">
                <RiskExplainabilityChart shapValues={shapValues} />
            </div>
        </div>
    );
}
