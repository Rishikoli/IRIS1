"use client";

import CardNav from "@/components/CardNav";

export default function Home() {
  const navItems = [
    {
      label: "Personal",
      bgColor: "#f2a09e",
      textColor: "#ffffff",
      links: [
        { label: "Banking", href: "#", ariaLabel: "Personal Banking" },
        { label: "Cards", href: "#", ariaLabel: "Personal Cards" },
        { label: "Loans", href: "#", ariaLabel: "Personal Loans" }
      ]
    },
    {
      label: "Business",
      bgColor: "#7B68EE",
      textColor: "#ffffff",
      links: [
        { label: "Business Banking", href: "#", ariaLabel: "Business Banking" },
        { label: "Merchant Services", href: "#", ariaLabel: "Merchant Services" },
        { label: "Corporate Cards", href: "#", ariaLabel: "Corporate Cards" }
      ]
    },
    {
      label: "Investments",
      bgColor: "#FF6B9D",
      textColor: "#ffffff",
      links: [
        { label: "Stocks", href: "#", ariaLabel: "Stock Trading" },
        { label: "Crypto", href: "#", ariaLabel: "Cryptocurrency" },
        { label: "Retirement", href: "#", ariaLabel: "Retirement Planning" }
      ]
    }
  ];

  return (
    <>
      <style jsx>{`
        .neumorphic-card {
          transition: all 0.3s ease;
        }

        .neumorphic-card:hover {
          transform: translateY(-2px);
          box-shadow: 16px 16px 32px #c8c8c8, -16px -16px 32px #ffffff;
        }

        .neumorphic-icon {
          transition: all 0.3s ease;
        }

        .neumorphic-button {
          transition: all 0.2s ease;
        }

        .neumorphic-button:hover {
          transform: translateY(-1px);
        }

        .neumorphic-button:active {
          transform: translateY(1px);
        }

        .neumorphic-dot {
          transition: all 0.2s ease;
        }

        .neumorphic-inset {
          transition: all 0.2s ease;
        }

        .neumorphic-circle {
          transition: all 0.2s ease;
        }
      `}</style>
      <div className="min-h-screen font-sans relative overflow-x-hidden" style={{ background: 'linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 50%, #f0f0f0 100%)' }}>
        {/* Card Navigation */}
        <CardNav
          logo="/logo.svg"
          logoAlt="FinanceHub Logo"
          items={navItems}
          className="top-8"
          baseColor="#f0f0f0"
          menuColor="#f2a09e"
          buttonBgColor="#f2a09e"
          buttonTextColor="#ffffff"
        />

        {/* Hero Section */}
        <div className="pt-32 pb-12 px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center max-w-4xl mx-auto mb-12">
              <div className="inline-flex items-center px-6 py-3 rounded-full mb-6 neumorphic-inset" style={{ background: '#e8e8e8', boxShadow: 'inset 8px 8px 16px #d0d0d0, inset -8px -8px 16px #ffffff' }}>
                <span className="w-3 h-3 rounded-full mr-3 neumorphic-circle" style={{ background: '#f2a09e', boxShadow: 'inset 2px 2px 4px #d89592, inset -2px -2px 4px #ffcfc8' }}></span>
                <span className="text-sm font-semibold" style={{ color: '#666' }}>Trusted by 50,000+ customers worldwide</span>
              </div>
              <h1 className="text-5xl lg:text-7xl font-bold mb-6 leading-tight" style={{ color: '#333' }}>
                Smart Finance for
                <span className="bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent"> Modern Life</span>
              </h1>
              <p className="text-xl leading-relaxed mb-8 max-w-2xl mx-auto" style={{ color: '#666' }}>
                Take control of your financial future with intelligent banking, seamless payments, and powerful investment tools—all in one place.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="px-8 py-4 rounded-xl text-base font-semibold text-white transition-all neumorphic-button" style={{ background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)', boxShadow: '8px 8px 16px #d89592, -8px -8px 16px #ffcfc8' }}>
                  Open Free Account
                </button>
                <button className="px-8 py-4 rounded-xl text-base font-semibold bg-white border-2 border-gray-200 hover:border-pink-300 transition-all neumorphic-button" style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff', color: '#666' }}>
                  Watch Demo
                </button>
              </div>
            </div>

            {/* Feature Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
              {/* Card 1 - Smart Banking */}
              <div className="neumorphic-card rounded-3xl p-8 transition-all group" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
                <div className="flex items-center justify-center w-20 h-20 rounded-3xl mb-6 mx-auto neumorphic-icon" style={{ background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)', boxShadow: '8px 8px 16px #d89592, -8px -8px 16px #ffcfc8' }}>
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-center" style={{ color: '#333' }}>Smart Banking</h3>
                <p className="leading-relaxed text-center mb-6" style={{ color: '#666' }}>
                  Experience next-generation banking with AI-powered insights, instant transfers, and intelligent budgeting tools.
                </p>
                <div className="space-y-4 mb-8">
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    Zero-fee transactions
                  </div>
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    Real-time notifications
                  </div>
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    Advanced security
                  </div>
                </div>
                <button className="w-full py-4 rounded-xl font-semibold text-white transition-all neumorphic-button" style={{ background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)', boxShadow: '8px 8px 16px #d89592, -8px -8px 16px #ffcfc8' }}>
                  Start Banking
                </button>
              </div>

              {/* Card 2 - Investment Platform */}
              <div className="neumorphic-card rounded-3xl p-8 transition-all group" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
                <div className="flex items-center justify-center w-20 h-20 rounded-3xl mb-6 mx-auto neumorphic-icon" style={{ background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)', boxShadow: '8px 8px 16px #6b5acc, -8px -8px 16px #8b79f0' }}>
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-center" style={{ color: '#333' }}>Investment Platform</h3>
                <p className="leading-relaxed text-center mb-6" style={{ color: '#666' }}>
                  Build wealth with our automated investment platform. Diversify across stocks, crypto, and retirement accounts.
                </p>
                <div className="space-y-4 mb-8">
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    Zero commission trading
                  </div>
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    AI portfolio management
                  </div>
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    Tax optimization
                  </div>
                </div>
                <button className="w-full py-4 rounded-xl font-semibold text-white transition-all neumorphic-button" style={{ background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)', boxShadow: '8px 8px 16px #6b5acc, -8px -8px 16px #8b79f0' }}>
                  Start Investing
                </button>
              </div>

              {/* Card 3 - Premium Cards */}
              <div className="neumorphic-card rounded-3xl p-8 transition-all group" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
                <div className="flex items-center justify-center w-20 h-20 rounded-3xl mb-6 mx-auto neumorphic-icon" style={{ background: 'linear-gradient(135deg, #FF6B9D 0%, #FF4081 100%)', boxShadow: '8px 8px 16px #e85a8a, -8px -8px 16px #ff7cb0' }}>
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-center" style={{ color: '#333' }}>Premium Cards</h3>
                <p className="leading-relaxed text-center mb-6" style={{ color: '#666' }}>
                  Unlock exclusive rewards and benefits with our premium card offerings. Cashback, travel perks, and more.
                </p>
                <div className="space-y-4 mb-8">
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    Up to 5% cashback
                  </div>
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    Travel insurance included
                  </div>
                  <div className="flex items-center text-sm" style={{ color: '#666' }}>
                    <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
                    No foreign fees
                  </div>
                </div>
                <button className="w-full py-4 rounded-xl font-semibold text-white transition-all neumorphic-button" style={{ background: 'linear-gradient(135deg, #FF6B9D 0%, #FF4081 100%)', boxShadow: '8px 8px 16px #e85a8a, -8px -8px 16px #ff7cb0' }}>
                  Get Premium Card
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
