'use client'

import { useState, useEffect } from 'react'
import { FiSearch, FiTrendingUp, FiShield, FiBarChart, FiActivity, FiSettings } from 'react-icons/fi'
import CompanySearch from '@/components/CompanySearch'
import AnalysisDisplay from '@/components/AnalysisDisplay'
import RiskDashboard from '@/components/RiskDashboard'
import ResultsVisualization from '@/components/ResultsVisualization' // Keep for legacy or specific use if needed
import ForensicSection from '@/components/ForensicSection' // Add import


interface AnalysisResult {
  success: boolean
  company_id: string
  analysis_timestamp: string
  vertical_analysis?: any
  horizontal_analysis?: any
  financial_ratios?: any
  anomaly_detection?: any
  altman_z_score?: any
  beneish_m_score?: any
}

interface RiskScore {
  success: boolean
  company_id: string
  risk_score: {
    overall_risk_score: number // Renamed from overall_score
    risk_level: string
    confidence_score: number
    risk_factors: string[]
    analysis_timestamp: string
    investment_recommendation?: string
    monitoring_frequency?: string
    category_scores?: any
    shap_values?: Record<string, number> // Add missing optional property
  }
}

type ActiveTab = 'search' | 'analysis' | 'results' | 'risk'

export default function IRISDashboard() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('search')
  const [selectedCompany, setSelectedCompany] = useState<string>('')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [riskScore, setRiskScore] = useState<RiskScore | null>(null)

  // Sentiment Data State
  const [sentimentData, setSentimentData] = useState<any>(null)
  const [isSentimentLoading, setIsSentimentLoading] = useState(false)

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')

  const tabs = [
    { id: 'search', label: 'Company Search', icon: FiSearch },
    { id: 'analysis', label: 'Forensic Analysis', icon: FiTrendingUp },
    { id: 'results', label: 'Analysis Results', icon: FiBarChart },
    { id: 'risk', label: 'Risk Assessment', icon: FiShield },
  ]

  const handleCompanySelect = async (companySymbol: string) => {
    setSelectedCompany(companySymbol)
    setActiveTab('analysis')
    setIsLoading(true)
    setError('')

    try {
      // Run forensic analysis (proxy via Next.js rewrite)
      const analysisResponse = await fetch(`/api/forensic/${companySymbol}`, {
        method: 'POST',
      })

      if (!analysisResponse.ok) {
        throw new Error(`Analysis failed: ${analysisResponse.statusText}`)
      }

      const analysisData = await analysisResponse.json()
      setAnalysisResult(analysisData)

      // Check if risk data is already in the forensic analysis response
      if (analysisData.risk_assessment) {
        setRiskScore({
          success: true,
          company_id: companySymbol,
          risk_score: {
            overall_risk_score: analysisData.risk_assessment.overall_risk_score || 45, // Renamed from overall_score
            risk_level: analysisData.risk_assessment.risk_level || 'MEDIUM',
            confidence_score: analysisData.risk_assessment.confidence_score || 0.8,
            risk_factors: analysisData.risk_assessment.risk_factors || [],
            analysis_timestamp: analysisData.analysis_timestamp,
            investment_recommendation: analysisData.risk_assessment.investment_recommendation,
            monitoring_frequency: analysisData.risk_assessment.monitoring_frequency,
            category_scores: analysisData.risk_assessment.category_scores,
            shap_values: analysisData.risk_assessment.shap_values
          }
        })
      } else {
        // Get risk score (proxy via Next.js rewrite) - fallback if not in forensic response
        try {
          const riskResponse = await fetch(`/api/risk-score/${companySymbol}`, {
            method: 'POST',
          })

          if (riskResponse.ok) {
            const riskData = await riskResponse.json()
            setRiskScore(riskData)
          }
        } catch (error) {
          console.warn('Could not fetch separate risk score:', error)
        }
      }


      // Fetch Sentiment Analysis (Parallel)
      setIsSentimentLoading(true)
      fetch('/api/v1/sentiment/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_symbol: companySymbol }),
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            setSentimentData(data.data)
          }
        })
        .catch(err => console.error('Sentiment fetch failed:', err))
        .finally(() => setIsSentimentLoading(false))

      setActiveTab('results')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      console.error('Error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'search':
        return <CompanySearch onCompanySelect={handleCompanySelect} />
      case 'analysis':
        return <AnalysisDisplay
          companySymbol={selectedCompany}
          isLoading={isLoading}
          error={error}
        />
      case 'results':
        return <ForensicSection
          analysisData={analysisResult}
          isLoading={isLoading}
          sentimentData={sentimentData}
          isSentimentLoading={isSentimentLoading}
        />
      case 'risk':
        return <RiskDashboard
          riskScore={riskScore}
          analysisResult={analysisResult}
          isLoading={isLoading}
        />
      default:
        return <CompanySearch onCompanySelect={handleCompanySelect} />
    }
  }

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: '#f5f5f5' }}>
      {/* Sidebar Navigation */}
      <aside className="w-64 neumorphic-card" style={{
        background: '#f0f0f0',
        boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff',
        borderRadius: '0 1rem 1rem 0',
        margin: '1rem 0 1rem 1rem'
      }}>
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-8">
            <div className="w-10 h-10 neumorphic-inset rounded-xl flex items-center justify-center" style={{
              background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)',
              boxShadow: 'inset 4px 4px 8px #d89592, inset -4px -4px 8px #ffcfc8'
            }}>
              <FiActivity className="w-6 h-6" style={{ color: '#ffffff' }} />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: '#333' }}>
                IRIS Analysis
              </h1>
              <p className="text-xs" style={{ color: '#666' }}>Forensic Platform</p>
            </div>
          </div>

          <nav className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as ActiveTab)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium transition-all duration-200 rounded-lg ${activeTab === tab.id
                    ? 'neumorphic-inset'
                    : 'neumorphic-button hover:neumorphic-inset'
                    }`}
                  style={{
                    background: activeTab === tab.id ? '#e0e0e0' : 'transparent',
                    color: activeTab === tab.id ? '#333' : '#666',
                    boxShadow: activeTab === tab.id
                      ? 'inset 4px 4px 8px #c8c8c8, inset -4px -4px 8px #f8f8f8'
                      : 'none',
                    justifyContent: 'flex-start'
                  }}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-6 relative">
        {/* Animated Grid Background - Upward to Downward Flow */}

        {/* Content Overlay */}
        <div className="relative z-10 max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  )
}
