'use client';

import React from 'react';
import { X } from 'lucide-react';

interface ForensicFormulasModalProps {
    isOpen: boolean;
    onClose: () => void;
    analysisData: any;
}

const ForensicFormulasModal: React.FC<ForensicFormulasModalProps> = ({ isOpen, onClose, analysisData }) => {
    if (!isOpen) return null;

    const formulas = [
        {
            title: "Altman Z-Score",
            description: "Predicts bankruptcy risk based on five financial ratios.",
            formula: "Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E",
            value: analysisData?.altman_z_score?.altman_z_score?.z_score,
            variables: [
                "A = Working Capital / Total Assets",
                "B = Retained Earnings / Total Assets",
                "C = EBIT / Total Assets",
                "D = Market Value of Equity / Total Liabilities",
                "E = Sales / Total Assets"
            ],
            color: "text-blue-500"
        },
        {
            title: "Beneish M-Score",
            description: "Detects earnings manipulation.",
            formula: "M = -4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI + 0.115*DEPI - 0.172*SGAI + 4.679*TATA - 0.327*LVGI",
            value: analysisData?.beneish_m_score?.beneish_m_score?.m_score,
            variables: [
                "DSRI = Days Sales in Receivables Index",
                "GMI = Gross Margin Index",
                "AQI = Asset Quality Index",
                "SGI = Sales Growth Index",
                "DEPI = Depreciation Index",
                "SGAI = Sales G&A Expenses Index",
                "TATA = Total Accruals to Total Assets",
                "LVGI = Leverage Index"
            ],
            color: "text-purple-500"
        },
        {
            title: "Debt to Equity Ratio",
            description: "Measures financial leverage.",
            formula: "D/E = Total Liabilities / Shareholders' Equity",
            value: analysisData?.financial_ratios?.financial_ratios?.['2025-03-31']?.debt_to_equity,
            variables: [],
            color: "text-green-500"
        },
        {
            title: "Current Ratio",
            description: "Measures ability to pay short-term obligations.",
            formula: "Current Ratio = Current Assets / Current Liabilities",
            value: "1.32", // Placeholder as per previous mock data
            variables: [],
            color: "text-orange-500"
        }
    ];

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div
                className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 flex flex-col max-h-[80vh]"
                style={{
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
                }}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-slate-800/50 flex-shrink-0">
                    <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">Forensic Formulas</h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Mathematical models used in analysis</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors"
                        aria-label="Close modal"
                    >
                        <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-4 overflow-y-auto space-y-4 flex-grow">
                    {formulas.map((item, index) => (
                        <div key={index} className="p-3 rounded-xl bg-gray-50 dark:bg-slate-800/50 border border-gray-100 dark:border-gray-700">
                            <div className="flex justify-between items-start mb-1">
                                <h4 className={`text-base font-bold ${item.color}`}>{item.title}</h4>
                                {item.value !== undefined && (
                                    <div className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-900 border border-gray-200 dark:border-gray-700 shadow-sm">
                                        <span className="text-[10px] text-gray-500 dark:text-gray-400 mr-1.5">Score:</span>
                                        <span className={`font-bold text-sm ${item.color}`}>{item.value}</span>
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-gray-600 dark:text-gray-300 mb-2">{item.description}</p>

                            <div className="bg-white dark:bg-slate-900 p-2 rounded-lg border border-gray-200 dark:border-gray-700 font-mono text-xs text-gray-800 dark:text-gray-200 overflow-x-auto">
                                {item.formula}
                            </div>

                            {item.variables.length > 0 && (
                                <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-1.5 text-[10px] text-gray-500 dark:text-gray-400">
                                    {item.variables.map((variable, vIndex) => (
                                        <div key={vIndex} className="flex items-center gap-1.5">
                                            <span className="w-1 h-1 rounded-full bg-gray-300 dark:bg-gray-600"></span>
                                            {variable}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Footer */}
                <div className="p-4 bg-gray-50 dark:bg-slate-800/50 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center flex-shrink-0">
                    <span className="text-[10px] text-gray-500 dark:text-gray-400">
                        Standard financial forensic models.
                    </span>
                    <button
                        onClick={onClose}
                        className="px-5 py-2 rounded-lg bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-semibold text-xs hover:opacity-90 transition-opacity"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ForensicFormulasModal;
