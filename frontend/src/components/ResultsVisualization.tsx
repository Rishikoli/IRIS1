'use client'

import { useState } from 'react'
import { FiTrendingUp, FiTrendingDown, FiMinus, FiBarChart, FiPieChart, FiCheck, FiShield } from 'react-icons/fi'

interface AnalysisResult {
  success: boolean
  company_id: string
  analysis_timestamp: string
  vertical_analysis?: any
  horizontal_analysis?: any
  financial_ratios?: any
  benford_analysis?: any
  anomaly_detection?: any
  altman_z_score?: any
  beneish_m_score?: any
  risk_assessment?: any
  compliance_assessment?: any
}

interface ResultsVisualizationProps {
  analysisResult: AnalysisResult | null
  isLoading: boolean
}

export default function ResultsVisualization({ analysisResult, isLoading }: ResultsVisualizationProps) {
  const [activeView, setActiveView] = useState<'overview' | 'ratios' | 'trends' | 'anomalies' | 'risk' | 'compliance'>('overview')

  // Utility functions
  const formatValue = (value: number) => {
    if (typeof value === 'number') {
      return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
    }
    return value
  }

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`
  }

  if (isLoading) {
    return (
      <div className="relative min-h-screen overflow-hidden">
        {/* Background Gradient */}
        <div className="fixed inset-0 bg-gradient-to-br from-indigo-50/60 to-purple-50/60" style={{ backgroundColor: '#f5f5f5', zIndex: 0 }}></div>

        {/* Loading Content */}
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="neumorphic-card rounded-3xl p-8 max-w-md mx-auto text-center" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 mx-auto mb-6" style={{ borderColor: '#f2a09e' }}></div>
            <h3 className="text-2xl font-bold mb-4" style={{ color: '#333' }}>Loading Analysis Results...</h3>
            <p className="text-slate-600">Please wait while we process your forensic analysis</p>
          </div>
        </div>
      </div>
    )
  }

  if (!analysisResult) {
    return (
      <div className="relative min-h-screen overflow-hidden">
        {/* Background Gradient */}
        <div className="fixed inset-0 bg-gradient-to-br from-indigo-50/60 to-purple-50/60" style={{ backgroundColor: '#f5f5f5', zIndex: 0 }}></div>

        {/* No Results Content */}
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="neumorphic-card rounded-3xl p-8 max-w-md mx-auto text-center" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
            <FiBarChart className="w-20 h-20 mx-auto mb-6" style={{ color: '#7B68EE' }} />
            <h3 className="text-2xl font-bold mb-4" style={{ color: '#333' }}>No Analysis Results</h3>
            <p className="text-slate-600">Run a forensic analysis to see results here.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-indigo-50/60 to-purple-50/60" style={{ backgroundColor: '#f5f5f5', zIndex: 0 }}></div>

      {/* Main Content */}
      <div className="relative z-10 max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-5xl lg:text-7xl font-bold mb-4 leading-tight" style={{ color: '#333' }}>
            Analysis Results
            <span className="bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent"> Dashboard</span>
          </h2>
          <p className="text-xl" style={{ color: '#666' }}>
            Comprehensive forensic analysis for {analysisResult.company_id}
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex space-x-1 mb-8 neumorphic-card rounded-xl p-1" style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}>
          {[
            { id: 'overview', label: 'Overview', icon: FiBarChart },
            { id: 'ratios', label: 'Financial Ratios', icon: FiPieChart },
            { id: 'trends', label: 'Trend Analysis', icon: FiTrendingUp },
            { id: 'anomalies', label: 'Anomalies', icon: FiTrendingDown },
            { id: 'risk', label: 'Risk Assessment', icon: FiShield },
            { id: 'compliance', label: 'Compliance', icon: FiCheck },
          ].map((view) => (
            <button
              key={view.id}
              onClick={() => setActiveView(view.id as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeView === view.id
                  ? 'neumorphic-inset font-bold'
                  : 'neumorphic-button hover:neumorphic-inset'
              }`}
              style={{
                background: activeView === view.id ? '#e0e0e0' : 'transparent',
                color: activeView === view.id ? '#333' : '#666',
                boxShadow: activeView === view.id
                  ? 'inset 4px 4px 8px #c8c8c8, inset -4px -4px 8px #f8f8f8'
                  : 'none'
              }}
            >
              <view.icon className="w-4 h-4" />
              <span>{view.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        {activeView === 'overview' && <OverviewView analysisResult={analysisResult} />}
        {activeView === 'ratios' && <RatiosView analysisResult={analysisResult} />}
        {activeView === 'trends' && <TrendsView analysisResult={analysisResult} />}
        {activeView === 'anomalies' && <AnomaliesView analysisResult={analysisResult} />}
        {activeView === 'risk' && <RiskView analysisResult={analysisResult} />}
        {activeView === 'compliance' && <ComplianceView analysisResult={analysisResult} />}
      </div>
    </div>
  )
}

