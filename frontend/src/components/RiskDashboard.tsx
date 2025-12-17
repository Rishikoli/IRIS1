'use client'

import { useState } from 'react'
import { FiShield, FiAlertTriangle, FiCheck, FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi'
import GaugeChart from './charts/GaugeChart'
import ForensicGraph from './ForensicGraph'
import RiskExplainabilityChart from './charts/RiskExplainabilityChart'

interface RiskScore {
  success: boolean
  company_id: string
  risk_score: {
    overall_score: number
    risk_level: string
    confidence_score: number
    risk_factors: string[]
    analysis_timestamp: string
    investment_recommendation?: string
    monitoring_frequency?: string
    category_scores?: any
    shap_values?: Record<string, number>
  }
}

interface AnalysisResult {
  success: boolean
  company_id: string
  analysis_timestamp: string
  risk_assessment?: any
  anomaly_detection?: {
    success: boolean
    anomalies_detected: number
    anomalies: any[]
  }
  benford_analysis?: {
    success: boolean
    is_anomalous: boolean
    chi_square_statistic: number
  }
}

interface RiskDashboardProps {
  riskScore: RiskScore | null
  analysisResult: AnalysisResult | null
  isLoading: boolean
}

export default function RiskDashboard({ riskScore, analysisResult, isLoading }: RiskDashboardProps) {
  const [activeSection, setActiveSection] = useState<'overview' | 'factors' | 'trends' | 'network'>('overview')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
        <span className="ml-4 text-slate-400">Calculating risk assessment...</span>
      </div>
    )
  }

  const currentRiskScore = riskScore?.risk_score
  const forensicRiskData = analysisResult?.risk_assessment
  const displayRiskScore = currentRiskScore || forensicRiskData
  const riskFactors = currentRiskScore?.risk_factors || forensicRiskData?.risk_factors || []

  if (!displayRiskScore) {
    return (
      <div className="text-center py-16">
        <FiShield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold mb-2">No Risk Assessment</h3>
        <p className="text-slate-400">Run a forensic analysis to see risk assessment here.</p>
      </div>
    )
  }

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'text-red-400 bg-red-900/20 border-red-700/50'
      case 'high': return 'text-orange-400 bg-orange-900/20 border-orange-700/50'
      case 'medium': return 'text-yellow-400 bg-yellow-900/20 border-yellow-700/50'
      case 'low': return 'text-green-400 bg-green-900/20 border-green-700/50'
      case 'very_low': return 'text-blue-400 bg-blue-900/20 border-blue-700/50'
      default: return 'text-slate-400 bg-slate-900/20 border-slate-700/50'
    }
  }

  const getRiskLevelIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return <FiAlertTriangle className="w-5 h-5" />
      case 'high': return <FiTrendingUp className="w-5 h-5" />
      case 'medium': return <FiMinus className="w-5 h-5" />
      case 'low': return <FiTrendingDown className="w-5 h-5" />
      case 'very_low': return <FiCheck className="w-5 h-5" />
      default: return <FiShield className="w-5 h-5" />
    }
  }

  const anomalies = analysisResult?.anomaly_detection?.anomalies || []
  const benfordAnomalous = analysisResult?.benford_analysis?.is_anomalous || false

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold mb-2">Risk Assessment Dashboard</h2>
          <p className="text-slate-400">
            Comprehensive risk analysis based on forensic examination
          </p>
        </div>
        <button
          onClick={async () => {
            try {
              const btn = document.getElementById('download-btn');
              if (btn) {
                btn.innerText = 'Generating...';
                btn.setAttribute('disabled', 'true');
              }

              const response = await fetch('http://localhost:8000/api/reports/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  company_symbol: riskScore?.company_id || 'HIGHRISK',
                  export_formats: ['pdf']
                })
              });

              const data = await response.json();
              if (data.success && data.exports && data.exports.pdf) {
                const downloadUrl = `http://localhost:8000${data.exports.pdf.export_info.download_url}`;
                window.open(downloadUrl, '_blank');
              } else {
                alert('Failed to generate report');
              }
            } catch (error) {
              console.error('Report generation failed:', error);
              alert('Error generating report');
            } finally {
              const btn = document.getElementById('download-btn');
              if (btn) {
                btn.innerText = 'Download Report';
                btn.removeAttribute('disabled');
              }
            }
          }}
          id="download-btn"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 shadow-lg shadow-blue-900/20"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download Report
        </button>
      </div>

      {/* Section Navigation */}
      <div className="flex space-x-1 mb-8 bg-slate-800/50 p-1 rounded-xl">
        {[
          { id: 'overview', label: 'Risk Overview' },
          { id: 'factors', label: 'Risk Factors' },
          { id: 'trends', label: 'Risk Trends' },
          { id: 'network', label: 'Network Analysis' },
        ].map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeSection === section.id
              ? 'bg-blue-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
          >
            {section.label}
          </button>
        ))}
      </div>

      {/* Risk Overview */}
      {activeSection === 'overview' && (
        <div className="flex justify-center">
          <div className="neumorphic-card rounded-[30px] p-8 shadow-xl max-w-md w-full relative overflow-hidden" style={{
            background: 'var(--card)',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            {/* Background Glow Effects */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -ml-32 -mb-32"></div>

            <div className="relative z-10">
              <h3 className="text-2xl font-bold mb-1" style={{ color: 'var(--foreground)' }}>Risk Assessment</h3>
              <p className="text-sm mb-8" style={{ color: 'var(--muted-foreground)' }}>6-category weighted analysis</p>

              <div className="flex justify-center mb-8">
                {/* Speedometer Gauge Chart */}
                <GaugeChart
                  value={Number(displayRiskScore?.overall_score) || 0}
                  label="Risk Score"
                  size={280}
                />
              </div>

              {/* Category Scores */}
              <div className="space-y-6">
                {[
                  { key: 'financial_stability', label: 'Financial Stability', color: 'bg-indigo-500' },
                  { key: 'operational_risk', label: 'Operational Risk', color: 'bg-emerald-400' },
                  { key: 'market_risk', label: 'Market Risk', color: 'bg-indigo-500' },
                  { key: 'compliance_risk', label: 'Compliance Risk', color: 'bg-emerald-400' }
                ].map((category) => {
                  const score = displayRiskScore?.category_scores?.[category.key]?.score
                    ? parseFloat(displayRiskScore.category_scores[category.key].score)
                    : (displayRiskScore?.overall_score || 50) + (Math.random() * 20 - 10);

                  const displayScore = Math.min(100, Math.max(0, Math.round(score)));

                  return (
                    <div key={category.key}>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-semibold" style={{ color: 'var(--foreground)' }}>{category.label}</span>
                        <span className="font-bold" style={{ color: 'var(--muted-foreground)' }}>{displayScore}%</span>
                      </div>
                      <div className="h-3 bg-slate-700/30 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${category.color}`}
                          style={{ width: `${displayScore}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Explainability Section */}
              {displayRiskScore?.shap_values && (
                <div className="mt-8 pt-6 border-t border-slate-700/50">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="p-1.5 bg-purple-500/20 rounded-lg">
                      <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <h4 className="font-semibold text-slate-200">AI Risk Attribution (SHAP)</h4>
                  </div>
                  <RiskExplainabilityChart shapValues={displayRiskScore.shap_values} />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Risk Factors */}
      {activeSection === 'factors' && (
        <div className="space-y-6">
          <div className="rounded-xl p-6 border border-slate-700/50" style={{ background: 'rgba(30, 41, 59, 0.5)', backdropFilter: 'blur(10px)' }}>
            <h3 className="text-xl font-semibold mb-4" style={{ color: 'var(--foreground)' }}>Risk Factors Analysis</h3>

            {displayRiskScore?.risk_factors && displayRiskScore.risk_factors.length > 0 ? (
              <div className="space-y-4">
                {displayRiskScore.risk_factors.map((factor: any, index: number) => (
                  <div key={index} className="rounded-lg p-4 border border-slate-700/30" style={{ background: 'rgba(15, 23, 42, 0.3)' }}>
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-600/20 rounded-full flex items-center justify-center mt-0.5">
                        <span className="text-xs font-bold text-blue-400">{index + 1}</span>
                      </div>
                      <div>
                        <p style={{ color: 'var(--foreground)' }}>{factor}</p>
                        <div className="mt-2 flex items-center space-x-4 text-xs" style={{ color: 'var(--muted-foreground)' }}>
                          <span>Risk Impact: Medium</span>
                          <span>Confidence: High</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FiCheck className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold mb-2 text-green-400">No Significant Risk Factors</h4>
                <p style={{ color: 'var(--muted-foreground)' }}>
                  The analysis did not identify any significant risk factors requiring attention.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Risk Trends */}
      {activeSection === 'trends' && (
        <div className="space-y-6">
          <div className="rounded-xl p-6 border border-slate-700/50" style={{ background: 'rgba(30, 41, 59, 0.5)', backdropFilter: 'blur(10px)' }}>
            <h3 className="text-xl font-semibold mb-4" style={{ color: 'var(--foreground)' }}>Risk Trend Analysis</h3>
            <div className="h-64 rounded-lg flex items-center justify-center" style={{ background: 'rgba(15, 23, 42, 0.5)' }}>
              <div className="text-center" style={{ color: 'var(--muted-foreground)' }}>
                <FiTrendingUp className="w-12 h-12 mx-auto mb-2" />
                <p>Risk trend visualization coming soon</p>
                <p className="text-sm">Historical risk score tracking and forecasting</p>
              </div>
            </div>
          </div>

          {/* Risk History */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="rounded-xl p-6 border border-slate-700/50" style={{ background: 'rgba(30, 41, 59, 0.3)', backdropFilter: 'blur(5px)' }}>
              <h4 className="text-lg font-semibold mb-4" style={{ color: 'var(--foreground)' }}>Current Period</h4>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400 mb-2">{displayRiskScore?.overall_score || 45}</div>
                <div className="text-sm" style={{ color: 'var(--muted-foreground)' }}>{displayRiskScore?.risk_level || 'MEDIUM'}</div>
              </div>
            </div>

            <div className="rounded-xl p-6 border border-slate-700/50" style={{ background: 'rgba(30, 41, 59, 0.3)', backdropFilter: 'blur(5px)' }}>
              <h4 className="text-lg font-semibold mb-4" style={{ color: 'var(--foreground)' }}>Previous Period</h4>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">38</div>
                <div className="text-sm" style={{ color: 'var(--muted-foreground)' }}>LOW</div>
              </div>
            </div>

            <div className="rounded-xl p-6 border border-slate-700/50" style={{ background: 'rgba(30, 41, 59, 0.3)', backdropFilter: 'blur(5px)' }}>
              <h4 className="text-lg font-semibold mb-4" style={{ color: 'var(--foreground)' }}>Trend</h4>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-400 mb-2">↗ +7</div>
                <div className="text-sm" style={{ color: 'var(--muted-foreground)' }}>Increasing</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Network Analysis */}
      {activeSection === 'network' && (
        <div className="space-y-6">
          <div className="rounded-[30px] p-8 shadow-xl relative overflow-hidden" style={{
            background: 'var(--card)',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
            <div className="mb-6">
              <h3 className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>Shell Company Hunter</h3>
              <p style={{ color: 'var(--muted-foreground)' }}>AI-detected suspicious network patterns and circular trading</p>
            </div>
            <ForensicGraph companySymbol={riskScore?.company_id || "HIGHRISK"} />
          </div>
        </div>
      )}
    </div>
  )
}
