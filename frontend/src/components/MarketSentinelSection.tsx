import React, { useState, useEffect } from 'react';
import { FiAlertTriangle, FiActivity, FiTrendingUp, FiTrendingDown, FiShield, FiDollarSign } from 'react-icons/fi';
import axios from 'axios';

interface MarketSentinelSectionProps {
    companySymbol: string;
}

export default function MarketSentinelSection({ companySymbol }: MarketSentinelSectionProps) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!companySymbol) return;

        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await axios.post('/api/v1/sentiment/technical/analyze', {
                    company_symbol: companySymbol
                });

                if (response.data.success) {
                    setData(response.data.data);
                } else {
                    setError(response.data.error || 'Failed to fetch technical analysis');
                }
            } catch (err: any) {
                console.error('Technical analysis error:', err);
                setError(err.message || 'An error occurred while analyzing market technicals');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [companySymbol]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mb-4"></div>
                <p className="text-slate-600 font-medium">Analyzing market technicals (Agent 8 Sentinel)...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-8 text-center bg-red-50 rounded-2xl border border-red-100">
                <FiAlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-bold text-red-800 mb-2">Analysis Failed</h3>
                <p className="text-red-600">{error}</p>
            </div>
        );
    }

    if (!data) {
        return null;
    }

    // Extract nested objects
    const analysis = data.analysis || {};
    const indicators = data.indicators || {};
    const riskLevel = analysis.risk_level || 'UNKNOWN';
    const riskScore = analysis.risk_score || 0;

    const riskColor =
        riskLevel.includes('HIGH') || riskLevel.includes('CRITICAL') ? 'text-red-600' :
            riskLevel === 'MEDIUM' ? 'text-yellow-600' :
                'text-green-600';

    const riskBg =
        riskLevel.includes('HIGH') || riskLevel.includes('CRITICAL') ? 'bg-red-100' :
            riskLevel === 'MEDIUM' ? 'bg-yellow-100' :
                'bg-green-100';

    return (
        <div className="space-y-8">
            {/* Header & Risk Score */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                        <FiActivity className="text-purple-600" />
                        Market Sentinel
                        <span className="text-sm font-normal text-slate-500 bg-slate-100 px-2 py-1 rounded-md">Agent 8</span>
                    </h2>
                    <p className="text-slate-500 mt-1">
                        Real-time Pump & Dump detection and price/volume anomaly analysis
                    </p>
                </div>

                <div className={`px-8 py-4 rounded-2xl flex flex-col items-center border ${riskBg} ${riskColor.replace('text-', 'border-')}`}>
                    <div className="flex items-center gap-2 mb-1">
                        <FiShield className="w-5 h-5" />
                        <span className="font-bold tracking-wider">RISK LEVEL</span>
                    </div>
                    <span className="text-3xl font-extrabold">{riskLevel}</span>
                    <span className="text-sm font-semibold opacity-80">Score: {riskScore}/100</span>
                </div>
            </div>

            {/* Signals Grid */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Signals List */}
                <div className="neumorphic-card rounded-2xl p-6 bg-white/50 border border-slate-200/50 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
                        <FiAlertTriangle className="text-orange-500" />
                        Detected Signals
                    </h3>

                    {analysis.signals && analysis.signals.length > 0 ? (
                        <div className="space-y-3">
                            {analysis.signals.map((signal: string, idx: number) => (
                                <div key={idx} className="flex items-start gap-3 p-3 bg-red-50 rounded-lg border border-red-100">
                                    <div className="mt-1 min-w-[6px] h-6 rounded-full bg-red-500"></div>
                                    <span className="text-red-800 font-medium">{signal}</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="p-6 text-center text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                            No anomaly signals detected. Market patterns appear normal.
                        </div>
                    )}
                </div>

                {/* Technical Indicators */}
                <div className="neumorphic-card rounded-2xl p-6 bg-white/50 border border-slate-200/50 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
                        <FiTrendingUp className="text-blue-500" />
                        Key Indicators
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                        <IndicatorCard
                            label="Current Price"
                            value={data.current_price}
                            prefix="$"
                            icon={<FiDollarSign className="text-green-500" />}
                        />
                        <IndicatorCard
                            label="RSI (14)"
                            value={indicators.rsi_14}
                            suffix=""
                            status={indicators.rsi_14 > 70 ? 'danger' : indicators.rsi_14 < 30 ? 'warning' : 'neutral'}
                        />
                        <IndicatorCard
                            label="Volume Spike"
                            value={analysis.vol_spike_ratio}
                            suffix="x"
                            status={analysis.vol_spike_ratio > 2 ? 'danger' : 'neutral'}
                        />
                        <IndicatorCard
                            label="SMA (20)"
                            value={indicators.sma_20}
                            prefix="$"
                        />
                    </div>
                </div>
            </div>

            {/* Price Action Description */}
            <div className="neumorphic-card rounded-2xl p-6 bg-white/50 border border-slate-200/50 shadow-sm">
                <h3 className="text-lg font-bold text-slate-700 mb-4">Market Context</h3>
                <div className="grid md:grid-cols-3 gap-6 text-sm">
                    <div className="p-3 bg-slate-50 rounded-lg">
                        <span className="block text-slate-500 mb-1">50-Day SMA</span>
                        <span className="text-lg font-mono font-bold text-slate-700">
                            ${formatNumber(indicators.sma_50)}
                        </span>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg">
                        <span className="block text-slate-500 mb-1">EMA (12)</span>
                        <span className="text-lg font-mono font-bold text-slate-700">
                            ${formatNumber(indicators.ema_12)}
                        </span>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg">
                        <span className="block text-slate-500 mb-1">Volume (20D Avg)</span>
                        <span className="text-lg font-mono font-bold text-slate-700">
                            {formatNumber(indicators.avg_volume_20)}
                        </span>
                    </div>
                </div>
            </div>

        </div>
    );
}

function IndicatorCard({ label, value, prefix = '', suffix = '', status = 'neutral', icon, isPercent = false }: any) {
    const statusColor =
        status === 'danger' ? 'bg-red-50 border-red-100 text-red-700' :
            status === 'warning' ? 'bg-yellow-50 border-yellow-100 text-yellow-700' :
                'bg-slate-50 border-slate-100 text-slate-700';

    const displayValue = isPercent && value ? `${((value - 1) * 100).toFixed(2)}` : formatNumber(value);

    return (
        <div className={`p-4 rounded-xl border ${statusColor} transition-all`}>
            <div className="text-xs font-semibold uppercase opacity-70 mb-1 flex justify-between">
                {label}
                {icon}
            </div>
            <div className="text-xl font-bold">
                {prefix}{displayValue}{suffix}
            </div>
        </div>
    );
}

function formatNumber(num: any) {
    if (num === undefined || num === null) return '-';
    // If it's a number
    const n = Number(num);
    if (isNaN(n)) return num;
    return n.toLocaleString('en-US', { maximumFractionDigits: 2 });
}
