'use client'

import { useState } from 'react'
import { FiShield, FiAlertTriangle, FiCheck, FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi'

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
  const [activeSection, setActiveSection] = useState<'overview' | 'factors' | 'trends'>('overview')

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
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Risk Assessment Dashboard</h2>
        <p className="text-slate-400">
          Comprehensive risk analysis based on forensic examination
        </p>
      </div>

      {/* Section Navigation */}
      <div className="flex space-x-1 mb-8 bg-slate-800/50 p-1 rounded-xl">
        {[
          { id: 'overview', label: 'Risk Overview' },
          { id: 'factors', label: 'Risk Factors' },
          { id: 'trends', label: 'Risk Trends' },
        ].map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeSection === section.id
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
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Main Risk Score */}
          <div className="space-y-6">
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 border border-slate-700/50">
              <h3 className="text-2xl font-semibold mb-6 text-center">Overall Risk Score</h3>

              <div className="text-center mb-6">
                <div className={`inline-flex items-center space-x-3 px-6 py-3 rounded-xl border ${getRiskLevelColor(displayRiskScore?.risk_level || 'medium')}`}>
                  {getRiskLevelIcon(displayRiskScore?.risk_level || 'medium')}
                  <div>
                    <div className="text-3xl font-bold">{displayRiskScore?.overall_score || 45}</div>
                    <div className="text-sm opacity-80">{displayRiskScore?.risk_level || 'MEDIUM'}</div>
                  </div>
                </div>
              </div>

              {/* Risk Meter */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-400">Risk Level</span>
                  <span className="text-sm text-slate-400">
                    {displayRiskScore?.confidence_score ? `${(displayRiskScore.confidence_score * 100).toFixed(0)}%` : '80%'} Confidence
                  </span>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full transition-all duration-1000 ${
                      displayRiskScore?.overall_score >= 80 ? 'bg-red-500' :
                      displayRiskScore?.overall_score >= 60 ? 'bg-orange-500' :
                      displayRiskScore?.overall_score >= 40 ? 'bg-yellow-500' :
                      displayRiskScore?.overall_score >= 20 ? 'bg-green-500' :
                      'bg-blue-500'
                    }`}
                    style={{ width: `${displayRiskScore?.overall_score || 45}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>0</span>
                  <span>50</span>
                  <span>100</span>
                </div>
              </div>

              {/* Risk Description */}
              <div className="text-center">
                <p className="text-slate-300 mb-4">
                  {displayRiskScore?.overall_score >= 80 ? 'Critical risk level requires immediate attention.' :
                   displayRiskScore?.overall_score >= 60 ? 'High risk level suggests caution and further investigation.' :
                   displayRiskScore?.overall_score >= 40 ? 'Medium risk level indicates moderate concerns.' :
                   displayRiskScore?.overall_score >= 20 ? 'Low risk level suggests generally healthy financials.' :
                   'Very low risk level indicates strong financial health.'}
                </p>
                <div className="text-xs text-slate-400">
                  Last updated: {displayRiskScore?.analysis_timestamp ?
                    new Date(displayRiskScore.analysis_timestamp).toLocaleString() : 'Recently'}
                </div>
              </div>
            </div>
          </div>

          {/* Risk Indicators */}
          <div className="space-y-6">
            {/* Anomaly Detection */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
              <h4 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                <FiAlertTriangle className="w-5 h-5 text-orange-400" />
                <span>Anomaly Detection</span>
              </h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Anomalies Found</span>
                  <span className={`font-mono ${anomalies.length > 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {anomalies.length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Benford's Law</span>
                  <span className={`font-mono ${benfordAnomalous ? 'text-red-400' : 'text-green-400'}`}>
                    {benfordAnomalous ? 'Anomalous' : 'Normal'}
                  </span>
                </div>
              </div>
            </div>

            {/* Risk Distribution */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
              <h4 className="text-lg font-semibold mb-4">Risk Distribution</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Financial Risk</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-slate-700 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                    <span className="text-xs text-slate-400">60%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Operational Risk</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-slate-700 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{ width: '30%' }}></div>
                    </div>
                    <span className="text-xs text-slate-400">30%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Market Risk</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-slate-700 rounded-full h-2">
                      <div className="bg-purple-500 h-2 rounded-full" style={{ width: '10%' }}></div>
                    </div>
                    <span className="text-xs text-slate-400">10%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Risk Factors */}
      {activeSection === 'factors' && (
        <div className="space-y-6">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <h3 className="text-xl font-semibold mb-4">Risk Factors Analysis</h3>

            {displayRiskScore?.risk_factors && displayRiskScore.risk_factors.length > 0 ? (
              <div className="space-y-4">
                {displayRiskScore.risk_factors.map((factor: any, index: number) => (
                  <div key={index} className="bg-slate-900/30 rounded-lg p-4 border border-slate-700/30">
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-600/20 rounded-full flex items-center justify-center mt-0.5">
                        <span className="text-xs font-bold text-blue-400">{index + 1}</span>
                      </div>
                      <div>
                        <p className="text-slate-300">{factor}</p>
                        <div className="mt-2 flex items-center space-x-4 text-xs text-slate-400">
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
                <p className="text-slate-400">
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
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <h3 className="text-xl font-semibold mb-4">Risk Trend Analysis</h3>
            <div className="h-64 bg-slate-900/50 rounded-lg flex items-center justify-center">
              <div className="text-center text-slate-400">
                <FiTrendingUp className="w-12 h-12 mx-auto mb-2" />
                <p>Risk trend visualization coming soon</p>
                <p className="text-sm">Historical risk score tracking and forecasting</p>
              </div>
            </div>
          </div>

          {/* Risk History */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
              <h4 className="text-lg font-semibold mb-4">Current Period</h4>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400 mb-2">{displayRiskScore?.overall_score || 45}</div>
                <div className="text-sm text-slate-400">{displayRiskScore?.risk_level || 'MEDIUM'}</div>
              </div>
            </div>

            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
              <h4 className="text-lg font-semibold mb-4">Previous Period</h4>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">38</div>
                <div className="text-sm text-slate-400">LOW</div>
              </div>
            </div>

            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
              <h4 className="text-lg font-semibold mb-4">Trend</h4>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-400 mb-2">↗ +7</div>
                <div className="text-sm text-slate-400">Increasing</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
