'use client'

import { useState, useEffect, useRef } from 'react'
import { FiSearch, FiTrendingUp, FiCheck, FiAlertCircle, FiShield, FiX } from 'react-icons/fi'

interface Company {
  symbol: string
  name: string
}

interface CompanySearchProps {
  onCompanySelect: (symbol: string) => void
}

export default function CompanySearch({ onCompanySelect }: CompanySearchProps) {
  const [companies, setCompanies] = useState<Company[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const manualInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchCompanies()
  }, [])

  useEffect(() => {
    if (searchTerm.trim()) {
      const filtered = companies.filter(company =>
        company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        company.symbol.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredCompanies(filtered)
    } else {
      setFilteredCompanies(companies)
    }
  }, [searchTerm, companies])

  const fetchCompanies = async () => {
    setIsLoading(true)
    setError('')

    try {
      // Use Next.js rewrite proxy to avoid CORS in development
      const response = await fetch('/api/companies')
      if (!response.ok) {
        throw new Error('Failed to fetch companies')
      }

      const data = await response.json()
      setCompanies(data.companies || [])
    } catch (err) {
      setError('Failed to load companies. Please ensure the backend is running.')
      console.error('Error fetching companies:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const validateSymbol = (symbol: string): { isValid: boolean; message: string } => {
    if (!symbol) {
      return { isValid: false, message: 'Please enter a company symbol' }
    }
    
    // Basic validation for common exchange suffixes
    const validSuffixes = ['.NS', '.BO', '.NSE', '.BSE']
    const hasValidSuffix = validSuffixes.some(suffix => symbol.endsWith(suffix))
    
    if (!hasValidSuffix) {
      return { 
        isValid: false, 
        message: 'Please include a valid exchange suffix (e.g., .NS for NSE, .BO for BSE)'
      }
    }
    
    return { isValid: true, message: '' }
  }

  const handleCompanyClick = (symbol: string) => {
    const validation = validateSymbol(symbol)
    if (!validation.isValid) {
      setErrorMessage(validation.message)
      setShowErrorModal(true)
      return
    }
    onCompanySelect(symbol)
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent">
          Forensic Financial Analysis
        </h2>
        <p className="text-xl mb-6" style={{ color: '#666' }}>
          Analyze company financial health with advanced forensic techniques
        </p>
        <div className="flex items-center justify-center space-x-8 text-sm" style={{ color: '#666' }}>
          <div className="flex items-center space-x-2">
            <FiTrendingUp className="w-4 h-4" style={{ color: '#f2a09e' }} />
            <span>Financial Ratios</span>
          </div>
          <div className="flex items-center space-x-2">
            <FiCheck className="w-4 h-4" style={{ color: '#7B68EE' }} />
            <span>Anomaly Detection</span>
          </div>
          <div className="flex items-center space-x-2">
            <FiShield className="w-4 h-4" style={{ color: '#FF6B9D' }} />
            <span>Risk Assessment</span>
          </div>
        </div>
      </div>

      {/* Search Section */}
      <div className="neumorphic-card rounded-2xl p-8" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
        <h3 className="text-2xl font-bold mb-6 text-center" style={{ color: '#333' }}>Select Company for Analysis</h3>

        {/* Search Input */}
        <div className="relative mb-6">
          <FiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: '#666' }} />
          <input
            type="text"
            placeholder="Search companies by name or symbol..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-4 neumorphic-inset rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            style={{
              background: '#e0e0e0',
              border: 'none',
              color: '#333',
              boxShadow: 'inset 6px 6px 12px #c8c8c8, inset -6px -6px 12px #f8f8f8'
            }}
          />
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: '#f2a09e' }}></div>
            <span className="ml-3" style={{ color: '#666' }}>Loading companies...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="flex items-center justify-center py-8 text-red-400 neumorphic-inset rounded-xl" style={{
            background: '#fef2f2',
            boxShadow: 'inset 4px 4px 8px #fecaca, inset -4px -4px 8px #ffffff',
            border: '1px solid #fecaca',
            color: '#ef4444'
          }}>
            <FiAlertCircle className="w-5 h-5 mr-2" />
            <span>{error}</span>
          </div>
        )}

        {/* Companies List */}
        {!isLoading && !error && (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredCompanies.length === 0 ? (
              <div className="text-center py-8" style={{ color: '#666' }}>
                {searchTerm ? 'No companies found matching your search.' : 'No companies available.'}
              </div>
            ) : (
              filteredCompanies.map((company) => (
                <div
                  key={company.symbol}
                  onClick={() => handleCompanyClick(company.symbol)}
                  className="neumorphic-button hover:neumorphic-inset rounded-xl p-4 cursor-pointer transition-all duration-200"
                  style={{
                    background: '#f0f0f0',
                    boxShadow: '6px 6px 12px #d0d0d0, -6px -6px 12px #ffffff',
                    border: '1px solid transparent'
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold" style={{ color: '#333' }}>{company.name}</div>
                      <div className="text-sm" style={{ color: '#666' }}>{company.symbol}</div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="px-3 py-1 rounded-full text-xs font-medium" style={{
                        background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)',
                        color: '#ffffff',
                        boxShadow: '4px 4px 8px #d89592, -4px -4px 8px #ffcfc8'
                      }}>
                        NSE
                      </span>
                      <FiTrendingUp className="w-4 h-4" style={{ color: '#7B68EE' }} />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Manual Entry */}
        <div className="mt-6 pt-6 border-t" style={{ borderColor: '#e0e0e0' }}>
          <h4 className="text-sm font-medium mb-3" style={{ color: '#333' }}>Or Enter Company Symbol Manually</h4>
          <div className="flex space-x-3">
            <input
              ref={manualInputRef}
              type="text"
              placeholder="e.g., RELIANCE.BO, TCS.NS"
              className="flex-1 px-4 py-3 neumorphic-inset rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              style={{
                background: '#e0e0e0',
                border: 'none',
                color: '#333',
                boxShadow: 'inset 6px 6px 12px #c8c8c8, inset -6px -6px 12px #f8f8f8'
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const value = (e.target as HTMLInputElement).value.trim().toUpperCase()
                  if (value) {
                    handleCompanyClick(value)
                  }
                }
              }}
            />
            <button
              className="px-6 py-3 rounded-xl font-medium transition-colors duration-200"
              style={{
                background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)',
                color: 'white',
                boxShadow: '4px 4px 8px #d0d0d0, -4px -4px 8px #ffffff'
              }}
              onClick={() => {
                const value = manualInputRef.current?.value.trim().toUpperCase()
                if (value) {
                  handleCompanyClick(value)
                }
              }}
              className="px-6 py-3 neumorphic-button font-medium transition-all duration-200"
              style={{
                background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)',
                color: '#ffffff',
                boxShadow: '6px 6px 12px #d89592, -6px -6px 12px #ffcfc8',
                borderRadius: '0.75rem'
              }}
            >
              Analyze
            </button>
          </div>
        </div>
      </div>

      {/* Features Preview */}
      <div className="mt-12 grid md:grid-cols-3 gap-6">
        <div className="neumorphic-card rounded-xl p-6" style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}>
          <div className="w-12 h-12 neumorphic-inset rounded-xl flex items-center justify-center mb-4 mx-auto" style={{
            background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)',
            boxShadow: 'inset 4px 4px 8px #d89592, inset -4px -4px 8px #ffcfc8'
          }}>
            <FiTrendingUp className="w-6 h-6" style={{ color: '#ffffff' }} />
          </div>
          <h3 className="text-lg font-bold mb-2 text-center" style={{ color: '#333' }}>Forensic Analysis</h3>
          <p className="text-slate-600 text-sm text-center">
            Comprehensive financial statement analysis including vertical, horizontal, and ratio analysis.
          </p>
        </div>

        <div className="neumorphic-card rounded-xl p-6" style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}>
          <div className="w-12 h-12 neumorphic-inset rounded-xl flex items-center justify-center mb-4 mx-auto" style={{
            background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)',
            boxShadow: 'inset 4px 4px 8px #6b5acc, inset -4px -4px 8px #8b79f0'
          }}>
            <FiCheck className="w-6 h-6" style={{ color: '#ffffff' }} />
          </div>
          <h3 className="text-lg font-bold mb-2 text-center" style={{ color: '#333' }}>Anomaly Detection</h3>
          <p className="text-slate-600 text-sm text-center">
            Advanced algorithms to detect irregularities and potential financial manipulation.
          </p>
        </div>

        <div className="neumorphic-card rounded-xl p-6" style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}>
          <div className="w-12 h-12 neumorphic-inset rounded-xl flex items-center justify-center mb-4 mx-auto" style={{
            background: 'linear-gradient(135deg, #FF6B9D 0%, #FF4081 100%)',
            boxShadow: 'inset 4px 4px 8px #e85a8a, inset -4px -4px 8px #ff7cb0'
          }}>
            <FiShield className="w-6 h-6" style={{ color: '#ffffff' }} />
          </div>
          <h3 className="text-lg font-bold mb-2 text-center" style={{ color: '#333' }}>Risk Assessment</h3>
          <p className="text-slate-600 text-sm text-center">
            Multi-factor risk scoring with confidence levels and detailed risk factor analysis.
          </p>
        </div>
      </div>

      {/* Error Modal */}
      {showErrorModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4" style={{
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)'
          }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-red-500 flex items-center">
                <FiAlertCircle className="mr-2" /> Invalid Input
              </h3>
              <button 
                onClick={() => setShowErrorModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <FiX className="w-5 h-5" />
              </button>
            </div>
            <p className="text-gray-700 mb-6">{errorMessage}</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowErrorModal(false)}
                className="px-4 py-2 rounded-lg font-medium transition-colors duration-200"
                style={{
                  background: '#f0f0f0',
                  color: '#666',
                  boxShadow: '4px 4px 8px #e0e0e0, -4px -4px 8px #ffffff'
                }}
              >
                Close
              </button>
              <button
                onClick={() => {
                  setShowErrorModal(false)
                  manualInputRef.current?.focus()
                }}
                className="px-4 py-2 rounded-lg font-medium text-white transition-colors duration-200"
                style={{
                  background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)',
                  boxShadow: '4px 4px 8px #d0d0d0, -4px -4px 8px #ffffff'
                }}
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
