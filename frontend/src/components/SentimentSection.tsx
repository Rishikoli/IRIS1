import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { FiTrendingUp, FiTrendingDown, FiMinus, FiExternalLink } from 'react-icons/fi';

interface SentimentSectionProps {
    sentimentData: any;
    isLoading?: boolean;
    companySymbol?: string;
}

export default function SentimentSection({ sentimentData, isLoading = false, companySymbol = 'Reliance' }: SentimentSectionProps) {
    const [monitoringData, setMonitoringData] = useState<any>(null);
    const [monitoringLoading, setMonitoringLoading] = useState(false);

    // Fetch real-time monitoring sentiment data
    useEffect(() => {
        const fetchMonitoringSentiment = async () => {
            if (!companySymbol) return;

            setMonitoringLoading(true);
            try {
                const response = await fetch(`/api/v1/sentiment/company/${companySymbol}?hours=24`);
                if (response.ok) {
                    const data = await response.json();
                    setMonitoringData(data);
                } else {
                    setMonitoringData(null);
                }
            } catch (error) {
                console.error('Failed to fetch monitoring sentiment:', error);
                setMonitoringData(null);
            } finally {
                setMonitoringLoading(false);
            }
        };

        fetchMonitoringSentiment();
    }, [companySymbol]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2" style={{ borderColor: '#7B68EE' }}></div>
                <span className="ml-4 text-lg font-medium" style={{ color: '#64748b' }}>Analyzing market sentiment...</span>
            </div>
        );
    }

    if (!sentimentData || sentimentData.error) {
        return (
            <div className="text-center py-12">
                <div className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center" style={{
                    background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)',
                    boxShadow: '0 0 20px rgba(242, 160, 158, 0.3)'
                }}>
                    <span className="text-3xl">📉</span>
                </div>
                <h3 className="text-2xl font-bold mb-2" style={{ color: '#1e293b' }}>No Sentiment Data</h3>
                <p className="text-base" style={{ color: '#64748b' }}>
                    {sentimentData?.error || "Run analysis to view market sentiment"}
                </p>
            </div>
        );
    }

    const { trends, news_sentiment, overall_sentiment } = sentimentData;
    const trendsData = trends?.data || [];
    const headlines = news_sentiment?.headlines || [];
    const sentimentScore = news_sentiment?.sentiment_analysis?.score || 0;
    const sentimentLabel = news_sentiment?.sentiment_analysis?.label || "Neutral";
    const sentimentSummary = news_sentiment?.sentiment_analysis?.summary || "";

    // FinBERT Data
    const finbertData = news_sentiment?.finbert_analysis;
    const finbertScore = finbertData?.score || 0;
    const finbertLabel = finbertData?.label || "Neutral";
    const finbertBreakdown = finbertData?.breakdown || { positive: 0, negative: 0, neutral: 0 };
    const totalFinbert = (finbertBreakdown.positive + finbertBreakdown.negative + finbertBreakdown.neutral) || 1;

    const getSentimentColor = (score: number) => {
        if (score > 20) return '#4ade80'; // Green
        if (score < -20) return '#ef4444'; // Red
        return '#facc15'; // Yellow
    };

    const getTrendingIcon = (trending: string) => {
        if (trending === 'up') return <FiTrendingUp className="text-green-500" />;
        if (trending === 'down') return <FiTrendingDown className="text-red-500" />;
        return <FiMinus className="text-yellow-500" />;
    };

    const getTrendingColor = (trending: string) => {
        if (trending === 'up') return '#4ade80';
        if (trending === 'down') return '#ef4444';
        return '#facc15';
    };

    const sentimentColor = getSentimentColor(sentimentScore);

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Market Sentiment</h2>
                    <p className="text-base font-medium" style={{ color: '#64748b' }}>
                        Real-time analysis of Google Trends and Financial News
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="px-6 py-3 rounded-xl flex items-center gap-3" style={{
                        background: 'rgba(255, 255, 255, 0.9)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.1), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: `2px solid ${sentimentColor}20`
                    }}>
                        <span className="text-sm font-bold" style={{ color: '#64748b' }}>VERDICT:</span>
                        <span className="text-lg font-bold" style={{ color: sentimentColor }}>
                            {overall_sentiment.toUpperCase()}
                        </span>
                    </div>
                </div>
            </div>

            {/* Real-Time Monitoring Section (NEW!) */}
            {monitoringData && (
                <div className="neumorphic-card rounded-3xl p-8 border-4 border-purple-200" style={{
                    background: 'linear-gradient(135deg, rgba(251, 243, 255, 0.95) 0%, rgba(243, 232, 255, 0.95) 100%)',
                    backdropFilter: 'blur(15px)',
                    boxShadow: '0 0 40px rgba(167, 139, 250, 0.3), 16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)'
                }}>
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{
                                background: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)',
                                boxShadow: '0 4px 12px rgba(167, 139, 250, 0.4)'
                            }}>
                                <span className="text-2xl">🚀</span>
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold" style={{ color: '#5b21b6' }}>Real-Time News Monitoring</h3>
                                <p className="text-sm font-medium" style={{ color: '#7c3aed' }}>
                                    Live sentiment from {monitoringData.total_articles} articles (Last 24 hours)
                                </p>
                            </div>
                        </div>
                        <div className="px-4 py-2 rounded-xl flex items-center gap-2" style={{
                            background: getTrendingColor(monitoringData.trending),
                            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                        }}>
                            {getTrendingIcon(monitoringData.trending)}
                            <span className="text-sm font-bold text-white">
                                {monitoringData.trending.toUpperCase()}
                            </span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {/* Positive */}
                        <div className="bg-white/90 backdrop-blur rounded-2xl p-4 text-center" style={{
                            boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                        }}>
                            <div className="text-3xl font-bold mb-1 text-green-500">
                                {monitoringData.sentiment_breakdown.positive}
                            </div>
                            <div className="text-xs font-semibold text-gray-600">Positive</div>
                            <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-green-400 transition-all duration-1000"
                                    style={{ width: `${(monitoringData.sentiment_breakdown.positive / monitoringData.total_articles * 100)}%` }}
                                ></div>
                            </div>
                        </div>

                        {/* Negative */}
                        <div className="bg-white/90 backdrop-blur rounded-2xl p-4 text-center" style={{
                            boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                        }}>
                            <div className="text-3xl font-bold mb-1 text-red-500">
                                {monitoringData.sentiment_breakdown.negative}
                            </div>
                            <div className="text-xs font-semibold text-gray-600">Negative</div>
                            <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-red-400 transition-all duration-1000"
                                    style={{ width: `${(monitoringData.sentiment_breakdown.negative / monitoringData.total_articles * 100)}%` }}
                                ></div>
                            </div>
                        </div>

                        {/* Neutral */}
                        <div className="bg-white/90 backdrop-blur rounded-2xl p-4 text-center" style={{
                            boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                        }}>
                            <div className="text-3xl font-bold mb-1 text-yellow-500">
                                {monitoringData.sentiment_breakdown.neutral}
                            </div>
                            <div className="text-xs font-semibold text-gray-600">Neutral</div>
                            <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-yellow-400 transition-all duration-1000"
                                    style={{ width: `${(monitoringData.sentiment_breakdown.neutral / monitoringData.total_articles * 100)}%` }}
                                ></div>
                            </div>
                        </div>

                        {/* Confidence */}
                        <div className="bg-white/90 backdrop-blur rounded-2xl p-4 text-center" style={{
                            boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                        }}>
                            <div className="text-3xl font-bold mb-1 text-purple-500">
                                {(monitoringData.avg_confidence * 100).toFixed(0)}%
                            </div>
                            <div className="text-xs font-semibold text-gray-600">Confidence</div>
                            <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-purple-400 transition-all duration-1000"
                                    style={{ width: `${(monitoringData.avg_confidence * 100)}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-4 text-center text-sm font-medium" style={{ color: '#6d28d9' }}>
                        Powered by FinBERT • 200+ articles/cycle from 7 sources
                    </div>
                </div>
            )}

            {/* Top Row: Trends Chart & Sentiment Scores */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Google Trends Chart */}
                <div className="lg:col-span-2 neumorphic-card rounded-3xl p-8" style={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(15px)',
                    boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)'
                }}>
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2" style={{ color: '#1e293b' }}>
                        <span>📈</span> Google Search Interest (Last 30 Days)
                    </h3>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trendsData}>
                                <defs>
                                    <linearGradient id="colorInterest" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#7B68EE" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#7B68EE" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis
                                    dataKey="date"
                                    tick={{ fill: '#64748b', fontSize: 12 }}
                                    axisLine={false}
                                    tickLine={false}
                                    minTickGap={30}
                                />
                                <YAxis
                                    tick={{ fill: '#64748b', fontSize: 12 }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                                        borderRadius: '12px',
                                        border: 'none',
                                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="interest"
                                    stroke="#7B68EE"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorInterest)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Sentiment Score Card */}
                <div className="neumorphic-card rounded-3xl p-8 flex flex-col justify-center items-center text-center" style={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(15px)',
                    boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)'
                }}>
                    <h3 className="text-xl font-bold mb-6" style={{ color: '#1e293b' }}>News Sentiment Score</h3>

                    <div className="relative w-48 h-48 flex items-center justify-center mb-6">
                        {/* Circular Progress Background */}
                        <svg className="w-full h-full transform -rotate-90">
                            <circle
                                cx="96"
                                cy="96"
                                r="88"
                                stroke="#e2e8f0"
                                strokeWidth="12"
                                fill="none"
                            />
                            <circle
                                cx="96"
                                cy="96"
                                r="88"
                                stroke={sentimentColor}
                                strokeWidth="12"
                                fill="none"
                                strokeDasharray={2 * Math.PI * 88}
                                strokeDashoffset={2 * Math.PI * 88 * (1 - (sentimentScore + 100) / 200)} // Normalize -100 to 100 range
                                strokeLinecap="round"
                                className="transition-all duration-1000 ease-out"
                            />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-4xl font-bold" style={{ color: sentimentColor }}>
                                {sentimentScore}
                            </span>
                            <span className="text-sm font-medium text-gray-500">/ 100</span>
                        </div>
                    </div>

                    <div className="text-lg font-semibold mb-2" style={{ color: sentimentColor }}>
                        {sentimentLabel}
                    </div>
                    <p className="text-sm text-gray-500 leading-relaxed">
                        {sentimentSummary}
                    </p>
                </div>

                {/* FinBERT Sentiment Card */}
                <div className="neumorphic-card rounded-3xl p-8 flex flex-col justify-center items-center text-center" style={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(15px)',
                    boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)'
                }}>
                    <h3 className="text-xl font-bold mb-6" style={{ color: '#1e293b' }}>FinBERT Analysis</h3>

                    <div className="relative w-32 h-32 flex items-center justify-center mb-4">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle
                                cx="64"
                                cy="64"
                                r="56"
                                stroke="#e2e8f0"
                                strokeWidth="8"
                                fill="none"
                            />
                            <circle
                                cx="64"
                                cy="64"
                                r="56"
                                stroke={getSentimentColor(finbertScore)}
                                strokeWidth="8"
                                fill="none"
                                strokeDasharray={2 * Math.PI * 56}
                                strokeDashoffset={2 * Math.PI * 56 * (1 - (finbertScore + 100) / 200)}
                                strokeLinecap="round"
                                className="transition-all duration-1000 ease-out"
                            />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-2xl font-bold" style={{ color: getSentimentColor(finbertScore) }}>
                                {finbertScore}
                            </span>
                        </div>
                    </div>

                    <div className="text-lg font-semibold mb-4" style={{ color: getSentimentColor(finbertScore) }}>
                        {finbertLabel}
                    </div>

                    {/* Breakdown Bars */}
                    <div className="w-full space-y-2">
                        <div className="flex items-center text-xs">
                            <span className="w-16 text-left font-medium text-green-600">Positive</span>
                            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden mx-2">
                                <div className="h-full bg-green-400" style={{ width: `${(finbertBreakdown.positive / totalFinbert) * 100}%` }}></div>
                            </div>
                            <span className="w-6 text-right text-gray-500">{finbertBreakdown.positive}</span>
                        </div>
                        <div className="flex items-center text-xs">
                            <span className="w-16 text-left font-medium text-gray-500">Neutral</span>
                            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden mx-2">
                                <div className="h-full bg-gray-400" style={{ width: `${(finbertBreakdown.neutral / totalFinbert) * 100}%` }}></div>
                            </div>
                            <span className="w-6 text-right text-gray-500">{finbertBreakdown.neutral}</span>
                        </div>
                        <div className="flex items-center text-xs">
                            <span className="w-16 text-left font-medium text-red-600">Negative</span>
                            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden mx-2">
                                <div className="h-full bg-red-400" style={{ width: `${(finbertBreakdown.negative / totalFinbert) * 100}%` }}></div>
                            </div>
                            <span className="w-6 text-right text-gray-500">{finbertBreakdown.negative}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* News Headlines */}
            <div className="neumorphic-card rounded-3xl p-8" style={{
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(15px)',
                boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)'
            }}>
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2" style={{ color: '#1e293b' }}>
                    <span>📰</span> Latest Financial News
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {headlines.map((item: any, index: number) => (
                        <a
                            key={index}
                            href={item.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="group p-4 rounded-xl transition-all duration-300 hover:scale-[1.02]"
                            style={{
                                background: 'rgba(255, 255, 255, 0.6)',
                                border: '1px solid rgba(226, 232, 240, 0.8)'
                            }}
                        >
                            <div className="flex justify-between items-start gap-4">
                                <div>
                                    <h4 className="font-semibold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
                                        {item.title}
                                    </h4>
                                    <p className="text-xs text-gray-500">
                                        {new Date(item.pubDate).toLocaleDateString(undefined, {
                                            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                                        })}
                                    </p>
                                </div>
                                <FiExternalLink className="text-gray-400 group-hover:text-blue-500 flex-shrink-0" />
                            </div>
                        </a>
                    ))}
                </div>
            </div>
        </div>
    );
}
