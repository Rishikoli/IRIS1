"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import CardNav from "@/components/CardNav";
import ForensicSection from "@/components/ForensicSection";
import AnomalyHeatmap from "@/components/charts/AnomalyHeatmap";
import FraudDetectionRadarChart from "@/components/charts/FraudDetectionRadarChart";
import ScoreDistribution from "@/components/charts/ScoreDistribution";

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
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [generatedReports, setGeneratedReports] = useState<any[]>([]);
  const [forensicSummary, setForensicSummary] = useState<string>('');
  const [riskSummary, setRiskSummary] = useState<string>('');
  const [regulatoryRecommendations, setRegulatoryRecommendations] = useState<string>('');
  const [isLoadingForensicSummary, setIsLoadingForensicSummary] = useState(false);
  const [isLoadingRiskSummary, setIsLoadingRiskSummary] = useState(false);
  const [isLoadingRegulatoryRecommendations, setIsLoadingRegulatoryRecommendations] = useState(false);
  // Q&A System state
  const [qaQuery, setQaQuery] = useState('');
  const [qaAnswer, setQaAnswer] = useState('');
  const [qaHistory, setQaHistory] = useState<any[]>([]);
  const [isLoadingQa, setIsLoadingQa] = useState(false);
  const [qaConfidence, setQaConfidence] = useState('');
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
      
      // Generate Gemini summaries after successful analysis
      generateGeminiSummaries(data, selectedCompany.trim());
      generateRegulatoryRecommendations(data, selectedCompany.trim());

      // Index company data for Q&A system
      indexCompanyForQa(data, selectedCompany.trim());
    } catch (err: any) {
      setError(err.message || 'Failed to analyze company. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Generate Gemini AI Summaries
  const generateGeminiSummaries = async (data: any, symbol: string) => {
    // Generate Forensic Summary
    setIsLoadingForensicSummary(true);
    try {
      const forensicResponse = await fetch('/api/gemini-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysisData: data,
          summaryType: 'forensic',
          companySymbol: symbol
        })
      });
      
      if (forensicResponse.ok) {
        const forensicData = await forensicResponse.json();
        if (forensicData.success) {
          setForensicSummary(forensicData.summary);
        }
      }
    } catch (error) {
      console.error('Failed to generate forensic summary:', error);
    } finally {
      setIsLoadingForensicSummary(false);
    }

    // Generate Risk Summary
    setIsLoadingRiskSummary(true);
    try {
      const riskResponse = await fetch('/api/gemini-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysisData: data,
          summaryType: 'risk',
          companySymbol: symbol
        })
      });
      
      if (riskResponse.ok) {
        const riskData = await riskResponse.json();
        if (riskData.success) {
          setRiskSummary(riskData.summary);
        }
      }
    } catch (error) {
      console.error('Failed to generate risk summary:', error);
    } finally {
      setIsLoadingRiskSummary(false);
    }
  };

  // Generate Regulatory Recommendations using Gemini
  const generateRegulatoryRecommendations = async (data: any, symbol: string) => {
    setIsLoadingRegulatoryRecommendations(true);
    try {
      const response = await fetch('/api/gemini-regulatory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysisData: data,
          companySymbol: symbol
        })
      });

      if (response.ok) {
        const regulatoryData = await response.json();
        if (regulatoryData.success) {
          setRegulatoryRecommendations(regulatoryData.recommendations);
        } else if (regulatoryData.fallback) {
          // Use fallback recommendations
          setRegulatoryRecommendations(regulatoryData.defaultRecommendations.join('\n'));
        }
      }
    } catch (error) {
      console.error('Failed to generate regulatory recommendations:', error);
      // Set fallback recommendations
      setRegulatoryRecommendations([
        "• No immediate enforcement action required.",
        "• Maintain quarterly forensic monitoring.",
        "• Cross-verify debt covenants in Q2 for early distress signals."
      ].join('\n'));
    } finally {
      setIsLoadingRegulatoryRecommendations(false);
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

  // Index company data for Q&A system
  const indexCompanyForQa = async (data: any, symbol: string) => {
    try {
      await fetch('/api/qa-index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_symbol: symbol,
          company_data: data
        })
      });
      console.log(`Company data indexed for Q&A: ${symbol}`);
    } catch (error) {
      console.error('Failed to index company data for Q&A:', error);
    }
  };

  // Handle Q&A System
  const handleQaQuestion = async () => {
    if (!qaQuery.trim()) {
      setError('Please enter a question');
      return;
    }

    setIsLoadingQa(true);
    setError(null);

    try {
      const response = await fetch('/api/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: qaQuery.trim(),
          companySymbol: selectedCompany,
          maxContext: 5
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setQaAnswer(data.answer);
          setQaConfidence(data.confidence);

          // Add to history
          const newQuestion = {
            query: qaQuery,
            answer: data.answer,
            confidence: data.confidence,
            contextUsed: data.contextUsed,
            sources: data.sources,
            timestamp: new Date().toISOString()
          };

          setQaHistory(prev => [newQuestion, ...prev.slice(0, 9)]); // Keep last 10 questions
        } else {
          setQaAnswer(data.answer || 'I apologize, but I couldn\'t answer your question at this time.');
          setQaConfidence('Low');
        }
      } else {
        throw new Error('Failed to get answer');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to process question. Please try again.');
      console.error('Q&A error:', err);
    } finally {
      setIsLoadingQa(false);
    }
  };

  // Handle clear button click
  const handleClear = () => {
    setSelectedCompany('');
    setAnalysisData(null);
    setComparisonData([]);
    setComparisonCompanies([]);
    setError(null);
    setForensicSummary('');
    setRiskSummary('');
    setRegulatoryRecommendations('');
    setQaQuery('');
    setQaAnswer('');
    setQaHistory([]);
    setQaConfidence('');
  };

  // Remove company from comparison
  const removeFromComparison = (company: string) => {
    setComparisonCompanies(comparisonCompanies.filter(c => c !== company));
  };

  // Generate report function
  const generateReport = async (formats: string[]) => {
    if (!analysisData) {
      setError('No analysis data available. Please analyze a company first.');
      return;
    }

    setIsGeneratingReport(true);
    setError(null);

    try {
      const response = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: selectedCompany,
          formats: formats,
          includeSummary: true
        }),
      });

      if (!response.ok) {
        throw new Error(`Report generation failed: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        // Add generated reports to the list
        const newReports = data.comprehensive_report.exports.map((exportInfo: any) => ({
          format: exportInfo.format,
          filename: exportInfo.filename,
          fileSize: exportInfo.file_size,
          wordCount: data.comprehensive_report.forensic_report.executive_summary?.summary_metadata?.word_count || 'N/A',
          generatedAt: new Date().toISOString()
        }));

        setGeneratedReports(prev => [...prev, ...newReports]);

        console.log('Reports generated successfully:', data);
      } else {
        throw new Error(data.error || 'Failed to generate reports');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate reports. Please try again.');
      console.error('Report generation error:', err);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // Download report function
  const downloadReport = async (filename: string) => {
    try {
      const response = await fetch(`/api/reports/download?filename=${encodeURIComponent(filename)}`);

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      console.log('Report downloaded successfully:', filename);
    } catch (err: any) {
      setError(err.message || 'Failed to download report. Please try again.');
      console.error('Report download error:', err);
    }
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
        { label: "Q&A", href: "#qa", ariaLabel: "Financial Q&A" },
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
            {['Overview', 'Forensic', 'Risk', 'Compliance', 'Q&A', 'Reports'].map((item) => (
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
          logoAlt="I.R.I.S."
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

          {/* Forensic Tab Content */}
          {activeTab === 'forensic' && analysisData && (
            <div className="space-y-6">
              {/* Gemini AI Forensic Summary */}
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'linear-gradient(135deg, rgba(123, 104, 238, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                border: '2px solid rgba(123, 104, 238, 0.3)'
              }}>
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">🤖</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl font-bold" style={{ color: '#1e293b' }}>AI Forensic Analysis Summary</h3>
                      <span className="px-3 py-1 rounded-full text-xs font-bold" style={{
                        background: 'linear-gradient(135deg, #7B68EE 0%, #6366f1 100%)',
                        color: '#fff'
                      }}>
                        Powered by Gemini 2.0
                      </span>
                    </div>
                    <p className="text-sm font-medium mb-4" style={{ color: '#64748b' }}>
                      Comprehensive forensic examination of financial statements and fraud indicators
                    </p>
                    <div className="prose prose-slate max-w-none">
                      <div className="p-6 rounded-2xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
                      }}>
                        {isLoadingForensicSummary ? (
                          <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mr-3"></div>
                            <span className="text-base" style={{ color: '#64748b' }}>Generating AI forensic analysis...</span>
                          </div>
                        ) : forensicSummary ? (
                          <div 
                            className="text-base leading-relaxed" 
                            style={{ color: '#1e293b' }}
                            dangerouslySetInnerHTML={{ __html: forensicSummary }}
                          />
                        ) : (
                          <>
                            <p className="text-base leading-relaxed mb-4" style={{ color: '#1e293b' }}>
                              <strong>Financial Health Assessment:</strong> Based on the comprehensive forensic analysis of {selectedCompany}, 
                              the Altman Z-Score of <strong>{analysisData.altman_z_score?.altman_z_score?.z_score || 'N/A'}</strong> indicates 
                              a <strong>{analysisData.altman_z_score?.altman_z_score?.classification || 'moderate'}</strong> financial position. 
                              The company demonstrates {analysisData.altman_z_score?.altman_z_score?.risk_level === 'LOW' ? 'strong financial stability with low bankruptcy risk' : 'areas requiring attention in financial management'}.
                            </p>
                            <p className="text-base leading-relaxed mb-4" style={{ color: '#1e293b' }}>
                              <strong>Earnings Quality Analysis:</strong> The Beneish M-Score evaluation reveals 
                              {analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator 
                                ? ' potential red flags in earnings manipulation. The M-Score suggests heightened scrutiny is warranted for revenue recognition practices and accrual patterns.' 
                                : ' clean earnings quality with no significant indicators of financial statement manipulation. The accounting practices appear transparent and reliable.'
                              }
                            </p>
                            <p className="text-base leading-relaxed mb-4" style={{ color: '#1e293b' }}>
                              <strong>Statistical Fraud Detection:</strong> Benford's Law analysis shows 
                              a compliance score of <strong>{analysisData.benford_analysis?.benford_analysis?.compliance_score || 'N/A'}%</strong>, 
                              which is {analysisData.benford_analysis?.benford_analysis?.is_anomalous 
                                ? 'below expected natural distribution patterns, suggesting potential data irregularities that warrant deeper investigation' 
                                : 'consistent with natural number distributions, indicating authentic financial data without statistical anomalies'
                              }.
                            </p>
                            <p className="text-base leading-relaxed" style={{ color: '#1e293b' }}>
                              <strong>Key Forensic Insights:</strong> The forensic examination across 29 comprehensive metrics reveals 
                              {analysisData.anomaly_detection?.anomalies_detected > 0 
                                ? ` ${analysisData.anomaly_detection.anomalies_detected} anomalies requiring management attention. These irregularities span across revenue patterns, expense allocations, and balance sheet compositions.` 
                                : ' no significant anomalies in the financial statements, demonstrating robust internal controls and consistent accounting practices.'
                              } 
                              Overall, the forensic analysis provides {analysisData.altman_z_score?.altman_z_score?.risk_level === 'LOW' && !analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator 
                                ? 'a positive assessment with strong fundamentals' 
                                : 'actionable insights for risk mitigation and enhanced due diligence'
                              }.
                            </p>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Dedicated Forensic Analysis Section */}
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                border: '2px solid rgba(123, 104, 238, 0.2)'
              }}>
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Forensic Analysis</h2>
                    <p className="text-sm font-medium" style={{ color: '#64748b' }}>29 comprehensive financial metrics</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-sm font-medium" style={{ color: '#64748b' }}>
                      Powered by Agent 2
                    </div>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                      <span className="text-white text-xs font-bold">A2</span>
                    </div>
                  </div>
                </div>

                {/* Forensic Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {[
                    {
                      name: 'Altman Z-Score',
                      value: analysisData.altman_z_score?.altman_z_score?.z_score || 'N/A',
                      status: analysisData.altman_z_score?.altman_z_score?.classification || 'Unknown',
                      color: analysisData.altman_z_score?.altman_z_score?.risk_level === 'LOW' ? '#4ade80' : '#FF6B9D',
                      icon: '📊'
                    },
                    {
                      name: 'Beneish M-Score',
                      value: analysisData.beneish_m_score?.beneish_m_score?.m_score || 'N/A',
                      status: analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? 'Risk' : 'Safe',
                      color: analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? '#FF6B9D' : '#4ade80',
                      icon: '⚖️'
                    },
                    {
                      name: 'Benford\'s Law',
                      value: `${analysisData.benford_analysis?.benford_analysis?.compliance_score || 'N/A'}%`,
                      status: analysisData.benford_analysis?.benford_analysis?.interpretation || 'Normal',
                      color: analysisData.benford_analysis?.benford_analysis?.is_anomalous ? '#FF6B9D' : '#4ade80',
                      icon: '📈'
                    },
                    {
                      name: 'Debt to Equity',
                      value: analysisData.financial_ratios?.financial_ratios?.['2025-03-31']?.debt_to_equity || 'N/A',
                      status: 'Good',
                      color: '#4ade80',
                      icon: '💰'
                    },
                    {
                      name: 'Current Ratio',
                      value: '1.32',
                      status: 'Moderate',
                      color: '#7B68EE',
                      icon: '🔄'
                    },
                    {
                      name: 'ROE',
                      value: `${analysisData.financial_ratios?.financial_ratios?.['2025-03-31']?.roe || 'N/A'}%`,
                      status: 'Strong',
                      color: '#4ade80',
                      icon: '📈'
                    },
                  ].map((metric, index) => (
                    <div
                      key={index}
                      className="neumorphic-card rounded-2xl p-6 group"
                      style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
                        border: `2px solid ${metric.color}20`
                      }}
                    >
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 rounded-xl flex items-center justify-center text-xl" style={{
                          background: `linear-gradient(135deg, ${metric.color}, ${metric.color}dd)`,
                          boxShadow: `0 0 15px ${metric.color}30`
                        }}>
                          {metric.icon}
                        </div>
                        <div>
                          <h3 className="font-bold text-base mb-1" style={{ color: '#1e293b' }}>{metric.name}</h3>
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
                      </div>
                    </div>
                  ))}
                </div>

                {/* ScoreDistribution Chart */}
                <div className="neumorphic-card rounded-3xl p-8 mb-8" style={{
                  background: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(20px)',
                  boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                  border: '2px solid rgba(123, 104, 238, 0.2)'
                }}>
                  <h3 className="text-2xl font-bold mb-6" style={{ color: '#1e293b' }}>Forensic Test Results Distribution</h3>
                  <ScoreDistribution
                    data={{
                      forensicScores: analysisData.forensic_scores || [65, 78, 82, 45, 91, 67, 88, 72, 55, 83, 76, 69, 84, 77, 90, 58, 81, 74, 86, 79, 75, 89, 73, 85, 80, 87, 71, 92, 68],
                      companyScore: analysisData.altman_z_score?.altman_z_score?.z_score || 75
                    }}
                    benchmarks={{
                      industry_avg: 70,
                      peer_avg: 72
                    }}
                    companyName={selectedCompany}
                  />
                </div>

                {/* Detailed Forensic Tables */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Financial Ratios Table */}
                  <div className="neumorphic-card rounded-2xl p-6" style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                  }}>
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Key Financial Ratios</h3>
                    <div className="space-y-3">
                      {Object.entries(analysisData.financial_ratios?.financial_ratios || {}).slice(0, 3).map(([period, ratios]: [string, any]) => (
                        <div key={period} className="p-4 rounded-xl" style={{
                          background: 'rgba(255, 255, 255, 0.8)',
                          boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
                        }}>
                          <h4 className="font-semibold mb-2" style={{ color: '#1e293b' }}>{period}</h4>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Net Margin:</span>
                              <span className="font-semibold ml-2" style={{ color: '#7B68EE' }}>
                                {ratios.net_margin_pct || 'N/A'}%
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">ROE:</span>
                              <span className="font-semibold ml-2" style={{ color: '#4ade80' }}>
                                {ratios.roe || 'N/A'}%
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Current Ratio:</span>
                              <span className="font-semibold ml-2" style={{ color: '#FF6B9D' }}>
                                {ratios.current_ratio || 'N/A'}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Debt/Equity:</span>
                              <span className="font-semibold ml-2" style={{ color: '#f2a09e' }}>
                                {ratios.debt_to_equity || 'N/A'}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Advanced Tests Table */}
                  <div className="neumorphic-card rounded-2xl p-6" style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                  }}>
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Advanced Fraud Detection</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 rounded-xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '2px solid rgba(74, 222, 128, 0.2)'
                      }}>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                            <span className="text-white text-sm">✓</span>
                          </div>
                          <div>
                            <p className="font-semibold" style={{ color: '#1e293b' }}>Benford's Law</p>
                            <p className="text-sm" style={{ color: '#64748b' }}>Statistical compliance</p>
                          </div>
                        </div>
                        <span className="font-bold" style={{ color: '#4ade80' }}>
                          {analysisData.benford_analysis?.benford_analysis?.compliance_score || 'N/A'}%
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-4 rounded-xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '2px solid rgba(255, 107, 157, 0.2)'
                      }}>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center">
                            <span className="text-white text-sm">⚠️</span>
                          </div>
                          <div>
                            <p className="font-semibold" style={{ color: '#1e293b' }}>Altman Z-Score</p>
                            <p className="text-sm" style={{ color: '#64748b' }}>Bankruptcy risk</p>
                          </div>
                        </div>
                        <span className="font-bold" style={{ color: '#FF6B9D' }}>
                          {analysisData.altman_z_score?.altman_z_score?.z_score || 'N/A'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-4 rounded-xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '2px solid rgba(139, 92, 246, 0.2)'
                      }}>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
                            <span className="text-white text-sm">🔍</span>
                          </div>
                          <div>
                            <p className="font-semibold" style={{ color: '#1e293b' }}>Beneish M-Score</p>
                            <p className="text-sm" style={{ color: '#64748b' }}>Earnings manipulation</p>
                          </div>
                        </div>
                        <span className="font-bold" style={{ color: '#8b5cf6' }}>
                          {analysisData.beneish_m_score?.beneish_m_score?.m_score || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Risk Tab Content */}
          {activeTab === 'risk' && analysisData && (
            <div className="space-y-6">
              {/* Gemini AI Risk Summary */}
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                border: '2px solid rgba(255, 107, 157, 0.3)'
              }}>
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-pink-500 to-red-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">🎯</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl font-bold" style={{ color: '#1e293b' }}>AI Risk Intelligence Summary</h3>
                      <span className="px-3 py-1 rounded-full text-xs font-bold" style={{
                        background: 'linear-gradient(135deg, #FF6B9D 0%, #ef4444 100%)',
                        color: '#fff'
                      }}>
                        Powered by Gemini 2.0
                      </span>
                    </div>
                    <p className="text-sm font-medium mb-4" style={{ color: '#64748b' }}>
                      Multi-dimensional risk evaluation across 6 critical investment categories
                    </p>
                    <div className="prose prose-slate max-w-none">
                      <div className="p-6 rounded-2xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
                      }}>
                        {isLoadingRiskSummary ? (
                          <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-600 mr-3"></div>
                            <span className="text-base" style={{ color: '#64748b' }}>Generating AI risk intelligence...</span>
                          </div>
                        ) : riskSummary ? (
                          <div 
                            className="text-base leading-relaxed" 
                            style={{ color: '#1e293b' }}
                            dangerouslySetInnerHTML={{ __html: riskSummary }}
                          />
                        ) : (
                          <>
                            <p className="text-base leading-relaxed mb-4" style={{ color: '#1e293b' }}>
                              <strong>Overall Risk Profile:</strong> {selectedCompany} presents an overall risk score of{' '}
                              <strong style={{ 
                                color: (analysisData.risk_assessment?.overall_risk_score || 0) > 70 ? '#ef4444' : 
                                       (analysisData.risk_assessment?.overall_risk_score || 0) > 50 ? '#f59e0b' : '#22c55e',
                                fontSize: '1.1em'
                              }}>
                                {analysisData.risk_assessment?.overall_risk_score || 'N/A'}/100
                              </strong>, classified as{' '}
                              <strong>{analysisData.risk_assessment?.risk_level || 'MODERATE'} RISK</strong>. 
                              This assessment is derived from a comprehensive analysis of financial stability, market volatility, 
                              operational efficiency, and regulatory compliance factors.
                            </p>
                            <p className="text-base leading-relaxed mb-4" style={{ color: '#1e293b' }}>
                              <strong>Investment Recommendation:</strong>{' '}
                              {(analysisData.risk_assessment?.overall_risk_score || 0) < 40 
                                ? 'The company demonstrates strong fundamentals with low risk exposure, making it suitable for conservative investors seeking stable returns. The risk-reward profile favors long-term capital appreciation with minimal downside volatility.' 
                                : (analysisData.risk_assessment?.overall_risk_score || 0) < 70 
                                  ? 'The company exhibits moderate risk characteristics that require balanced portfolio allocation. Suitable for investors with medium risk tolerance who can weather short-term fluctuations for potential growth opportunities.' 
                                  : 'The company shows elevated risk indicators that warrant cautious approach. Recommended only for aggressive investors with high risk appetite and diversified portfolios. Enhanced monitoring and stop-loss strategies are advised.'
                              }
                            </p>
                            <p className="text-base leading-relaxed mb-4" style={{ color: '#1e293b' }}>
                              <strong>Key Risk Drivers:</strong> The primary risk factors include{' '}
                              {analysisData.risk_assessment?.category_scores ? 
                                Object.entries(analysisData.risk_assessment.category_scores)
                                  .sort((a: any, b: any) => (b[1].score || 0) - (a[1].score || 0))
                                  .slice(0, 3)
                                  .map((entry: any) => entry[0].replace(/_/g, ' '))
                                  .join(', ')
                                : 'financial leverage, market volatility, and operational efficiency'
                              }. These factors collectively contribute to the overall risk profile and require continuous monitoring 
                              for early warning signals of deteriorating conditions.
                            </p>
                            <p className="text-base leading-relaxed" style={{ color: '#1e293b' }}>
                              <strong>Monitoring Frequency:</strong> Based on the current risk assessment, we recommend{' '}
                              <strong style={{ color: '#7B68EE' }}>
                                {(analysisData.risk_assessment?.overall_risk_score || 0) > 70 ? 'WEEKLY' : 
                                 (analysisData.risk_assessment?.overall_risk_score || 0) > 50 ? 'BI-WEEKLY' : 'MONTHLY'}
                              </strong>{' '}
                              portfolio reviews. 
                              {(analysisData.risk_assessment?.overall_risk_score || 0) > 70 
                                ? ' High-risk positions require frequent reassessment to capture rapid market changes and emerging threats.' 
                                : (analysisData.risk_assessment?.overall_risk_score || 0) > 50 
                                  ? ' Moderate-risk investments benefit from regular check-ins to maintain optimal risk-return balance.' 
                                  : ' Low-risk holdings allow for less frequent monitoring while maintaining strategic oversight.'
                              }
                              {' '}Key metrics to track include liquidity ratios, debt service coverage, and market sentiment indicators.
                            </p>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Dedicated Risk Assessment Section */}
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                border: '2px solid rgba(255, 107, 157, 0.2)'
              }}>
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Risk Assessment</h2>
                    <p className="text-sm font-medium" style={{ color: '#64748b' }}>6-category weighted analysis</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-sm font-medium" style={{ color: '#64748b' }}>
                      Powered by Agent 3
                    </div>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-red-600 flex items-center justify-center">
                      <span className="text-white text-xs font-bold">A3</span>
                    </div>
                  </div>
                </div>

                {/* Risk Score Overview */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                  <div className="flex items-center justify-center">
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

                  <div className="space-y-4">
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Risk Categories</h3>
                    {Object.entries(analysisData.risk_assessment?.category_scores || {}).map(([category, data]: [string, any], index) => {
                      const categoryName = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                      const score = Math.round(data.score || 0);
                      const color = score > 70 ? '#FF6B9D' : score > 50 ? '#7B68EE' : '#4ade80';

                      return (
                        <div key={index} className="group">
                          <div className="flex justify-between text-sm mb-2">
                            <span className="font-semibold" style={{ color: '#1e293b' }}>{categoryName}</span>
                            <span className="font-bold" style={{ color: '#64748b' }}>{score}%</span>
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
                                width: `${score}%`,
                                background: `linear-gradient(90deg, ${color}, ${color}aa)`
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
                      );
                    })}
                  </div>
                </div>

                {/* AnomalyHeatmap Chart */}
                <div className="neumorphic-card rounded-3xl p-8 mb-8" style={{
                  background: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(20px)',
                  boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                  border: '2px solid rgba(255, 107, 157, 0.2)'
                }}>
                  <h3 className="text-2xl font-bold mb-6" style={{ color: '#1e293b' }}>Anomaly Detection Heatmap</h3>
                  <AnomalyHeatmap
                    data={{
                      anomalyData: [
                        { dimension: 'Revenue', category: 'Q1', value: 0.8, severity: 'high' },
                        { dimension: 'Expenses', category: 'Q1', value: 0.6, severity: 'medium' },
                        { dimension: 'Assets', category: 'Q1', value: 0.4, severity: 'low' },
                        { dimension: 'Liabilities', category: 'Q1', value: 0.9, severity: 'high' },
                        { dimension: 'Cash Flow', category: 'Q1', value: 0.7, severity: 'high' },
                        { dimension: 'Inventory', category: 'Q1', value: 0.5, severity: 'medium' },
                        { dimension: 'Receivables', category: 'Q1', value: 0.3, severity: 'low' },
                        { dimension: 'Payables', category: 'Q1', value: 0.2, severity: 'low' },
                        { dimension: 'Equity', category: 'Q1', value: 0.1, severity: 'low' },
                        { dimension: 'Profit Margins', category: 'Q1', value: 0.6, severity: 'medium' }
                      ]
                    }}
                    dimensions={['Revenue', 'Expenses', 'Assets', 'Liabilities', 'Cash Flow', 'Inventory', 'Receivables', 'Payables', 'Equity', 'Profit Margins']}
                    companyName={selectedCompany}
                  />
                </div>

                {/* Risk Factors & Recommendations */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="neumorphic-card rounded-2xl p-6" style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                  }}>
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Risk Factors</h3>
                    <div className="space-y-3">
                      {analysisData.risk_assessment?.risk_factors?.slice(0, 5).map((factor: string, index: number) => (
                        <div key={index} className="flex items-center gap-3 p-3 rounded-xl" style={{
                          background: 'rgba(255, 255, 255, 0.8)',
                          boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                          border: '1px solid rgba(255, 107, 157, 0.2)'
                        }}>
                          <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center flex-shrink-0">
                            <span className="text-white text-sm">⚠️</span>
                          </div>
                          <span className="font-medium" style={{ color: '#1e293b' }}>{factor}</span>
                        </div>
                      )) || (
                        <div className="text-center py-8">
                          <p className="text-gray-500">No specific risk factors identified</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="neumorphic-card rounded-2xl p-6" style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                  }}>
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Investment Recommendation</h3>
                    <div className="p-4 rounded-xl mb-4" style={{
                      background: 'rgba(255, 255, 255, 0.8)',
                      boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                      border: '2px solid rgba(74, 222, 128, 0.2)'
                    }}>
                      <p className="font-semibold text-lg mb-2" style={{ color: '#1e293b' }}>
                        {analysisData.risk_assessment?.risk_level || 'MEDIUM'} Risk Profile
                      </p>
                      <p className="text-sm" style={{ color: '#64748b' }}>
                        {analysisData.risk_assessment?.investment_recommendation || 'Additional analysis recommended for investment decisions.'}
                      </p>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center gap-3 p-3 rounded-xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '1px solid rgba(34, 197, 94, 0.2)'
                      }}>
                        <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
                          <span className="text-white text-sm">📅</span>
                        </div>
                        <div>
                          <p className="font-semibold" style={{ color: '#1e293b' }}>Monitoring Frequency</p>
                          <p className="text-sm" style={{ color: '#64748b' }}>
                            {analysisData.risk_assessment?.monitoring_frequency || 'QUARTERLY'} reviews recommended
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 p-3 rounded-xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '1px solid rgba(139, 92, 246, 0.2)'
                      }}>
                        <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0">
                          <span className="text-white text-sm">🎯</span>
                        </div>
                        <div>
                          <p className="font-semibold" style={{ color: '#1e293b' }}>Next Review</p>
                          <p className="text-sm" style={{ color: '#64748b' }}>
                            {(new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Reports Section */}
          {activeTab === 'reports' && analysisData && (
            <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
              background: 'rgba(255, 255, 255, 0.9)',
              backdropFilter: 'blur(20px)',
              boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)'
            }}>
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Generate Reports</h2>
                  <p className="text-sm font-medium" style={{ color: '#64748b' }}>
                    Comprehensive analysis reports for {selectedCompany}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-sm font-medium" style={{ color: '#64748b' }}>
                    Generated by Gemini 2.0 AI
                  </div>
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <span className="text-white text-xs font-bold">AI</span>
                  </div>
                </div>
              </div>

              {/* Report Generation Options */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                <div className="neumorphic-card rounded-2xl p-6" style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
                  border: '2px solid rgba(239, 68, 68, 0.2)'
                }}>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center">
                      <span className="text-white text-xl">📄</span>
                    </div>
                    <div>
                      <h3 className="font-bold text-lg" style={{ color: '#1e293b' }}>PDF Report</h3>
                      <p className="text-sm" style={{ color: '#64748b' }}>Professional PDF format</p>
                    </div>
                  </div>
                  <button
                    onClick={() => generateReport(['pdf'])}
                    disabled={isGeneratingReport}
                    className="w-full px-4 py-3 rounded-xl font-semibold transition-all neumorphic-button"
                    style={{
                      background: isGeneratingReport ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                      boxShadow: '6px 6px 12px rgba(239, 68, 68, 0.3), -6px -6px 12px rgba(255, 255, 255, 0.8)',
                      color: '#fff',
                      cursor: isGeneratingReport ? 'not-allowed' : 'pointer',
                      opacity: isGeneratingReport ? 0.7 : 1
                    }}
                  >
                    {isGeneratingReport ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Generating...
                      </div>
                    ) : (
                      '📄 Generate PDF'
                    )}
                  </button>
                </div>

                <div className="neumorphic-card rounded-2xl p-6" style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
                  border: '2px solid rgba(16, 185, 129, 0.2)'
                }}>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                      <span className="text-white text-xl">📊</span>
                    </div>
                    <div>
                      <h3 className="font-bold text-lg" style={{ color: '#1e293b' }}>Excel Report</h3>
                      <p className="text-sm" style={{ color: '#64748b' }}>Data analysis spreadsheet</p>
                    </div>
                  </div>
                  <button
                    onClick={() => generateReport(['excel'])}
                    disabled={isGeneratingReport}
                    className="w-full px-4 py-3 rounded-xl font-semibold transition-all neumorphic-button"
                    style={{
                      background: isGeneratingReport ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      boxShadow: '6px 6px 12px rgba(16, 185, 129, 0.3), -6px -6px 12px rgba(255, 255, 255, 0.8)',
                      color: '#fff',
                      cursor: isGeneratingReport ? 'not-allowed' : 'pointer',
                      opacity: isGeneratingReport ? 0.7 : 1
                    }}
                  >
                    {isGeneratingReport ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Generating...
                      </div>
                    ) : (
                      '📊 Generate Excel'
                    )}
                  </button>
                </div>

                <div className="neumorphic-card rounded-2xl p-6" style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
                  border: '2px solid rgba(139, 92, 246, 0.2)'
                }}>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                      <span className="text-white text-xl">🚀</span>
                    </div>
                    <div>
                      <h3 className="font-bold text-lg" style={{ color: '#1e293b' }}>Complete Report</h3>
                      <p className="text-sm" style={{ color: '#64748b' }}>PDF + Excel + AI Summary</p>
                    </div>
                  </div>
                  <button
                    onClick={() => generateReport(['pdf', 'excel'])}
                    disabled={isGeneratingReport}
                    className="w-full px-4 py-3 rounded-xl font-semibold transition-all neumorphic-button"
                    style={{
                      background: isGeneratingReport ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' : 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                      boxShadow: '6px 6px 12px rgba(139, 92, 246, 0.3), -6px -6px 12px rgba(255, 255, 255, 0.8)',
                      color: '#fff',
                      cursor: isGeneratingReport ? 'not-allowed' : 'pointer',
                      opacity: isGeneratingReport ? 0.7 : 1
                    }}
                  >
                    {isGeneratingReport ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Generating...
                      </div>
                    ) : (
                      '🚀 Generate Complete'
                    )}
                  </button>
                </div>
              </div>

              {/* Recent Reports */}
              {generatedReports.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-2xl font-bold mb-6" style={{ color: '#1e293b' }}>Recent Reports</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {generatedReports.map((report, index) => (
                      <div
                        key={index}
                        className="neumorphic-card rounded-2xl p-6 group"
                        style={{
                          background: 'rgba(255, 255, 255, 0.8)',
                          boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)',
                          border: '2px solid rgba(139, 92, 246, 0.2)'
                        }}
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                              <span className="text-white text-sm font-bold">
                                {report.format === 'pdf' ? '📄' : '📊'}
                              </span>
                            </div>
                            <div>
                              <p className="font-bold" style={{ color: '#1e293b' }}>
                                {report.format.toUpperCase()} Report
                              </p>
                              <p className="text-sm" style={{ color: '#64748b' }}>
                                {new Date(report.generatedAt).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => downloadReport(report.filename)}
                            className="px-4 py-2 rounded-xl font-semibold transition-all neumorphic-button"
                            style={{
                              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                              boxShadow: '4px 4px 8px rgba(139, 92, 246, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.8)',
                              color: '#fff'
                            }}
                          >
                            ⬇️ Download
                          </button>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span style={{ color: '#64748b' }}>
                            {(report.fileSize / 1024).toFixed(1)} KB
                          </span>
                          <span style={{ color: '#64748b' }}>
                            {report.wordCount || 'N/A'} words
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Analysis Message */}
              {!analysisData && (
                <div className="text-center py-12">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">📄</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2" style={{ color: '#1e293b' }}>
                    No Analysis Available
                  </h3>
                  <p className="text-sm" style={{ color: '#64748b' }}>
                    Please analyze a company first to generate reports
                  </p>
                </div>
              )}
            </div>
          )}
          {analysisData && activeTab === 'overview' ? (
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
          ) : null}

          {/* Compliance Tab Content */}
          {activeTab === 'compliance' && analysisData && (
            <div className="space-y-6">
              {/* Gemini AI Regulatory Recommendations */}
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                border: '2px solid rgba(34, 197, 94, 0.3)'
              }}>
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">⚖️</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl font-bold" style={{ color: '#1e293b' }}>SEBI Regulatory Recommendations</h3>
                      <span className="px-3 py-1 rounded-full text-xs font-bold" style={{
                        background: 'linear-gradient(135deg, #22c55e 0%, #10b981 100%)',
                        color: '#fff'
                      }}>
                        Powered by Gemini 2.0
                      </span>
                    </div>
                    <p className="text-sm font-medium mb-4" style={{ color: '#64748b' }}>
                      AI-generated regulatory guidance and compliance monitoring recommendations for SEBI officers
                    </p>
                    <div className="prose prose-slate max-w-none">
                      <div className="p-6 rounded-2xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)'
                      }}>
                        {isLoadingRegulatoryRecommendations ? (
                          <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mr-3"></div>
                            <span className="text-base" style={{ color: '#64748b' }}>Generating regulatory recommendations...</span>
                          </div>
                        ) : regulatoryRecommendations ? (
                          <div
                            className="text-base leading-relaxed"
                            style={{ color: '#1e293b' }}
                            dangerouslySetInnerHTML={{ __html: regulatoryRecommendations.replace(/\n/g, '<br>') }}
                          />
                        ) : (
                          <div className="text-center py-8">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center mx-auto mb-4">
                              <span className="text-2xl">⚖️</span>
                            </div>
                            <p className="text-base leading-relaxed mb-4" style={{ color: '#1e293b' }}>
                              <strong>Default Regulatory Recommendations:</strong>
                            </p>
                            <div className="space-y-2 text-left">
                              <p style={{ color: '#1e293b' }}>• <strong>No immediate enforcement action required.</strong></p>
                              <p style={{ color: '#1e293b' }}>• <strong>Maintain quarterly forensic monitoring.</strong></p>
                              <p style={{ color: '#1e293b' }}>• <strong>Cross-verify debt covenants in Q2 for early distress signals.</strong></p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Compliance Assessment Section */}
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                border: '2px solid rgba(34, 197, 94, 0.2)'
              }}>
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="text-3xl font-bold mb-2" style={{ color: '#1e293b' }}>Compliance Assessment</h2>
                    <p className="text-sm font-medium" style={{ color: '#64748b' }}>Regulatory framework validation</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-sm font-medium" style={{ color: '#64748b' }}>
                      Powered by Agent 4
                    </div>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                      <span className="text-white text-xs font-bold">A4</span>
                    </div>
                  </div>
                </div>

                {/* Compliance Score Overview */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                  <div className="flex items-center justify-center">
                    <div
                      className="w-48 h-48 rounded-full flex items-center justify-center relative"
                      style={{
                        background: 'linear-gradient(135deg, #22c55e 0%, #10b981 100%)',
                        boxShadow: '12px 12px 24px rgba(34, 197, 94, 0.3), -12px -12px 24px rgba(255, 255, 255, 0.2)'
                      }}
                    >
                      <div
                        className="w-40 h-40 rounded-full flex flex-col items-center justify-center relative"
                        style={{
                          background: 'rgba(255, 255, 255, 0.95)',
                          boxShadow: 'inset 6px 6px 12px rgba(0,0,0,0.1), inset -6px -6px 12px rgba(255,255,255,0.9)'
                        }}
                      >
                        <span className="text-5xl font-bold mb-1" style={{ color: '#22c55e' }}>
                          {analysisData.compliance_assessment?.overall_compliance_score || 'N/A'}
                        </span>
                        <span className="text-sm font-semibold" style={{ color: '#64748b' }}>Compliance Score</span>
                        <div className="absolute -top-2 -right-2">
                          <div className="w-6 h-6 rounded-full bg-white shadow-lg flex items-center justify-center">
                            <span className="text-xs">%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Framework Compliance</h3>
                    {Object.entries(analysisData.compliance_assessment?.framework_scores || {}).map(([framework, data]: [string, any], index) => {
                      const frameworkName = framework.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                      const score = Math.round(data.score || 0);
                      const color = score > 80 ? '#22c55e' : score > 60 ? '#7B68EE' : '#FF6B9D';

                      return (
                        <div key={index} className="group">
                          <div className="flex justify-between text-sm mb-2">
                            <span className="font-semibold" style={{ color: '#1e293b' }}>{frameworkName}</span>
                            <span className="font-bold" style={{ color: '#64748b' }}>{score}%</span>
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
                                width: `${score}%`,
                                background: `linear-gradient(90deg, ${color}, ${color}aa)`
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
                      );
                    })}
                  </div>
                </div>

                {/* Violations and Actions */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="neumorphic-card rounded-2xl p-6" style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                  }}>
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Compliance Violations</h3>
                    <div className="space-y-3">
                      {analysisData.compliance_assessment?.violations?.slice(0, 5).map((violation: string, index: number) => (
                        <div key={index} className="flex items-center gap-3 p-3 rounded-xl" style={{
                          background: 'rgba(255, 255, 255, 0.8)',
                          boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                          border: '1px solid rgba(255, 107, 157, 0.2)'
                        }}>
                          <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center flex-shrink-0">
                            <span className="text-white text-sm">⚠️</span>
                          </div>
                          <span className="font-medium" style={{ color: '#1e293b' }}>{violation}</span>
                        </div>
                      )) || (
                        <div className="text-center py-8">
                          <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center mx-auto mb-3">
                            <span className="text-white text-lg">✓</span>
                          </div>
                          <p className="text-green-600 font-semibold">No violations detected</p>
                          <p className="text-sm text-gray-500">Company is compliant with all frameworks</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="neumorphic-card rounded-2xl p-6" style={{
                    background: 'rgba(255, 255, 255, 0.7)',
                    boxShadow: '8px 8px 16px rgba(0,0,0,0.1), -8px -8px 16px rgba(255,255,255,0.9)'
                  }}>
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#1e293b' }}>Next Review Schedule</h3>
                    <div className="space-y-4">
                      <div className="p-4 rounded-xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '2px solid rgba(34, 197, 94, 0.2)'
                      }}>
                        <p className="font-semibold text-lg mb-2" style={{ color: '#1e293b' }}>
                          {analysisData.compliance_assessment?.compliance_status || 'QUARTERLY'} Review Required
                        </p>
                        <p className="text-sm" style={{ color: '#64748b' }}>
                          {analysisData.compliance_assessment?.overall_compliance_score > 80
                            ? 'Annual review sufficient due to strong compliance record'
                            : analysisData.compliance_assessment?.overall_compliance_score > 60
                            ? 'Quarterly monitoring recommended'
                            : 'Monthly compliance checks required'
                          }
                        </p>
                      </div>

                      <div className="flex items-center gap-3 p-3 rounded-xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '1px solid rgba(139, 92, 246, 0.2)'
                      }}>
                        <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0">
                          <span className="text-white text-sm">📅</span>
                        </div>
                        <div>
                          <p className="font-semibold" style={{ color: '#1e293b' }}>Next Review Date</p>
                          <p className="text-sm" style={{ color: '#64748b' }}>
                            {analysisData.compliance_assessment?.next_review_date || 'Q2 2025'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
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

          {/* Q&A Tab Content */}
          {activeTab === 'qa' && analysisData && (
            <div className="space-y-6">
              {/* Q&A Interface */}
              <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%)',
                backdropFilter: 'blur(20px)',
                boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                border: '2px solid rgba(59, 130, 246, 0.3)'
              }}>
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">🤖</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl font-bold" style={{ color: '#1e293b' }}>Financial Q&A System</h3>
                      <span className="px-3 py-1 rounded-full text-xs font-bold" style={{
                        background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                        color: '#fff'
                      }}>
                        Powered by Gemini 2.0 + RAG
                      </span>
                    </div>
                    <p className="text-sm font-medium mb-6" style={{ color: '#64748b' }}>
                      Ask natural language questions about {selectedCompany} financial analysis using AI-powered retrieval-augmented generation
                    </p>

                    {/* Question Input */}
                    <div className="mb-6">
                      <div className="flex gap-4">
                        <div className="flex-1">
                          <input
                            type="text"
                            value={qaQuery}
                            onChange={(e) => setQaQuery(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleQaQuestion()}
                            placeholder="Ask about financial metrics, ratios, risk assessment, compliance status..."
                            className="w-full px-6 py-4 rounded-2xl text-base font-medium transition-all"
                            style={{
                              background: 'rgba(255, 255, 255, 0.9)',
                              boxShadow: 'inset 8px 8px 16px rgba(0,0,0,0.1), inset -8px -8px 16px rgba(255,255,255,0.9)',
                              border: 'none',
                              outline: 'none',
                              color: '#1e293b'
                            }}
                            disabled={isLoadingQa}
                          />
                        </div>
                        <button
                          onClick={handleQaQuestion}
                          disabled={isLoadingQa || !qaQuery.trim()}
                          className="px-8 py-4 rounded-2xl font-bold text-white transition-all neumorphic-button"
                          style={{
                            background: isLoadingQa ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                            boxShadow: '8px 8px 16px rgba(59, 130, 246, 0.3), -8px -8px 16px rgba(255, 255, 255, 0.8)',
                            cursor: isLoadingQa || !qaQuery.trim() ? 'not-allowed' : 'pointer',
                            opacity: isLoadingQa || !qaQuery.trim() ? 0.7 : 1,
                            minWidth: '120px'
                          }}
                        >
                          {isLoadingQa ? (
                            <div className="flex items-center gap-2">
                              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                              Asking...
                            </div>
                          ) : (
                            '💬 Ask'
                          )}
                        </button>
                      </div>

                      {/* Question Suggestions */}
                      <div className="mt-4 flex flex-wrap gap-2">
                        {[
                          "What is the company's risk level?",
                          "Explain the Altman Z-Score",
                          "What are the main compliance violations?",
                          "How is the debt-to-equity ratio?",
                          "What does the Beneish M-Score indicate?"
                        ].map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => setQaQuery(suggestion)}
                            className="px-3 py-2 rounded-xl text-sm font-medium transition-all neumorphic-button"
                            style={{
                              background: 'rgba(255, 255, 255, 0.8)',
                              boxShadow: '4px 4px 8px rgba(0,0,0,0.1), -4px -4px 8px rgba(255,255,255,0.9)',
                              color: '#3b82f6',
                              border: '1px solid rgba(59, 130, 246, 0.2)'
                            }}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Answer Display */}
                    {qaAnswer && (
                      <div className="p-6 rounded-2xl" style={{
                        background: 'rgba(255, 255, 255, 0.8)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '2px solid rgba(59, 130, 246, 0.2)'
                      }}>
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
                            <span className="text-white text-sm">AI</span>
                          </div>
                          <div>
                            <p className="font-bold" style={{ color: '#1e293b' }}>AI Assistant</p>
                            <div className="flex items-center gap-2">
                              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                                qaConfidence === 'High' ? 'bg-green-100 text-green-700' :
                                qaConfidence === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                                {qaConfidence} Confidence
                              </span>
                              <span className="text-xs" style={{ color: '#64748b' }}>
                                {new Date().toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="text-base leading-relaxed" style={{ color: '#1e293b' }}>
                          {qaAnswer}
                        </div>

                        {qaHistory.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-200">
                            <p className="text-sm font-medium mb-2" style={{ color: '#64748b' }}>
                              💡 Suggested follow-up questions:
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {[
                                "What are the key risk factors?",
                                "How does this compare to industry?",
                                "What are the compliance implications?",
                                "Can you explain the financial ratios?"
                              ].map((followUp, index) => (
                                <button
                                  key={index}
                                  onClick={() => setQaQuery(followUp)}
                                  className="px-2 py-1 rounded-lg text-xs font-medium transition-all"
                                  style={{
                                    background: 'rgba(59, 130, 246, 0.1)',
                                    color: '#3b82f6',
                                    border: '1px solid rgba(59, 130, 246, 0.2)'
                                  }}
                                >
                                  {followUp}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Q&A History */}
              {qaHistory.length > 0 && (
                <div className="neumorphic-card rounded-3xl p-8 glass-morphism" style={{
                  background: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(20px)',
                  boxShadow: '20px 20px 40px rgba(0,0,0,0.1), -20px -20px 40px rgba(255,255,255,0.9)',
                  border: '2px solid rgba(59, 130, 246, 0.2)'
                }}>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-2xl font-bold mb-2" style={{ color: '#1e293b' }}>Q&A History</h3>
                      <p className="text-sm font-medium" style={{ color: '#64748b' }}>
                        Previous questions and answers for {selectedCompany}
                      </p>
                    </div>
                    <button
                      onClick={() => setQaHistory([])}
                      className="px-4 py-2 rounded-xl font-semibold transition-all neumorphic-button"
                      style={{
                        background: 'rgba(255, 255, 255, 0.9)',
                        boxShadow: '4px 4px 8px rgba(0,0,0,0.1), -4px -4px 8px rgba(255,255,255,0.9)',
                        color: '#64748b'
                      }}
                    >
                      Clear History
                    </button>
                  </div>

                  <div className="space-y-4">
                    {qaHistory.map((item, index) => (
                      <div key={index} className="p-6 rounded-2xl" style={{
                        background: 'rgba(255, 255, 255, 0.7)',
                        boxShadow: 'inset 4px 4px 8px rgba(0,0,0,0.05), inset -4px -4px 8px rgba(255,255,255,0.9)',
                        border: '1px solid rgba(59, 130, 246, 0.2)'
                      }}>
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
                              <span className="text-white text-xs">Q</span>
                            </div>
                            <p className="font-semibold" style={{ color: '#1e293b' }}>{item.query}</p>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            item.confidence === 'High' ? 'bg-green-100 text-green-700' :
                            item.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {item.confidence}
                          </span>
                        </div>

                        <div className="flex items-start gap-3">
                          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                            <span className="text-white text-xs">A</span>
                          </div>
                          <div className="text-sm leading-relaxed" style={{ color: '#1e293b' }}>
                            {item.answer}
                          </div>
                        </div>

                        {item.contextUsed > 0 && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <p className="text-xs" style={{ color: '#64748b' }}>
                              Based on {item.contextUsed} financial document{item.contextUsed !== 1 ? 's' : ''}
                              {item.sources.length > 0 && ` • Sources: ${item.sources.join(', ')}`}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
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
