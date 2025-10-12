"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import CardNav from "@/components/CardNav";

export default function IRISAnalyticsDashboard() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCompany, setSelectedCompany] = useState('');
  const [comparisonCompanies, setComparisonCompanies] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Handle analyze button click
  const handleAnalyze = async () => {
    if (!selectedCompany.trim()) {
      setError('Please enter a company name or symbol');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Call forensic analysis API
      const response = await fetch(`/api/forensic-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol: selectedCompany.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysisData(data);
      console.log('Analysis completed:', data);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze company. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle company comparison
  const handleCompare = async () => {
    if (comparisonCompanies.length < 2) {
      setError('Please select at least 2 companies to compare');
      return;
    }

    setIsComparing(true);
    setError(null);

    try {
      const comparisonResults = [];

      for (const company of comparisonCompanies) {
        const response = await fetch(`/api/forensic-analysis`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ symbol: company.trim() }),
        });

        if (response.ok) {
          const data = await response.json();
          comparisonResults.push({
            symbol: company,
            data: data
          });
        } else {
          console.error(`Failed to analyze ${company}`);
        }
      }

      setComparisonData(comparisonResults);
      console.log('Comparison completed:', comparisonResults);
    } catch (err: any) {
      setError(err.message || 'Failed to compare companies. Please try again.');
      console.error('Comparison error:', err);
    } finally {
      setIsComparing(false);
    }
  };

  // Add company to comparison
  const addToComparison = (company: string) => {
    if (company && !comparisonCompanies.includes(company) && comparisonCompanies.length < 4) {
      setComparisonCompanies([...comparisonCompanies, company]);
    }
  };

  // Handle clear button click
  const handleClear = () => {
    setSelectedCompany('');
    setAnalysisData(null);
    setComparisonData([]);
    setComparisonCompanies([]);
    setError(null);
  };

  // Remove company from comparison
  const removeFromComparison = (company: string) => {
    setComparisonCompanies(comparisonCompanies.filter(c => c !== company));
  };

  const navItems = [
    {
      label: "Analytics",
      bgColor: "#7B68EE",
      textColor: "#ffffff",
      links: [
        { label: "Overview", href: "#overview", ariaLabel: "Overview Dashboard" },
        { label: "Forensic", href: "#forensic", ariaLabel: "Forensic Analysis" },
        { label: "Risk", href: "#risk", ariaLabel: "Risk Assessment" },
        { label: "Compliance", href: "#compliance", ariaLabel: "Compliance Check" },
        { label: "Reports", href: "#reports", ariaLabel: "Reports" }
      ]
    },
    {
      label: "Actions",
      bgColor: "#FF6B9D",
      textColor: "#ffffff",
      links: [
        { label: "Export Data", href: "#export", ariaLabel: "Export Data" },
        { label: "Compare", href: "#compare", ariaLabel: "Compare Companies" },
        { label: "Settings", href: "#settings", ariaLabel: "Settings" }
      ]
    }
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f0f0f0' }}>
      {/* Enhanced Gradient Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 opacity-30 pointer-events-none"></div>

      <style jsx>{`
        .neumorphic-card {
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          overflow: hidden;
        }
        .neumorphic-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
          border-radius: inherit;
          pointer-events: none;
        }
        .neumorphic-card:hover {
          transform: translateY(-4px) scale(1.02);
          box-shadow: 16px 16px 32px #d0d0d0, -16px -16px 32px #ffffff;
        }
        .neumorphic-button {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .neumorphic-button:hover {
          transform: translateY(-2px);
          box-shadow: 6px 6px 12px #d0d0d0, -6px -6px 12px #ffffff;
        }
        .glass-morphism {
          background: rgba(255, 255, 255, 0.25);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.18);
        }
        .animated-gradient {
          background: linear-gradient(-45deg, #f2a09e, #e89694, #7B68EE, #FF6B9D);
          background-size: 400% 400%;
          animation: gradientShift 15s ease infinite;
        }
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .sidebar {
          position: fixed;
          left: 0;
          top: 0;
          bottom: 0;
          width: 280px;
          z-index: 40;
          transform: translateX(0);
          transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        }
        .main-content {
          margin-left: 280px;
          min-height: 100vh;
        }
        @media (max-width: 768px) {
          .sidebar {
            transform: translateX(-100%);
          }
          .main-content {
            margin-left: 0;
          }
        }
        .pulse-animation {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>

      {/* Sidebar Navigation */}
      <div className="sidebar neumorphic-card" style={{ background: '#f0f0f0', boxShadow: '8px 0 16px #d0d0d0, -8px 0 16px #ffffff' }}>
        <div className="p-6 h-full flex flex-col">
          {/* Sidebar Header */}
          <div className="mb-8">
            <h1 className="text-xl font-bold mb-2" style={{ color: '#333' }}>IRIS Analytics</h1>
            <p className="text-sm" style={{ color: '#666' }}>Financial Forensics Platform</p>
          </div>

          {/* Navigation Tabs */}
          <div className="flex-1 space-y-2">
            {['Overview', 'Forensic', 'Risk', 'Compliance', 'Reports'].map((item) => (
              <button
                key={item}
                onClick={() => setActiveTab(item.toLowerCase())}
                className={`w-full text-left px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === item.toLowerCase() ? 'neumorphic-button' : ''
                }`}
                style={
                  activeTab === item.toLowerCase()
                    ? { background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)', boxShadow: '4px 4px 8px #d89592, -4px -4px 8px #ffcfc8', color: '#fff' }
                    : { color: '#666' }
                }
              >
                {item}
              </button>
            ))}
          </div>

          {/* Sidebar Actions */}
          <div className="space-y-2 mt-8">
            <button
              className="w-full px-4 py-3 rounded-xl font-medium transition-all neumorphic-button"
              style={{ background: '#f0f0f0', boxShadow: '4px 4px 8px #d0d0d0, -4px -4px 8px #ffffff', color: '#666' }}
            >
              Export Data
            </button>
            <button
              onClick={() => router.push('/')}
              className="w-full px-4 py-3 rounded-xl font-medium transition-all neumorphic-button"
              style={{ background: '#f0f0f0', boxShadow: '4px 4px 8px #d0d0d0, -4px -4px 8px #ffffff', color: '#666' }}
            >
              ← Home
            </button>
          </div>
        </div>
      </div>

      {/* Home Page Navbar */}
      <div className="relative z-50">
        <CardNav
          logo="/logo.svg"
          logoAlt="FinanceHub Logo"
          items={navItems}
          className="-mt-2"
          baseColor="#f0f0f0"
          menuColor="#f2a09e"
          buttonBgColor="#f2a09e"
          buttonTextColor="#ffffff"
        />
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="max-w-7xl mx-auto px-6 pt-0 pb-4">
          {/* Search & Filter Section */}
          <div className="mb-8 mt-8">
            <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(20px)',
              boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)'
            }}>
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-1">
                  <label className="block text-sm font-semibold mb-3" style={{ color: '#1e293b' }}>Company Analysis</label>
                  <div className="relative">
                    <input
                      type="text"
                      value={selectedCompany}
                      onChange={(e) => setSelectedCompany(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                      placeholder="Enter NSE/BSE symbol (e.g., RELIANCE.NS, TCS.NS)"
                      className="w-full px-6 py-4 rounded-2xl text-base font-medium transition-all duration-300"
                      style={{
                        background: 'rgba(255, 255, 255, 0.9)',
                        boxShadow: 'inset 8px 8px 16px rgba(0,0,0,0.1), inset -8px -8px 16px rgba(255,255,255,0.9)',
                        border: 'none',
                        outline: 'none',
                        color: '#1e293b'
                      }}
                      disabled={isAnalyzing}
                    />
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <div className={`w-2 h-2 rounded-full ${isAnalyzing ? 'bg-blue-500 pulse-animation' : 'bg-gray-300'}`}></div>
                    </div>
                  </div>
                  {error && (
                    <p className="text-sm mt-3 font-medium" style={{ color: '#ef4444' }}>{error}</p>
                  )}
                </div>
                <div className="flex gap-4 items-end">
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || !selectedCompany.trim()}
                    className="px-8 py-4 rounded-2xl font-bold text-white transition-all neumorphic-button animated-gradient"
                    style={{
                      background: isAnalyzing ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' : 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)',
                      boxShadow: '8px 8px 16px rgba(242, 160, 158, 0.3), -8px -8px 16px rgba(255, 255, 255, 0.8)',
                      cursor: isAnalyzing || !selectedCompany.trim() ? 'not-allowed' : 'pointer',
                      opacity: isAnalyzing || !selectedCompany.trim() ? 0.7 : 1,
                      minWidth: '140px'
                    }}
                  >
                    {isAnalyzing ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        Analyzing...
                      </div>
                    ) : (
                      '🚀 Analyze'
                    )}
                  </button>
                  <button
                    onClick={handleClear}
                    disabled={isAnalyzing}
                    className="px-6 py-4 rounded-2xl font-semibold transition-all neumorphic-button"
                    style={{
                      background: 'rgba(255, 255, 255, 0.9)',
                      boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
                      color: '#64748b',
                      cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                      opacity: isAnalyzing ? 0.6 : 1
                    }}
                  >
                    Clear
                  </button>
                  {analysisData && (
                    <button
                      onClick={() => addToComparison(selectedCompany)}
                      disabled={comparisonCompanies.includes(selectedCompany) || comparisonCompanies.length >= 4}
                      className="px-6 py-4 rounded-2xl font-semibold transition-all neumorphic-button"
                      style={{
                        background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)',
                        boxShadow: '8px 8px 16px rgba(123, 104, 238, 0.3), -8px -8px 16px rgba(255, 255, 255, 0.8)',
                        color: '#fff',
                        cursor: (comparisonCompanies.includes(selectedCompany) || comparisonCompanies.length >= 4) ? 'not-allowed' : 'pointer',
                        opacity: (comparisonCompanies.includes(selectedCompany) || comparisonCompanies.length >= 4) ? 0.6 : 1
                      }}
                    >
                      ➕ Compare
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Company Comparison Section */}
          {comparisonCompanies.length > 0 && (
            <div className="mb-8">
              <div className="neumorphic-card rounded-3xl p-6 glass-morphism" style={{
                background: 'rgba(255, 255, 255, 0.8)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)'
              }}>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold" style={{ color: '#1e293b' }}>Company Comparison</h3>
                    <p className="text-sm font-medium" style={{ color: '#64748b' }}>
                      {comparisonCompanies.length} companies selected for comparison
                    </p>
                  </div>
                  <button
                    onClick={handleCompare}
                    disabled={isComparing || comparisonCompanies.length < 2}
                    className="px-6 py-3 rounded-2xl font-bold text-white transition-all neumorphic-button"
                    style={{
                      background: isComparing ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' : 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)',
                      boxShadow: '8px 8px 16px rgba(123, 104, 238, 0.3), -8px -8px 16px rgba(255, 255, 255, 0.8)',
                      cursor: isComparing || comparisonCompanies.length < 2 ? 'not-allowed' : 'pointer',
                      opacity: isComparing || comparisonCompanies.length < 2 ? 0.7 : 1
                    }}
                  >
                    {isComparing ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Comparing...
                      </div>
                    ) : (
                      '📊 Compare'
                    )}
                  </button>
                </div>

                {/* Selected Companies */}
                <div className="flex flex-wrap gap-3 mb-4">
                  {comparisonCompanies.map((company, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 px-4 py-2 rounded-xl"
                      style={{
                        background: 'rgba(255, 255, 255, 0.9)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.1), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '1px solid rgba(123, 104, 238, 0.2)'
                      }}
                    >
                      <span className="font-semibold" style={{ color: '#1e293b' }}>{company}</span>
                      <button
                        onClick={() => removeFromComparison(company)}
                        className="text-red-500 hover:text-red-700 text-lg font-bold"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>

                {/* Add Company to Comparison */}
                {comparisonCompanies.length < 4 && (
                  <div className="flex gap-3">
                    <input
                      type="text"
                      placeholder="Add company symbol..."
                      className="flex-1 px-4 py-2 rounded-xl"
                      style={{
                        background: 'rgba(255, 255, 255, 0.9)',
                        boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.1), inset -6px -6px 12px rgba(255,255,255,0.9)',
                        border: 'none',
                        outline: 'none',
                        color: '#1e293b'
                      }}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          const target = e.target as HTMLInputElement;
                          if (target.value.trim()) {
                            addToComparison(target.value.trim());
                            target.value = '';
                          }
                        }
                      }}
                    />
                    <button
                      onClick={(e) => {
                        const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                        if (input?.value.trim()) {
                          addToComparison(input.value.trim());
                          input.value = '';
                        }
                      }}
                      className="px-4 py-2 rounded-xl font-semibold transition-all neumorphic-button"
                      style={{
                        background: 'rgba(255, 255, 255, 0.9)',
                        boxShadow: '6px 6px 12px rgba(0,0,0,0.1), -6px -6px 12px rgba(255,255,255,0.9)',
                        color: '#7B68EE'
                      }}
                    >
                      + Add
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
          {isAnalyzing && (
            <div className="mb-6">
              <div className="neumorphic-card rounded-3xl p-8 text-center" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 mx-auto mb-4" style={{ borderColor: '#f2a09e' }}></div>
                <h3 className="text-xl font-bold mb-2" style={{ color: '#333' }}>Analyzing {selectedCompany}...</h3>
                <p className="text-sm" style={{ color: '#666' }}>Running forensic analysis and risk assessment</p>
              </div>
            </div>
          )}

          {/* Stats Grid */}
          {analysisData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              {[
                { 
                  label: 'Risk Score', 
                  value: `${analysisData.risk_assessment?.overall_risk_score || 'N/A'}/100`, 
                  color: '#FF6B9D', 
                  icon: '⚠️' 
                },
                { 
                  label: 'Forensic Metrics', 
                  value: '29', 
                  color: '#7B68EE', 
                  icon: '🔍' 
                },
                { 
                  label: 'Anomalies Found', 
                  value: analysisData.anomaly_detection?.anomalies_detected || '0', 
                  color: '#f2a09e', 
                  icon: '🚨' 
                },
                { 
                  label: 'Compliance', 
                  value: `${analysisData.compliance_assessment?.overall_compliance_score || 'N/A'}%`, 
                  color: '#4ade80', 
                  icon: '✓' 
                },
              ].map((stat, index) => (
              <div
                key={index}
                className="neumorphic-card rounded-3xl p-6 group"
                style={{
                  background: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(10px)',
                  boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)',
                  border: `2px solid ${stat.color}20`
                }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl"
                      style={{
                        background: `linear-gradient(135deg, ${stat.color}, ${stat.color}dd)`,
                        boxShadow: `0 0 20px ${stat.color}40`
                      }}
                    >
                      {stat.icon}
                    </div>
                    <div>
                      <p className="text-sm font-medium" style={{ color: '#64748b' }}>{stat.label}</p>
                      <p className="text-2xl font-bold" style={{ color: '#1e293b' }}>{stat.value}</p>
                    </div>
                  </div>
                  <div
                    className="w-4 h-4 rounded-full opacity-60 group-hover:opacity-100 transition-opacity"
                    style={{ background: stat.color }}
                  ></div>
                </div>
                <div className="w-full h-1 rounded-full overflow-hidden" style={{ background: `${stat.color}20` }}>
                  <div
                    className="h-full rounded-full transition-all duration-1000"
                    style={{
                      width: stat.label === 'Risk Score' ? `${Math.min((parseFloat(stat.value.split('/')[0]) || 0), 100)}%` : '100%',
                      background: `linear-gradient(90deg, ${stat.color}, ${stat.color}aa)`
                    }}
                  ></div>
                </div>
              </div>
            ))}
            </div>
          )}

          {/* Main Analysis Section */}
          {analysisData && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Forensic Analysis Card */}
            <div
              className="neumorphic-card rounded-3xl p-8 lg:col-span-2 group"
              style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(15px)',
                boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)',
                border: '2px solid rgba(123, 104, 238, 0.2)'
              }}
            >
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Forensic Analysis</h2>
                  <p className="text-sm font-medium" style={{ color: '#64748b' }}>29 comprehensive financial metrics</p>
                </div>
                <button
                  className="px-6 py-3 rounded-2xl text-sm font-semibold transition-all neumorphic-button"
                  style={{
                    background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)',
                    boxShadow: '6px 6px 12px rgba(123, 104, 238, 0.3), -6px -6px 12px rgba(255, 255, 255, 0.8)',
                    color: '#fff'
                  }}
                >
                  📊 View Details
                </button>
              </div>

              {/* Metrics List */}
              <div className="space-y-4">
                {[
                  { 
                    name: 'Altman Z-Score', 
                    value: analysisData.altman_z_score?.altman_z_score?.z_score || 'N/A', 
                    status: analysisData.altman_z_score?.altman_z_score?.classification || 'Unknown', 
                    color: analysisData.altman_z_score?.altman_z_score?.risk_level === 'LOW' ? '#4ade80' : '#FF6B9D' 
                  },
                  { 
                    name: 'Beneish M-Score', 
                    value: analysisData.beneish_m_score?.beneish_m_score?.m_score || 'N/A', 
                    status: analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? 'Risk' : 'Safe', 
                    color: analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? '#FF6B9D' : '#4ade80' 
                  },
                  { 
                    name: 'Debt to Equity', 
                    value: analysisData.financial_ratios?.financial_ratios?.['2025-03-31']?.debt_to_equity || 'N/A', 
                    status: 'Good', 
                    color: '#4ade80' 
                  },
                  { 
                    name: 'Current Ratio', 
                    value: '1.32', 
                    status: 'Moderate', 
                    color: '#7B68EE' 
                  },
                ].map((metric, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-6 rounded-2xl group"
                    style={{
                      background: 'rgba(255, 255, 255, 0.7)',
                      boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.05), inset -6px -6px 12px rgba(255,255,255,0.9)',
                      border: `1px solid ${metric.color}20`
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center"
                        style={{
                          background: `linear-gradient(135deg, ${metric.color}, ${metric.color}dd)`,
                          boxShadow: `0 0 15px ${metric.color}30`
                        }}
                      >
                        <span className="text-white font-bold text-sm">
                          {metric.name.split(' ')[0].charAt(0)}
                        </span>
                      </div>
                      <div>
                        <p className="font-bold text-base mb-1" style={{ color: '#1e293b' }}>{metric.name}</p>
                        <span className="text-xs px-3 py-1 rounded-full font-medium" style={{
                          background: `${metric.color}15`,
                          color: metric.color,
                          border: `1px solid ${metric.color}30`
                        }}>
                          {metric.status}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-3xl font-bold" style={{ color: metric.color }}>{metric.value}</span>
                      <div className="w-16 h-1 rounded-full mt-2" style={{ background: `${metric.color}20` }}>
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: metric.name.includes('Z-Score') ? '85%' : '70%',
                            background: `linear-gradient(90deg, ${metric.color}, ${metric.color}aa)`
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Assessment Card */}
            <div
              className="neumorphic-card rounded-3xl p-8"
              style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(15px)',
                boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)',
                border: '2px solid rgba(255, 107, 157, 0.2)'
              }}
            >
              <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Risk Assessment</h2>
              <p className="text-sm font-medium mb-8" style={{ color: '#64748b' }}>6-category weighted analysis</p>

              {/* Risk Score Circle */}
              <div className="flex items-center justify-center mb-8">
                <div
                  className="w-48 h-48 rounded-full flex items-center justify-center relative"
                  style={{
                    background: 'linear-gradient(135deg, #FF6B9D 0%, #FF4081 100%)',
                    boxShadow: '12px 12px 24px rgba(255, 107, 157, 0.3), -12px -12px 24px rgba(255, 255, 255, 0.2)'
                  }}
                >
                  <div
                    className="w-40 h-40 rounded-full flex flex-col items-center justify-center relative"
                    style={{
                      background: 'rgba(255, 255, 255, 0.95)',
                      boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.1), inset -6px -6px 12px rgba(255,255,255,0.9)'
                    }}
                  >
                    <span className="text-5xl font-bold mb-1" style={{ color: '#FF6B9D' }}>
                      {analysisData.risk_assessment?.overall_risk_score || 'N/A'}
                    </span>
                    <span className="text-sm font-semibold" style={{ color: '#64748b' }}>Risk Score</span>
                    <div className="absolute -top-2 -right-2">
                      <div className="w-6 h-6 rounded-full bg-white shadow-lg flex items-center justify-center">
                        <span className="text-xs">💯</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Risk Categories */}
              <div className="space-y-3">
                {Object.entries(analysisData.risk_assessment?.category_scores || {}).slice(0, 4).map(([category, data]: [string, any], index) => ({
                  category: category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                  level: Math.round(data.score || 0)
                })).map((item, index) => (
                  <div key={index} className="group">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="font-semibold" style={{ color: '#1e293b' }}>{item.category}</span>
                      <span className="font-bold" style={{ color: '#64748b' }}>{item.level}%</span>
                    </div>
                    <div
                      className="h-3 rounded-full overflow-hidden relative"
                      style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.1), inset -2px -2px 4px rgba(255,255,255,0.9)'
                      }}
                    >
                      <div
                        className="h-full rounded-full transition-all duration-1500 ease-out relative overflow-hidden"
                        style={{
                          width: `${item.level}%`,
                          background: item.level > 70 ? 'linear-gradient(90deg, #FF6B9D, #FF4081)' : item.level > 50 ? 'linear-gradient(90deg, #7B68EE, #6A5ACD)' : 'linear-gradient(90deg, #4ade80, #22c55e)'
                        }}
                      >
                        <div
                          className="absolute inset-0 opacity-30"
                          style={{
                            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)'
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            </div>
          )}

          {/* Company Comparison Results */}
          {comparisonData.length > 0 && (
            <div className="mb-8">
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(15px)',
                boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)',
                border: '2px solid rgba(123, 104, 238, 0.2)'
              }}>
                <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Company Comparison</h2>
                <p className="text-sm font-medium mb-8" style={{ color: '#64748b' }}>
                  Side-by-side analysis of {comparisonData.length} companies
                </p>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold" style={{ color: '#1e293b' }}>Risk Assessment</h3>
                    {comparisonData.map((company, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-2xl"
                           style={{
                             background: 'rgba(255, 255, 255, 0.7)',
                             boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                             border: '1px solid rgba(123, 104, 238, 0.2)'
                           }}>
                        <div>
                          <p className="font-bold" style={{ color: '#1e293b' }}>{company.symbol}</p>
                          <p className="text-sm" style={{ color: '#64748b' }}>
                            {company.data.risk_assessment?.risk_level || 'Unknown'} Risk
                          </p>
                        </div>
                        <span className="text-2xl font-bold" style={{ color: '#FF6B9D' }}>
                          {company.data.risk_assessment?.overall_risk_score || 'N/A'}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-xl font-bold" style={{ color: '#1e293b' }}>Compliance Status</h3>
                    {comparisonData.map((company, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-2xl"
                           style={{
                             background: 'rgba(255, 255, 255, 0.7)',
                             boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                             border: '1px solid rgba(34, 197, 94, 0.2)'
                           }}>
                        <div>
                          <p className="font-bold" style={{ color: '#1e293b' }}>{company.symbol}</p>
                          <p className="text-sm" style={{ color: '#64748b' }}>
                            {company.data.compliance_assessment?.compliance_status?.replace(/_/g, ' ') || 'Unknown'}
                          </p>
                        </div>
                        <span className="text-2xl font-bold" style={{ color: '#4ade80' }}>
                          {company.data.compliance_assessment?.overall_compliance_score || 'N/A'}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Anomaly Detection Section */}
          {analysisData && (
            <div
            className="neumorphic-card rounded-3xl p-8 mb-8"
            style={{
              background: 'rgba(255, 255, 255, 0.9)',
              backdropFilter: 'blur(15px)',
              boxShadow: '16px 16px 32px rgba(0,0,0,0.1), -16px -16px 32px rgba(255,255,255,0.9)',
              border: '2px solid rgba(34, 197, 94, 0.2)'
            }}
          >
            <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Anomaly Detection</h2>
            <p className="text-sm font-medium mb-8" style={{ color: '#64748b' }}>Advanced fraud detection algorithms</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  title: "Benford's Law Analysis",
                  status: analysisData.benford_analysis?.benford_analysis?.interpretation || 'Normal',
                  severity: analysisData.benford_analysis?.benford_analysis?.is_anomalous ? 'High' : 'Low',
                  color: analysisData.benford_analysis?.benford_analysis?.is_anomalous ? '#FF6B9D' : '#4ade80'
                },
                {
                  title: 'Revenue Pattern',
                  status: 'Normal',
                  severity: 'Low',
                  color: '#4ade80'
                },
                {
                  title: 'Expense Irregularities',
                  status: 'Review Required',
                  severity: 'Medium',
                  color: '#7B68EE'
                },
              ].map((anomaly, index) => (
                <div
                  key={index}
                  className="p-6 rounded-2xl group"
                  style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.05), inset -6px -6px 12px rgba(255,255,255,0.9)',
                    border: `2px solid ${anomaly.color}20`,
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="font-bold text-lg mb-2" style={{ color: '#1e293b' }}>{anomaly.title}</h3>
                    <div
                      className="w-4 h-4 rounded-full mt-1 group-hover:scale-110 transition-transform"
                      style={{
                        background: anomaly.color,
                        boxShadow: `0 0 12px ${anomaly.color}40`
                      }}
                    ></div>
                  </div>
                  <p className="text-sm mb-3 font-medium" style={{ color: '#64748b' }}>{anomaly.status}</p>
                  <span
                    className="text-xs px-3 py-2 rounded-full font-bold"
                    style={{
                      background: `linear-gradient(135deg, ${anomaly.color}, ${anomaly.color}dd)`,
                      color: '#fff',
                      boxShadow: `0 0 8px ${anomaly.color}30`
                    }}
                  >
                    {anomaly.severity} Risk
                  </span>
                </div>
              ))}
            </div>
            </div>
          )}

          {/* Quick Actions */}
          {analysisData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Generate Report',
                icon: '📄',
                color: '#f2a09e',
                description: 'PDF & Excel reports'
              },
              {
                title: 'Compare Companies',
                icon: '📊',
                color: '#7B68EE',
                description: 'Benchmark analysis'
              },
              {
                title: 'Export Data',
                icon: '💾',
                color: '#FF6B9D',
                description: 'Raw data export'
              },
            ].map((action, index) => (
              <button
                key={index}
                className="neumorphic-card rounded-3xl p-8 text-left transition-all cursor-pointer group relative overflow-hidden"
                style={{
                  background: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(10px)',
                  boxShadow: '12px 12px 24px rgba(0,0,0,0.1), -12px -12px 24px rgba(255,255,255,0.9)',
                  border: `2px solid ${action.color}20`
                }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 rounded-full opacity-10 group-hover:opacity-20 transition-opacity"
                     style={{ background: `radial-gradient(circle, ${action.color}, transparent)` }}></div>

                <div className="relative z-10">
                  <div className="flex items-center gap-4 mb-4">
                    <div
                      className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform"
                      style={{
                        background: `linear-gradient(135deg, ${action.color}, ${action.color}dd)`,
                        boxShadow: `0 0 20px ${action.color}40`
                      }}
                    >
                      {action.icon}
                    </div>
                    <div>
                      <span className="font-bold text-xl block mb-1" style={{ color: '#1e293b' }}>{action.title}</span>
                      <span className="text-sm font-medium" style={{ color: '#64748b' }}>{action.description}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold" style={{ color: action.color }}>
                      Click to proceed →
                    </span>
                    <div className="w-8 h-8 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
                         style={{ background: `${action.color}20` }}>
                      <span className="text-sm" style={{ color: action.color }}>⚡</span>
                    </div>
                  </div>
                </div>
              </button>
            ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
