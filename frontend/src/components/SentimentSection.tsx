import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { FiTrendingUp, FiTrendingDown, FiMinus, FiExternalLink } from 'react-icons/fi';

interface SentimentSectionProps {
    sentimentData: any;
    isLoading?: boolean;
}

export default function SentimentSection({ sentimentData, isLoading = false }: SentimentSectionProps) {
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

    const getSentimentColor = (score: number) => {
        if (score > 20) return '#4ade80'; // Green
        if (score < -20) return '#ef4444'; // Red
        return '#facc15'; // Yellow
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

            {/* Top Row: Trends Chart & Sentiment Score */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
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
