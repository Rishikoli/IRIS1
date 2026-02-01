'use client'

import { FiSearch, FiAlertCircle, FiArrowLeft } from 'react-icons/fi'

interface CompanyNotFoundProps {
    companySymbol: string
    onBack: () => void
}

export default function CompanyNotFound({ companySymbol, onBack }: CompanyNotFoundProps) {
    return (
        <div className="max-w-2xl mx-auto py-12 px-4">
            <div className="neumorphic-card p-8 text-center" style={{
                background: '#f0f0f0',
                borderRadius: '1.5rem',
                boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff'
            }}>
                {/* Animated Icon Container */}
                <div className="relative w-32 h-32 mx-auto mb-8">
                    <div className="absolute inset-0 rounded-full bg-red-100/50 animate-ping opacity-20"></div>
                    <div className="relative w-32 h-32 rounded-full flex items-center justify-center neumorphic-inset" style={{
                        background: '#f0f0f0',
                        boxShadow: 'inset 6px 6px 12px #d0d0d0, inset -6px -6px 12px #ffffff'
                    }}>
                        <FiAlertCircle className="w-16 h-16 text-red-500" />
                    </div>
                </div>

                <h2 className="text-3xl font-bold text-gray-800 mb-4">
                    Company Not Found
                </h2>

                <div className="bg-red-50 rounded-xl p-4 mb-6 border border-red-100">
                    <p className="text-lg text-red-600 font-medium font-mono">
                        {companySymbol}
                    </p>
                </div>

                <p className="text-gray-600 mb-8 max-w-md mx-auto leading-relaxed">
                    We couldn't find valid financial data for this ticker. This could be because:
                    <ul className="text-sm mt-3 space-y-2 text-left bg-white/50 p-4 rounded-lg">
                        <li className="flex items-start">
                            <span className="mr-2">•</span> The company is delisted or suspended.
                        </li>
                        <li className="flex items-start">
                            <span className="mr-2">•</span> The ticker symbol is incorrect (try .NS suffix).
                        </li>
                        <li className="flex items-start">
                            <span className="mr-2">•</span> Data is temporarily unavailable from the exchange.
                        </li>
                    </ul>
                </p>

                <button
                    onClick={onBack}
                    className="group flex items-center justify-center space-x-2 w-full max-w-xs mx-auto px-6 py-4 rounded-xl font-semibold text-white transition-all transform hover:-translate-y-1 hover:shadow-lg active:translate-y-0 active:scale-95"
                    style={{
                        background: 'linear-gradient(145deg, #6b7280, #4b5563)',
                        boxShadow: '6px 6px 12px #b0b0b0, -6px -6px 12px #ffffff'
                    }}
                >
                    <FiArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span>Return to Search</span>
                </button>
            </div>
        </div>
    )
}
