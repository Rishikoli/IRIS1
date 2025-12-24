import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

import SentimentSection from './SentimentSection';

// Dynamically import D3 components to avoid SSR issues
const FinancialRatiosChart = dynamic(() => import('@/components/charts/FinancialRatiosChart'), { ssr: false });
const VerticalAnalysisChart = dynamic(() => import('@/components/charts/VerticalAnalysisChart'), { ssr: false });
const HorizontalAnalysisChart = dynamic(() => import('@/components/charts/HorizontalAnalysisChart'), { ssr: false });

const BenfordChart = dynamic(() => import('@/components/charts/BenfordChart'), { ssr: false });
const ZScoreChart = dynamic(() => import('@/components/charts/ZScoreChart'), { ssr: false });
const MScoreChart = dynamic(() => import('@/components/charts/MScoreChart'), { ssr: false });



import NetworkGraph from './NetworkGraph';
import axios from 'axios';

interface ForensicSectionProps {
  analysisData: any;
  isLoading?: boolean;
  sentimentData?: any;
  isSentimentLoading?: boolean;
}

export default function ForensicSection({ analysisData, isLoading = false, sentimentData, isSentimentLoading = false }: ForensicSectionProps) {
  const [activeSubTab, setActiveSubTab] = useState('network');


  const [networkData, setNetworkData] = useState<any>(null);
  const [isNetworkLoading, setIsNetworkLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Reset network data when company changes
  useEffect(() => {
    setNetworkData(null);
  }, [analysisData?.company_id]);

  const handleExport = async (format: 'pdf' | 'excel') => {
    if (!analysisData?.company_id) return;

    setIsExporting(true);
    try {
      // 1. Generate Report
      const response = await axios.post('/api/reports/generate', {
        company_symbol: analysisData.company_id,
        export_formats: [format],
        include_summary: true
      });

      if (response.data.success && response.data.exports && response.data.exports[format]) {
        const exportInfo = response.data.exports[format].export_info;
        const downloadUrl = exportInfo.download_url;

        // 2. Trigger Download
        // Use the backend URL directly if it's a full URL, or append to base
        // The backend returns /api/reports/download/{filename}
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', exportInfo.filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } else {
        console.error('Export failed:', response.data);
        alert('Failed to generate report. Please try again.');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('An error occurred while exporting the report.');
    } finally {
      setIsExporting(false);
    }
  };

  useEffect(() => {
    if (!networkData && analysisData?.company_id) {
      const fetchNetworkData = async () => {
        setIsNetworkLoading(true);
        try {
          // Create a timeout promise
          const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Request timed out')), 60000)
          );

          // Race the API call against the timeout
          const response = await Promise.race([
            axios.get(`/api/forensic/network/${analysisData.company_id}`),
            timeoutPromise
          ]) as any;

          console.log('Network Data Response:', response.data);
          if (response.data.success) {
            setNetworkData(response.data);
          }
        } catch (error) {
          console.error('Failed to fetch network data:', error);
          // Set empty state on error instead of misleading fallback
          setNetworkData({
            gemini_data: {
              subsidiaries: [],
              transactions: []
            },
            predictive_forensics: {
              historical_revenue: [],
              revenue_forecast: [],
              trend: 'Unknown',
              future_risk_score: 0
            },
            graph_data: {
              nodes: [
                { id: analysisData.company_id, type: 'custom', data: { label: analysisData.company_id, type: 'company', risk_score: 0 }, position: { x: 500, y: 400 } }
              ],
              edges: []
            }
          });
        } finally {
          setIsNetworkLoading(false);
        }
      };
      fetchNetworkData();
    }
  }, [networkData, analysisData?.company_id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
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

  const RiskExplainabilityChart = dynamic(() => import('@/components/charts/RiskExplainabilityChart'), { ssr: false });

  const subTabs = [
    { id: 'network', label: 'RPT Network', icon: '🕸️' },
    { id: 'risk_explainability', label: 'Risk Explainability', icon: '📉' },
    { id: 'sentiment', label: 'Market Sentiment', icon: '📈' },

    { id: 'ratios', label: 'Financial Ratios', icon: '🔢' },
    { id: 'benford', label: 'Benford\'s Law', icon: '📊' },
    { id: 'zscore', label: 'Altman Z-Score', icon: '⚖️' },
    { id: 'mscore', label: 'Beneish M-Score', icon: '🔍' }
  ];

  const renderContent = () => {
    switch (activeSubTab) {
      case 'network':
        return <NetworkGraph data={networkData?.graph_data} cycles={networkData?.cycles} isLoading={isNetworkLoading} />;
      case 'risk_explainability':
        return (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-800">Risk Factor Impact Analysis</h3>
            <p className="text-slate-600">SHAP (SHapley Additive exPlanations) values showing how each factor contributes to the overall risk score.</p>
            {analysisData?.risk_assessment?.shap_values ? (
              <RiskExplainabilityChart shapValues={analysisData.risk_assessment.shap_values} />
            ) : (
              <div className="p-8 text-center text-slate-500 bg-slate-100 rounded-xl">
                Risk explainability data not available for this company.
              </div>
            )}
          </div>
        );
      case 'sentiment':
        return <SentimentSection sentimentData={sentimentData} isLoading={isSentimentLoading} />;
      case 'vertical':
        return <VerticalAnalysisChart data={analysisData.vertical_analysis} />;
      case 'horizontal':
        return <HorizontalAnalysisChart data={analysisData.horizontal_analysis} />;
      case 'ratios':
        return <FinancialRatiosChart data={analysisData.financial_ratios} />;

      case 'benford':
        return <BenfordChart data={analysisData.benford_analysis} />;
      case 'zscore':
        return <ZScoreChart data={analysisData.altman_z_score} />;
      case 'mscore':
        return <MScoreChart data={analysisData.beneish_m_score} />;
      default:
        return <NetworkGraph data={networkData?.graph_data} cycles={networkData?.cycles} isLoading={isNetworkLoading} />;
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


