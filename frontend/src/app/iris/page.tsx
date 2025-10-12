"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import CardNav from "@/components/CardNav";

export default function IRISAnalyticsDashboard() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCompany, setSelectedCompany] = useState('');

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
      <style jsx>{`
        .neumorphic-card {
          transition: all 0.3s ease;
        }
        .neumorphic-card:hover {
          transform: translateY(-2px);
        }
        .neumorphic-button:hover {
          transform: translateY(-1px);
        }
        .sidebar {
          position: fixed;
          left: 0;
          top: 0;
          bottom: 0;
          width: 240px;
          z-index: 40;
          transform: translateX(0);
          transition: transform 0.3s ease;
        }
        .main-content {
          margin-left: 240px;
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
      <div className="relative z-50 mb-12">
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
        <div className="max-w-7xl mx-auto px-6 py-4">
          {/* Search & Filter Section */}
          <div className="mb-6">
            <div className="neumorphic-card rounded-3xl p-6" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium mb-2" style={{ color: '#666' }}>Company Name / Symbol</label>
                  <input
                    type="text"
                    value={selectedCompany}
                    onChange={(e) => setSelectedCompany(e.target.value)}
                    placeholder="Enter company name or NSE/BSE symbol (e.g., RELIANCE.NS)"
                    className="w-full px-6 py-3 rounded-xl text-base transition-all"
                    style={{
                      background: '#f0f0f0',
                      boxShadow: 'inset 6px 6px 12px #d0d0d0, inset -6px -6px 12px #ffffff',
                      border: 'none',
                      outline: 'none',
                      color: '#333'
                    }}
                  />
                </div>
                <div className="flex gap-3 items-end">
                  <button
                    className="px-8 py-3 rounded-xl font-semibold text-white transition-all neumorphic-button"
                    style={{ background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)', boxShadow: '6px 6px 12px #d89592, -6px -6px 12px #ffcfc8' }}
                  >
                    Analyze
                  </button>
                  <button
                    className="px-6 py-3 rounded-xl font-medium transition-all neumorphic-button"
                    style={{ background: '#f0f0f0', boxShadow: '6px 6px 12px #d0d0d0, -6px -6px 12px #ffffff', color: '#666' }}
                  >
                    Clear
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {[
              { label: 'Risk Score', value: '67/100', color: '#FF6B9D', icon: '⚠️' },
              { label: 'Forensic Metrics', value: '29', color: '#7B68EE', icon: '🔍' },
              { label: 'Anomalies Found', value: '3', color: '#f2a09e', icon: '🚨' },
              { label: 'Compliance', value: '94%', color: '#4ade80', icon: '✓' },
            ].map((stat, index) => (
              <div
                key={index}
                className="neumorphic-card rounded-2xl p-6"
                style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-2xl">{stat.icon}</span>
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: `${stat.color}20`, boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.1)' }}
                  >
                    <div className="w-3 h-3 rounded-full" style={{ background: stat.color }}></div>
                  </div>
                </div>
                <h3 className="text-3xl font-bold mb-2" style={{ color: '#333' }}>{stat.value}</h3>
                <p className="text-sm" style={{ color: '#666' }}>{stat.label}</p>
              </div>
            ))}
          </div>

          {/* Main Analysis Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Forensic Analysis Card */}
            <div
              className="neumorphic-card rounded-3xl p-6 lg:col-span-2"
              style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold" style={{ color: '#333' }}>Forensic Analysis</h2>
                <button
                  className="px-4 py-2 rounded-xl text-sm font-medium transition-all neumorphic-button"
                  style={{ background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)', boxShadow: '4px 4px 8px #d89592, -4px -4px 8px #ffcfc8', color: '#fff' }}
                >
                  View Details
                </button>
              </div>

              {/* Metrics List */}
              <div className="space-y-4">
                {[
                  { name: 'Altman Z-Score', value: '2.45', status: 'Warning', color: '#FF6B9D' },
                  { name: 'Beneish M-Score', value: '-1.89', status: 'Safe', color: '#4ade80' },
                  { name: 'Debt to Equity', value: '0.85', status: 'Good', color: '#4ade80' },
                  { name: 'Current Ratio', value: '1.32', status: 'Moderate', color: '#7B68EE' },
                ].map((metric, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 rounded-xl"
                    style={{ background: '#f0f0f0', boxShadow: 'inset 4px 4px 8px #d0d0d0, inset -4px -4px 8px #ffffff' }}
                  >
                    <div>
                      <p className="font-semibold mb-1" style={{ color: '#333' }}>{metric.name}</p>
                      <span className="text-xs px-3 py-1 rounded-full" style={{ background: `${metric.color}20`, color: metric.color }}>
                        {metric.status}
                      </span>
                    </div>
                    <span className="text-2xl font-bold" style={{ color: metric.color }}>{metric.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Assessment Card */}
            <div
              className="neumorphic-card rounded-3xl p-6"
              style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}
            >
              <h2 className="text-2xl font-bold mb-6" style={{ color: '#333' }}>Risk Assessment</h2>

              {/* Risk Score Circle */}
              <div className="flex items-center justify-center mb-6">
                <div
                  className="w-40 h-40 rounded-full flex items-center justify-center"
                  style={{ background: 'linear-gradient(135deg, #FF6B9D 0%, #FF4081 100%)', boxShadow: '8px 8px 16px #e85a8a, -8px -8px 16px #ff7cb0' }}
                >
                  <div
                    className="w-32 h-32 rounded-full flex flex-col items-center justify-center"
                    style={{ background: '#f0f0f0', boxShadow: 'inset 4px 4px 8px #d0d0d0, inset -4px -4px 8px #ffffff' }}
                  >
                    <span className="text-4xl font-bold" style={{ color: '#FF6B9D' }}>67</span>
                    <span className="text-sm" style={{ color: '#666' }}>Risk Score</span>
                  </div>
                </div>
              </div>

              {/* Risk Categories */}
              <div className="space-y-3">
                {[
                  { category: 'Financial', level: 65 },
                  { category: 'Operational', level: 72 },
                  { category: 'Compliance', level: 45 },
                  { category: 'Market', level: 80 },
                ].map((item, index) => (
                  <div key={index}>
                    <div className="flex justify-between text-sm mb-1">
                      <span style={{ color: '#666' }}>{item.category}</span>
                      <span style={{ color: '#333' }} className="font-semibold">{item.level}%</span>
                    </div>
                    <div
                      className="h-2 rounded-full overflow-hidden"
                      style={{ background: '#f0f0f0', boxShadow: 'inset 2px 2px 4px #d0d0d0, inset -2px -2px 4px #ffffff' }}
                    >
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${item.level}%`,
                          background: item.level > 70 ? 'linear-gradient(90deg, #FF6B9D, #FF4081)' : item.level > 50 ? 'linear-gradient(90deg, #7B68EE, #6A5ACD)' : 'linear-gradient(90deg, #4ade80, #22c55e)'
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Anomaly Detection Section */}
          <div
            className="neumorphic-card rounded-3xl p-6 mb-6"
            style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}
          >
            <h2 className="text-2xl font-bold mb-6" style={{ color: '#333' }}>Anomaly Detection</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { title: "Benford's Law Analysis", status: 'Detected', severity: 'High', color: '#FF6B9D' },
                { title: 'Revenue Pattern', status: 'Normal', severity: 'Low', color: '#4ade80' },
                { title: 'Expense Irregularities', status: 'Review Required', severity: 'Medium', color: '#7B68EE' },
              ].map((anomaly, index) => (
                <div
                  key={index}
                  className="p-5 rounded-2xl"
                  style={{ background: '#f0f0f0', boxShadow: 'inset 6px 6px 12px #d0d0d0, inset -6px -6px 12px #ffffff' }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-lg" style={{ color: '#333' }}>{anomaly.title}</h3>
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ background: anomaly.color, boxShadow: `0 0 8px ${anomaly.color}` }}
                    ></div>
                  </div>
                  <p className="text-sm mb-2" style={{ color: '#666' }}>{anomaly.status}</p>
                  <span
                    className="text-xs px-3 py-1 rounded-full font-medium"
                    style={{ background: `${anomaly.color}20`, color: anomaly.color }}
                  >
                    {anomaly.severity} Risk
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { title: 'Generate Report', icon: '📄', color: '#f2a09e' },
              { title: 'Compare Companies', icon: '📊', color: '#7B68EE' },
              { title: 'Export Data', icon: '💾', color: '#FF6B9D' },
            ].map((action, index) => (
              <button
                key={index}
                className="neumorphic-card rounded-2xl p-6 text-left transition-all cursor-pointer"
                style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}
              >
                <div className="flex items-center gap-4">
                  <div
                    className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl"
                    style={{ background: `linear-gradient(135deg, ${action.color}, ${action.color}dd)`, boxShadow: `4px 4px 8px ${action.color}80` }}
                  >
                    {action.icon}
                  </div>
                  <span className="font-semibold text-lg" style={{ color: '#333' }}>{action.title}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
