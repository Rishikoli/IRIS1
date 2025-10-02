import CardNav from "@/components/CardNav";

export default function Home() {
  const navItems = [
    {
      label: "Personal",
      bgColor: "#4A90FF",
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
    <div className="min-h-screen font-sans relative overflow-x-hidden" style={{ background: 'linear-gradient(135deg, #E8F4FF 0%, #F0F7FF 50%, #FFFFFF 100%)' }}>
      {/* Card Navigation */}
      <CardNav
        logo="/logo.svg"
        logoAlt="FinanceHub Logo"
        items={navItems}
        className="top-8"
        baseColor="#ffffff"
        menuColor="#4A90FF"
        buttonBgColor="#4A90FF"
        buttonTextColor="#ffffff"
      />

      {/* Hero Section */}
      <div className="pt-32 pb-20 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto mb-16">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-50 border border-blue-200 mb-6">
              <span className="w-2 h-2 rounded-full bg-blue-500 mr-2 animate-pulse"></span>
              <span className="text-sm font-semibold text-blue-700">Trusted by 50,000+ customers worldwide</span>
            </div>
            <h1 className="text-5xl lg:text-7xl font-bold mb-6 leading-tight" style={{ color: '#1a1a1a' }}>
              Smart Finance for
              <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent"> Modern Life</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed mb-8 max-w-2xl mx-auto">
              Take control of your financial future with intelligent banking, seamless payments, and powerful investment tools—all in one place.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-4 rounded-xl text-base font-semibold text-white transition-all hover:shadow-xl hover:scale-105" style={{ background: 'linear-gradient(135deg, #4A90FF 0%, #357AE8 100%)' }}>
                Open Free Account
              </button>
              <button className="px-8 py-4 rounded-xl text-base font-semibold text-gray-700 bg-white border-2 border-gray-200 hover:border-blue-300 transition-all">
                Watch Demo
              </button>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
            {/* Card 1 - Smart Banking */}
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 border border-blue-100/50 shadow-xl hover:shadow-2xl transition-all group">
              <div className="flex items-center justify-center w-16 h-16 rounded-2xl mb-6 mx-auto" style={{ background: 'linear-gradient(135deg, #4A90FF 0%, #357AE8 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">Smart Banking</h3>
              <p className="text-gray-600 leading-relaxed text-center mb-6">
                Experience next-generation banking with AI-powered insights, instant transfers, and intelligent budgeting tools.
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  Zero-fee transactions
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  Real-time notifications
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  Advanced security
                </div>
              </div>
              <button className="w-full py-3 rounded-xl font-semibold text-white transition-all hover:shadow-lg group-hover:scale-105" style={{ background: 'linear-gradient(135deg, #4A90FF 0%, #357AE8 100%)' }}>
                Start Banking
              </button>
            </div>

            {/* Card 2 - Investment Platform */}
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 border border-blue-100/50 shadow-xl hover:shadow-2xl transition-all group">
              <div className="flex items-center justify-center w-16 h-16 rounded-2xl mb-6 mx-auto" style={{ background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">Investment Platform</h3>
              <p className="text-gray-600 leading-relaxed text-center mb-6">
                Build wealth with our automated investment platform. Diversify across stocks, crypto, and retirement accounts.
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  Zero commission trading
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  AI portfolio management
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  Tax optimization
                </div>
              </div>
              <button className="w-full py-3 rounded-xl font-semibold text-white transition-all hover:shadow-lg group-hover:scale-105" style={{ background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)' }}>
                Start Investing
              </button>
            </div>

            {/* Card 3 - Premium Cards */}
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 border border-blue-100/50 shadow-xl hover:shadow-2xl transition-all group">
              <div className="flex items-center justify-center w-16 h-16 rounded-2xl mb-6 mx-auto" style={{ background: 'linear-gradient(135deg, #FF6B9D 0%, #FF4081 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">Premium Cards</h3>
              <p className="text-gray-600 leading-relaxed text-center mb-6">
                Unlock exclusive rewards and benefits with our premium card offerings. Cashback, travel perks, and more.
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  Up to 5% cashback
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  Travel insurance included
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  No foreign fees
                </div>
              </div>
              <button className="w-full py-3 rounded-xl font-semibold text-white transition-all hover:shadow-lg group-hover:scale-105" style={{ background: 'linear-gradient(135deg, #FF6B9D 0%, #FF4081 100%)' }}>
                Get Premium Card
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
