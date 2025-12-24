'use client'

import { useState } from 'react'
import { FiShield, FiAlertTriangle, FiCheck, FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi'

import RiskExplainabilityChart from './charts/RiskExplainabilityChart'

interface RiskScore {
  success: boolean
  company_id: string
  risk_score: {
    overall_risk_score: number
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

  if (!displayRiskScore?.shap_values) {
    return (
      <div className="text-center py-16">
        <FiShield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold mb-2">No Risk Attribution Data</h3>
        <p className="text-slate-400">Run a forensic analysis to see AI risk attribution here.</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className={`neumorphic-card rounded-3xl p-8 overflow-hidden relative transition-all duration-300 hover:scale-[1.01] ${(displayRiskScore?.overall_risk_score || 0) > 75 ? 'animate-pulse-red ring-2 ring-red-500/50' : ''}`} style={{
        background: 'var(--card)',
        backdropFilter: 'blur(20px)',
        boxShadow: '20px 20px 60px #bebebe, -20px -20px 60px #ffffff',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-32 h-32 bg-purple-500/10 blur-3xl rounded-full pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-32 h-32 bg-blue-500/10 blur-3xl rounded-full pointer-events-none"></div>

        <div className="flex items-center gap-3 mb-6 relative z-10">
          <div className="p-2 bg-purple-500/20 rounded-xl">
            <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800 dark:text-white">AI Risk Attribution</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              SHAP (SHapley Additive exPlanations) analysis of risk factors
            </p>
          </div>

        </div>

        <div className="relative z-10">
          <RiskExplainabilityChart shapValues={displayRiskScore.shap_values} />
        </div>
      </div >
    </div >
  )
}
