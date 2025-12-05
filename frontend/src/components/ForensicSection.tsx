import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

import SentimentSection from './SentimentSection';

// Dynamically import D3 components to avoid SSR issues
const FinancialRatiosChart = dynamic(() => import('@/components/charts/FinancialRatiosChart'), { ssr: false });
const VerticalAnalysisChart = dynamic(() => import('@/components/charts/VerticalAnalysisChart'), { ssr: false });
const HorizontalAnalysisChart = dynamic(() => import('@/components/charts/HorizontalAnalysisChart'), { ssr: false });
const AnomalyDetectionChart = dynamic(() => import('@/components/charts/AnomalyDetectionChart'), { ssr: false });
const BenfordChart = dynamic(() => import('@/components/charts/BenfordChart'), { ssr: false });
const ZScoreChart = dynamic(() => import('@/components/charts/ZScoreChart'), { ssr: false });
const MScoreChart = dynamic(() => import('@/components/charts/MScoreChart'), { ssr: false });

interface ForensicSectionProps {
  analysisData: any;
  isLoading?: boolean;
  sentimentData?: any;
  isSentimentLoading?: boolean;
}

export default function ForensicSection({ analysisData, isLoading = false, sentimentData, isSentimentLoading = false }: ForensicSectionProps) {
  const [activeSubTab, setActiveSubTab] = useState('overview');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2" style={{ borderColor: '#7B68EE' }}></div>
        <span className="ml-4 text-lg font-medium" style={{ color: '#64748b' }}>Loading forensic analysis...</span>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center" style={{
          background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)',
          boxShadow: '0 0 20px rgba(242, 160, 158, 0.3)'
        }}>
          <span className="text-3xl">🔍</span>
        </div>
        <h3 className="text-2xl font-bold mb-2" style={{ color: '#1e293b' }}>Forensic Analysis</h3>
        <p className="text-base" style={{ color: '#64748b' }}>Run analysis to view comprehensive forensic metrics</p>
      </div>
    );
  }

  const subTabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'sentiment', label: 'Market Sentiment', icon: '📈' },
    { id: 'ratios', label: 'Financial Ratios', icon: '📈' },
    { id: 'vertical', label: 'Vertical Analysis', icon: '📊' },
    { id: 'horizontal', label: 'Horizontal Analysis', icon: '📈' },
    { id: 'anomalies', label: 'Anomaly Detection', icon: '🚨' },
    { id: 'benford', label: 'Benford\'s Law', icon: '📊' },
    { id: 'zscore', label: 'Altman Z-Score', icon: '⚖️' },
    { id: 'mscore', label: 'Beneish M-Score', icon: '🔍' }
  ];

  const renderContent = () => {
    switch (activeSubTab) {
      case 'overview':
        return <ForensicOverview analysisData={analysisData} />;
      case 'sentiment':
        return <SentimentSection sentimentData={sentimentData} isLoading={isSentimentLoading} />;
      case 'ratios':
        return <FinancialRatiosChart data={analysisData.financial_ratios} />;
      case 'vertical':
        return <VerticalAnalysisChart data={analysisData.vertical_analysis} />;
      case 'horizontal':
        return <HorizontalAnalysisChart data={analysisData.horizontal_analysis} />;
      case 'anomalies':
        return <AnomalyDetectionChart data={analysisData.anomaly_detection} />;
      case 'benford':
        return <BenfordChart data={analysisData.benford_analysis} />;
      case 'zscore':
        return <ZScoreChart data={analysisData.altman_z_score} />;
      case 'mscore':
        return <MScoreChart data={analysisData.beneish_m_score} />;
      default:
        return <ForensicOverview analysisData={analysisData} />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Forensic Section Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Forensic Analysis</h2>
          <p className="text-base font-medium" style={{ color: '#64748b' }}>
            Comprehensive financial statement analysis with 29 forensic metrics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl" style={{
            background: 'rgba(255, 255, 255, 0.9)',
            boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.1), inset -4px -4px 8px rgba(255,255,255,0.9)'
          }}>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-sm font-semibold" style={{ color: '#1e293b' }}>29 Metrics Analyzed</span>
          </div>
        </div>
      </div>

      {/* Sub-navigation Tabs */}
      <div className="flex flex-wrap gap-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl font-semibold transition-all neumorphic-button ${activeSubTab === tab.id ? 'active-tab' : ''
              }`}
            style={
              activeSubTab === tab.id
                ? {
                  background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)',
                  boxShadow: '6px 6px 12px rgba(123, 104, 238, 0.3), -6px -6px 12px rgba(255, 255, 255, 0.8)',
                  color: '#fff'
                }
                : {
                  background: 'rgba(255, 255, 255, 0.9)',
                  boxShadow: '6px 6px 12px rgba(0,0,0,0.1), -6px -6px 12px rgba(255,255,255,0.9)',
                  color: '#64748b'
                }
            }
          >
            <span className="text-lg">{tab.icon}</span>
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="neumorphic-card rounded-3xl p-8" style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(15px)',
        boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)'
      }}>
        {renderContent()}
      </div>

      <style jsx>{`
        .active-tab {
          transform: translateY(-2px) !important;
        }

        .neumorphic-button {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .neumorphic-button:hover {
          transform: translateY(-2px);
          box-shadow: 6px 6px 12px rgba(0,0,0,0.15), -6px -6px 12px rgba(255,255,255,0.9);
        }
      `}</style>
    </div>
  );
}

// Forensic Overview Component
function ForensicOverview({ analysisData }: { analysisData: any }) {
  const metrics = [
    {
      name: 'Altman Z-Score',
      value: analysisData.altman_z_score?.altman_z_score?.z_score || 'N/A',
      status: analysisData.altman_z_score?.altman_z_score?.classification || 'Unknown',
      color: analysisData.altman_z_score?.altman_z_score?.risk_level === 'LOW' ? '#4ade80' : '#FF6B9D',
      icon: '⚖️'
    },
    {
      name: 'Beneish M-Score',
      value: analysisData.beneish_m_score?.beneish_m_score?.m_score || 'N/A',
      status: analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? 'Risk' : 'Safe',
      color: analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? '#FF6B9D' : '#4ade80',
      icon: '🔍'
    },
    {
      name: 'Anomalies Detected',
      value: analysisData.anomaly_detection?.anomalies_detected || '0',
      status: 'Detected',
      color: '#7B68EE',
      icon: '🚨'
    },
    {
      name: 'Benford Score',
      value: `${analysisData.benford_analysis?.overall_score || 'N/A'}%`,
      status: 'Compliance',
      color: '#f2a09e',
      icon: '📊'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className="neumorphic-card rounded-2xl p-6 group"
            style={{
              background: 'rgba(255, 255, 255, 0.8)',
              boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)',
              border: `2px solid ${metric.color}20`
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                  style={{
                    background: `linear-gradient(135deg, ${metric.color}, ${metric.color}dd)`,
                    boxShadow: `0 0 15px ${metric.color}30`
                  }}
                >
                  {metric.icon}
                </div>
                <div>
                  <p className="text-sm font-medium" style={{ color: '#64748b' }}>{metric.name}</p>
                  <p className="text-2xl font-bold" style={{ color: '#1e293b' }}>{metric.value}</p>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs px-3 py-1 rounded-full font-medium" style={{
                background: `${metric.color}15`,
                color: metric.color,
                border: `1px solid ${metric.color}30`
              }}>
                {metric.status}
              </span>
              <div className="w-16 h-1 rounded-full" style={{ background: `${metric.color}20` }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: metric.name.includes('Anomalies') ? '30%' : '75%',
                    background: `linear-gradient(90deg, ${metric.color}, ${metric.color}aa)`
                  }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Analysis Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Analysis Summary */}
        <div className="space-y-6">
          <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Analysis Summary</h3>

          <div className="space-y-4">
            <div className="p-6 rounded-2xl" style={{
              background: 'rgba(255, 255, 255, 0.7)',
              boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.05), inset -6px -6px 12px rgba(255,255,255,0.9)'
            }}>
              <h4 className="font-semibold mb-3" style={{ color: '#1e293b' }}>📊 Financial Ratios</h4>
              {(() => {
                const ratios = analysisData.financial_ratios?.financial_ratios || {};
                const periods = Object.keys(ratios).sort().reverse();
                const latestPeriod = periods[0];
                const latestRatios = latestPeriod ? ratios[latestPeriod] : {};

                return (
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Gross Margin:</span>
                      <span className="font-semibold ml-2" style={{ color: '#1e293b' }}>
                        {latestRatios.gross_margin_pct || 'N/A'}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Net Margin:</span>
                      <span className="font-semibold ml-2" style={{ color: '#1e293b' }}>
                        {latestRatios.net_margin_pct || 'N/A'}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">ROE:</span>
                      <span className="font-semibold ml-2" style={{ color: '#1e293b' }}>
                        {latestRatios.roe || 'N/A'}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">ROA:</span>
                      <span className="font-semibold ml-2" style={{ color: '#1e293b' }}>
                        {latestRatios.roa || 'N/A'}%
                      </span>
                    </div>
                  </div>
                );
              })()}
            </div>

            <div className="p-6 rounded-2xl" style={{
              background: 'rgba(255, 255, 255, 0.7)',
              boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.05), inset -6px -6px 12px rgba(255,255,255,0.9)'
            }}>
              <h4 className="font-semibold mb-3" style={{ color: '#1e293b' }}>⚖️ Risk Indicators</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Bankruptcy Risk:</span>
                  <span className={`font-semibold ${analysisData.altman_z_score?.altman_z_score?.risk_level === 'LOW' ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisData.altman_z_score?.altman_z_score?.classification || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Manipulation Risk:</span>
                  <span className={`font-semibold ${!analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? 'text-green-600' : 'text-red-600'}`}>
                    {!analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? 'Low' : 'High'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Anomalies:</span>
                  <span className={`font-semibold ${analysisData.anomaly_detection?.anomalies_detected === 0 ? 'text-green-600' : 'text-yellow-600'}`}>
                    {analysisData.anomaly_detection?.anomalies_detected || 0} detected
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Quick Insights */}
        <div className="space-y-6">
          <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Quick Insights</h3>

          <div className="space-y-4">
            <div className="p-6 rounded-2xl" style={{
              background: 'rgba(255, 255, 255, 0.7)',
              boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.05), inset -6px -6px 12px rgba(255,255,255,0.9)',
              border: '2px solid rgba(123, 104, 238, 0.2)'
            }}>
              <h4 className="font-semibold mb-3 flex items-center gap-2" style={{ color: '#1e293b' }}>
                <span>🎯</span> Key Findings
              </h4>
              <ul className="space-y-2 text-sm" style={{ color: '#64748b' }}>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-1">•</span>
                  Comprehensive analysis of 29 financial metrics completed
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  Real-time data integration from multiple sources
                </li>
                <li className="flex items-start gap-2">
                  <span className={`mt-1 ${analysisData.anomaly_detection?.anomalies_detected === 0 ? 'text-green-500' : 'text-yellow-500'}`}>•</span>
                  {analysisData.anomaly_detection?.anomalies_detected === 0 ? 'No significant anomalies detected' : `${analysisData.anomaly_detection?.anomalies_detected} anomalies require attention`}
                </li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl" style={{
              background: 'rgba(255, 255, 255, 0.7)',
              boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.05), inset -6px -6px 12px rgba(255,255,255,0.9)',
              border: '2px solid rgba(255, 107, 157, 0.2)'
            }}>
              <h4 className="font-semibold mb-3 flex items-center gap-2" style={{ color: '#1e293b' }}>
                <span>📋</span> Recommendations
              </h4>
              <ul className="space-y-2 text-sm" style={{ color: '#64748b' }}>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  Review detailed ratio analysis for trend identification
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-500 mt-1">•</span>
                  Monitor anomaly detection results regularly
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-1">•</span>
                  Compare with industry benchmarks for context
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