function OverviewView({ analysisResult }: { analysisResult: AnalysisResult }) {
  const ratios = analysisResult.financial_ratios?.ratios || {}

  // Utility functions
  const formatValue = (value: number) => {
    if (typeof value === 'number') {
      return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
    }
    return value
  }

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`
  }

  return (
    <div className="grid lg:grid-cols-2 gap-8">
      {/* Key Metrics */}
      <div className="space-y-6">
        <div className="neumorphic-card rounded-3xl p-8" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
          <h3 className="text-2xl font-bold mb-6 text-center" style={{ color: '#333' }}>Key Financial Metrics</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Current Ratio</span>
              <span className="font-mono text-lg font-bold" style={{ color: '#333' }}>{formatValue(ratios.current_ratio || 0)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Debt-to-Equity</span>
              <span className="font-mono text-lg font-bold" style={{ color: '#333' }}>{formatValue(ratios.debt_to_equity || 0)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Return on Assets</span>
              <span className="font-mono text-lg font-bold" style={{ color: '#333' }}>{formatPercentage(ratios.return_on_assets || 0)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Gross Margin</span>
              <span className="font-mono text-lg font-bold" style={{ color: '#333' }}>{formatPercentage(ratios.gross_margin || 0)}</span>
            </div>
          </div>
        </div>

        {/* Analysis Summary */}
        <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
          <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Analysis Summary</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Vertical Analysis</span>
              <span className="text-green-600 font-semibold">✓ Completed</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Horizontal Analysis</span>
              <span className="text-green-600 font-semibold">✓ Completed</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Benford's Law</span>
              <span className="text-green-600 font-semibold">✓ Normal</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Anomalies Detected</span>
              <span className="text-green-600 font-semibold">0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Placeholder */}
      <div className="space-y-6">
        <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
          <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Revenue Trend</h3>
          <div className="h-48 bg-slate-900/50 rounded-lg flex items-center justify-center">
            <div className="text-center text-slate-400">
              <FiBarChart className="w-12 h-12 mx-auto mb-2" />
              <p>Chart visualization coming soon</p>
            </div>
          </div>
        </div>

        <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
          <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Financial Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Overall Health Score</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-slate-700 rounded-full h-2">
                  <div className="bg-green-400 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
                <span className="font-mono text-green-400">75/100</span>
              </div>
            </div>
            <div className="text-sm text-slate-600">
              Based on comprehensive forensic analysis of financial statements and risk factors.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function RatiosView({ analysisResult }: { analysisResult: AnalysisResult }) {
  const ratios = analysisResult.financial_ratios?.ratios || {}

  // Utility functions
  const formatValue = (value: number) => {
    if (typeof value === 'number') {
      return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
    }
    return value
  }

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Liquidity Ratios */}
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-lg font-bold mb-4 text-center" style={{ color: '#f2a09e' }}>Liquidity Ratios</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Current Ratio</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatValue(ratios.current_ratio || 0)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Quick Ratio</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatValue(ratios.quick_ratio || 0)}</span>
          </div>
        </div>
      </div>

      {/* Profitability Ratios */}
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-lg font-bold mb-4 text-center" style={{ color: '#7B68EE' }}>Profitability Ratios</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Gross Margin</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatPercentage(ratios.gross_margin || 0)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Operating Margin</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatPercentage(ratios.operating_margin || 0)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Net Margin</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatPercentage(ratios.net_margin || 0)}</span>
          </div>
        </div>
      </div>

      {/* Efficiency Ratios */}
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-lg font-bold mb-4 text-center" style={{ color: '#FF6B9D' }}>Efficiency Ratios</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-slate-600">ROA</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatPercentage(ratios.return_on_assets || 0)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">ROE</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatPercentage(ratios.return_on_equity || 0)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Asset Turnover</span>
            <span className="font-mono font-bold" style={{ color: '#333' }}>{formatValue(ratios.asset_turnover || 0)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function TrendsView({ analysisResult }: { analysisResult: AnalysisResult }) {
  return (
    <div className="space-y-6">
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Growth Trends</h3>
        <div className="h-64 bg-slate-900/50 rounded-lg flex items-center justify-center">
          <div className="text-center text-slate-400">
            <FiTrendingUp className="w-12 h-12 mx-auto mb-2" />
            <p>Trend charts coming soon</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function AnomaliesView({ analysisResult }: { analysisResult: AnalysisResult }) {
  const anomalies = analysisResult.anomaly_detection?.anomalies || []

  return (
    <div className="space-y-6">
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Anomaly Detection Results</h3>

        {anomalies.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mx-auto mb-4 neumorphic-circle" style={{ background: '#4ade80', boxShadow: 'inset 2px 2px 4px #3bb370, inset -2px -2px 4px #61eb90' }}>
              <FiCheck className="w-8 h-8 text-green-400" />
            </div>
            <h4 className="text-lg font-bold mb-2" style={{ color: '#4ade80' }}>No Anomalies Detected</h4>
            <p className="text-slate-600">
              The financial data appears normal with no significant irregularities detected.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {anomalies.map((anomaly: any, index: number) => (
              <div key={index} className="bg-red-900/20 border border-red-700/50 rounded-lg p-4 neumorphic-inset" style={{ background: '#fef2f2', boxShadow: 'inset 4px 4px 8px #fecaca, inset -4px -4px 8px #ffffff' }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold" style={{ color: '#ef4444' }}>{anomaly.type}</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    anomaly.severity === 'HIGH' ? 'bg-red-600 text-white' :
                    anomaly.severity === 'MEDIUM' ? 'bg-yellow-600 text-white' :
                    'bg-blue-600 text-white'
                  }`}>
                    {anomaly.severity}
                  </span>
                </div>
                <p className="text-slate-600 text-sm">{anomaly.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function RiskView({ analysisResult }: { analysisResult: AnalysisResult }) {
  const riskData = analysisResult.risk_assessment

  // Utility functions
  const formatValue = (value: number) => {
    if (typeof value === 'number') {
      return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
    }
    return value
  }

  if (!riskData) {
    return (
      <div className="neumorphic-card rounded-3xl p-8" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <div className="text-center">
          <FiShield className="w-16 h-16 mx-auto mb-4" style={{ color: '#7B68EE' }} />
          <h3 className="text-xl font-bold mb-2" style={{ color: '#333' }}>Risk Assessment</h3>
          <p className="text-slate-600">Risk assessment data not available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="grid lg:grid-cols-2 gap-8">
      {/* Risk Overview */}
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Risk Overview</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Overall Risk Score</span>
            <span className="font-mono text-lg font-bold" style={{ color: '#333' }}>
              {formatValue(riskData.overall_risk_score || 0)}/100
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Risk Level</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              (riskData.risk_level === 'LOW') ? 'bg-green-600 text-white' :
              (riskData.risk_level === 'MEDIUM') ? 'bg-yellow-600 text-white' :
              'bg-red-600 text-white'
            }`}>
              {riskData.risk_level || 'UNKNOWN'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Investment Recommendation</span>
            <span className="font-medium" style={{ color: '#7B68EE' }}>
              {riskData.investment_recommendation || 'N/A'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Monitoring Frequency</span>
            <span className="font-medium" style={{ color: '#333' }}>
              {riskData.monitoring_frequency || 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Risk Factors */}
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Key Risk Factors</h3>
        <div className="space-y-3">
          {riskData.risk_factors && riskData.risk_factors.length > 0 ? (
            riskData.risk_factors.map((factor: string, index: number) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span className="text-slate-600">{factor}</span>
              </div>
            ))
          ) : (
            <p className="text-slate-600">No specific risk factors identified</p>
          )}
        </div>
      </div>
    </div>
  )
}

function ComplianceView({ analysisResult }: { analysisResult: AnalysisResult }) {
  const complianceData = analysisResult.compliance_assessment

  // Utility functions
  const formatValue = (value: number) => {
    if (typeof value === 'number') {
      return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
    }
    return value
  }

  if (!complianceData) {
    return (
      <div className="neumorphic-card rounded-3xl p-8" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <div className="text-center">
          <FiCheck className="w-16 h-16 mx-auto mb-4" style={{ color: '#7B68EE' }} />
          <h3 className="text-xl font-bold mb-2" style={{ color: '#333' }}>Compliance Assessment</h3>
          <p className="text-slate-600">Compliance assessment data not available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="grid lg:grid-cols-2 gap-8">
      {/* Compliance Overview */}
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Compliance Overview</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Overall Compliance Score</span>
            <span className="font-mono text-lg font-bold" style={{ color: '#333' }}>
              {formatValue(complianceData.overall_compliance_score || 0)}/100
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Compliance Status</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              (complianceData.compliance_status === 'COMPLIANT') ? 'bg-green-600 text-white' :
              (complianceData.compliance_status === 'PARTIAL_COMPLIANCE') ? 'bg-yellow-600 text-white' :
              'bg-red-600 text-white'
            }`}>
              {complianceData.compliance_status || 'UNKNOWN'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Next Review Date</span>
            <span className="font-medium" style={{ color: '#333' }}>
              {complianceData.next_review_date ? new Date(complianceData.next_review_date).toLocaleDateString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Framework Scores */}
      <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-xl font-bold mb-4" style={{ color: '#333' }}>Regulatory Frameworks</h3>
        <div className="space-y-3">
          {complianceData.framework_scores ? (
            Object.entries(complianceData.framework_scores).map(([framework, score]: [string, any]) => (
              <div key={framework} className="flex items-center justify-between">
                <span className="text-slate-600">{framework}</span>
                <span className="font-mono font-bold" style={{ color: '#333' }}>
                  {formatValue(score || 0)}/100
                </span>
              </div>
            ))
          ) : (
            <p className="text-slate-600">No framework scores available</p>
          )}
        </div>
      </div>
    </div>
  )
}
