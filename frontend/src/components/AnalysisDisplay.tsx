'use client'

import { useState, useEffect } from 'react'
import { FiActivity, FiTrendingUp, FiCheck, FiX, FiLoader, FiShield } from 'react-icons/fi'
import CompanyNotFound from './CompanyNotFound'
import SebiRiskComposition from './charts/SebiRiskComposition'
import SebiFlagPanel from './SebiFlagPanel'

interface AnalysisDisplayProps {
  companySymbol: string
  isLoading: boolean
  error: string
}

export default function AnalysisDisplay({ companySymbol, isLoading, error }: AnalysisDisplayProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [isComplete, setIsComplete] = useState(false)

  const analysisSteps = [
    { id: 'init', label: 'Initializing analysis...', duration: 1000 },
    { id: 'ingestion', label: 'Ingesting financial data...', duration: 2000 },
    { id: 'vertical', label: 'Performing vertical analysis...', duration: 1500 },
    { id: 'horizontal', label: 'Performing horizontal analysis...', duration: 1500 },
    { id: 'ratios', label: 'Calculating financial ratios...', duration: 2000 },
    { id: 'benford', label: 'Running Benford\'s Law analysis...', duration: 2500 },
    { id: 'anomalies', label: 'Detecting anomalies...', duration: 2000 },
    { id: 'complete', label: 'Analysis completed successfully!', duration: 1000 },
  ]

  useEffect(() => {
    if (!isLoading) {
      setProgress(0)
      setCurrentStep('')
      setIsComplete(false)
      return
    }

    let currentIndex = 0
    setProgress(0)
    setCurrentStep(analysisSteps[0].label)

    const interval = setInterval(() => {
      currentIndex++

      if (currentIndex >= analysisSteps.length) {
        setProgress(100)
        setCurrentStep(analysisSteps[analysisSteps.length - 1].label)
        setIsComplete(true)
        clearInterval(interval)
        return
      }

      const step = analysisSteps[currentIndex]
      setProgress((currentIndex / (analysisSteps.length - 1)) * 100)
      setCurrentStep(step.label)

      setTimeout(() => {
        if (currentIndex < analysisSteps.length - 1) {
          setProgress(((currentIndex + 1) / (analysisSteps.length - 1)) * 100)
          setCurrentStep(analysisSteps[currentIndex + 1].label)
        }
      }, step.duration)
    }, 500)

    return () => clearInterval(interval)
  }, [isLoading])

  if (!isLoading && !error) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <div className="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <FiCheck className="w-8 h-8 text-green-400" />
        </div>
        <h3 className="text-2xl font-semibold mb-2">Ready for Analysis</h3>
        <p className="text-slate-400">
          Select a company from the search tab to begin forensic analysis.
        </p>
      </div>
    )
  }

  if (error) {
    if (error.includes('Not Found') || error.includes('404')) {
      return (
        <CompanyNotFound
          companySymbol={companySymbol}
          onBack={() => window.location.reload()}
        />
      )
    }

    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-900/20 border border-red-700/50 rounded-xl p-8 text-center">
          <div className="w-16 h-16 bg-red-600/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <FiX className="w-8 h-8 text-red-400" />
          </div>
          <h3 className="text-2xl font-semibold mb-2 text-red-400">Analysis Failed</h3>
          <p className="text-slate-300 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Forensic Analysis in Progress</h2>
        <p className="text-slate-400">Analyzing {companySymbol} financial data</p>
      </div>

      {/* Progress Card */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-slate-700/50">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-300">Progress</span>
            <span className="text-sm text-slate-400">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-slate-700/50 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Current Step */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-12 h-12 bg-blue-600/20 rounded-xl flex items-center justify-center">
            <FiLoader className="w-6 h-6 text-blue-400 animate-spin" />
          </div>
          <div>
            <div className="font-semibold text-white">{currentStep}</div>
            <div className="text-sm text-slate-400">Processing financial data...</div>
          </div>
        </div>

        {/* Analysis Steps */}
        <div className="space-y-3">
          {analysisSteps.slice(0, -1).map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 ${index < Math.floor((progress / 100) * (analysisSteps.length - 1))
                ? 'bg-green-900/20 border border-green-700/50'
                : 'bg-slate-900/30 border border-slate-700/30'
                }`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${index < Math.floor((progress / 100) * (analysisSteps.length - 1))
                ? 'bg-green-600 text-white'
                : 'bg-slate-600 text-slate-400'
                }`}>
                {index < Math.floor((progress / 100) * (analysisSteps.length - 1)) ? (
                  <FiCheck className="w-4 h-4" />
                ) : (
                  <span className="text-xs">{index + 1}</span>
                )}
              </div>
              <span className={`text-sm ${index < Math.floor((progress / 100) * (analysisSteps.length - 1))
                ? 'text-green-400'
                : 'text-slate-400'
                }`}>
                {step.label}
              </span>
            </div>
          ))}
        </div>

        {/* Analysis Info */}
        <div className="mt-8 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
          <div className="flex items-center space-x-2 mb-2">
            <FiActivity className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-slate-300">Analysis Details</span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-400">Company:</span>
              <span className="text-white ml-2 font-mono">{companySymbol}</span>
            </div>
            <div>
              <span className="text-slate-400">Data Source:</span>
              <span className="text-white ml-2">Enhanced Mock Data</span>
            </div>
            <div>
              <span className="text-slate-400">Analysis Type:</span>
              <span className="text-white ml-2">Comprehensive Forensic</span>
            </div>
            <div>
              <span className="text-slate-400">Status:</span>
              <span className="text-green-400 ml-2">In Progress</span>
            </div>
          </div>
        </div>
      </div>

      {/* Technical Details */}
      <div className="mt-8 grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <FiTrendingUp className="w-5 h-5 text-blue-400" />
            <span>Analysis Techniques</span>
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Vertical Analysis</span>
              <span className="text-green-400">✓ Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Horizontal Analysis</span>
              <span className="text-green-400">✓ Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Financial Ratios</span>
              <span className="text-green-400">✓ Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Benford's Law</span>
              <span className="text-green-400">✓ Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Anomaly Detection</span>
              <span className="text-green-400">✓ Active</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <h3 className="text-lg font-semibold mb-4">Data Processing</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Statements Collected</span>
              <span className="text-white">6</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Time Periods</span>
              <span className="text-white">3 years</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Data Quality</span>
              <span className="text-green-400">High</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Processing Speed</span>
              <span className="text-blue-400">Real-time</span>
            </div>
          </div>
        </div>
      </div>

      {/* SEBI Advisory & Supervision Section */}
      <div className="mt-12 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
            <FiShield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">SEBI Advisory & Supervision</h2>
            <p className="text-slate-400">Risk, Concentration & Regulatory Compliance View</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Risk Composition Chart (Span 2 cols) */}
          <div className="lg:col-span-2">
            <SebiRiskComposition
              data={[
                // Mock Data for Visualization - In real app, this comes from backend
                { name: companySymbol, mScore: -1.5, zScore: 1.2, concentration: 15, sector: 'IT Services' },
                { name: 'Portfolio Avg', mScore: -2.4, zScore: 3.5, concentration: 5, sector: 'Diversified' },
                { name: 'Peer 1', mScore: -1.9, zScore: 2.1, concentration: 8, sector: 'IT Services' },
                { name: 'Peer 2', mScore: -2.8, zScore: 4.0, concentration: 4, sector: 'IT Services' },
              ]}
            />
          </div>

          {/* Regulatory Flag Panel (Span 1 col) */}
          <div className="lg:col-span-1">
            <SebiFlagPanel
              data={{
                singleStockExposure: 15, // > 10% Breach
                sectorExposure: 22,      // Safe (< 25%)
                zScore: 1.2,             // Distress (< 1.8)
                hasShellLinks: false,    // Safe
                turnoverRatio: 2.4
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
