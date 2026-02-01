"use client";

import React from 'react';
import { FiAlertTriangle, FiAlertCircle, FiCheckCircle, FiShield } from 'react-icons/fi';

interface FlagProps {
    type: 'danger' | 'warning' | 'safe';
    title: string;
    condition: string;
    value: string;
    message: string;
}

const FlagRow = ({ type, title, condition, value, message }: FlagProps) => {
    const icon = type === 'danger' ? <FiAlertTriangle className="w-5 h-5 text-white" />
        : type === 'warning' ? <FiAlertCircle className="w-5 h-5 text-white" />
            : <FiCheckCircle className="w-5 h-5 text-white" />;

    const bg = type === 'danger' ? 'bg-red-500' : type === 'warning' ? 'bg-amber-500' : 'bg-green-500';
    const border = type === 'danger' ? 'border-red-100 bg-red-50' : type === 'warning' ? 'border-amber-100 bg-amber-50' : 'border-green-100 bg-green-50';

    return (
        <div className={`flex items-start gap-4 p-4 rounded-xl border ${border} transition-all hover:shadow-md`}>
            <div className={`p-2 rounded-lg ${bg} shadow-sm shrink-0`}>
                {icon}
            </div>
            <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                    <h4 className="font-bold text-slate-800">{title}</h4>
                    <div className="text-xs font-mono px-2 py-1 rounded bg-white border border-slate-200 shadow-sm text-slate-600">
                        {value}
                    </div>
                </div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">{condition}</p>
                <p className="text-sm text-slate-700 leading-relaxed">{message}</p>
            </div>
        </div>
    );
};

interface SebiFlagPanelProps {
    data: {
        singleStockExposure: number; // %
        sectorExposure: number;      // %
        zScore: number;
        hasShellLinks: boolean;
        turnoverRatio: number; // > X is risky
    }
}

export default function SebiFlagPanel({ data }: SebiFlagPanelProps) {
    // Logic Config
    const LIMIT_STOCK = 10;
    const LIMIT_SECTOR = 25;
    const LIMIT_DISTRESS = 1.8;
    const LIMIT_TURNOVER = 5.0; // Artificial hypothetical limit

    const flags: FlagProps[] = [];

    // Check 1: Single Stock Concentration
    if (data.singleStockExposure > LIMIT_STOCK) {
        flags.push({
            type: 'danger',
            title: 'Concentration Breach',
            condition: `Single Stock > ${LIMIT_STOCK}%`,
            value: `${data.singleStockExposure}%`,
            message: 'Portfolio is heavily exposed to a single entity, violating SEBI diversification guidelines for standard advisor models.'
        });
    } else {
        flags.push({
            type: 'safe',
            title: 'Diversification Check',
            condition: `Single Stock < ${LIMIT_STOCK}%`,
            value: `${data.singleStockExposure}%`,
            message: 'Portfolio exposure is within regulatory safety limits.'
        });
    }

    // Check 2: Sector Concentration
    if (data.sectorExposure > LIMIT_SECTOR) {
        flags.push({
            type: 'warning',
            title: 'Sector Overweight',
            condition: `Sector > ${LIMIT_SECTOR}%`,
            value: `${data.sectorExposure}%`,
            message: 'High concentration in a single sector increases systematic risk exposure.'
        });
    }

    // Check 3: Distress + Exposure
    if (data.zScore < LIMIT_DISTRESS && data.singleStockExposure > 5) {
        flags.push({
            type: 'danger',
            title: 'Distress Exposure',
            condition: 'Z-Score < 1.8 + Exposure > 5%',
            value: `Z:${data.zScore}`,
            message: 'Significant capital allocated to a company indicating high bankruptcy probability.'
        });
    }

    // Check 4: Shell Network
    if (data.hasShellLinks) {
        flags.push({
            type: 'danger',
            title: 'Shell Network Alert',
            condition: 'Shell Link Detected',
            value: 'CRITICAL',
            message: 'Entity has direct transactional links to confirmed shell companies. Immediate due diligence required.'
        });
    }

    return (
        <div className="neumorphic-card rounded-2xl p-6 bg-white">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
                <div className="p-2 bg-slate-800 rounded-lg">
                    <FiShield className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h3 className="text-xl font-bold text-slate-800">Regulatory Breach Panel</h3>
                    <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">AS PER SEBI RIA GUIDELINES</p>
                </div>
            </div>

            <div className="space-y-4">
                {flags.map((flag, idx) => (
                    <FlagRow key={idx} {...flag} />
                ))}
            </div>
        </div>
    );
}
