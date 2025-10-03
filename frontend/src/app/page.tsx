"use client";

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import CardNav from "@/components/CardNav";
import FeatureCard from "@/components/FeatureCard";
// import Squares from '@/components/Squares';
// Lazy-load heavy WebGL background to reduce initial JS
const LiquidEther = dynamic(() => import('@/components/LiquidEther'), {
  ssr: false,
  loading: () => null,
}) as any;




export default function Home() {
  // Defer mounting of heavy effect until after first paint/idle and respect reduced-motion
  const [enableEffect, setEnableEffect] = useState(false);
  const [simProps, setSimProps] = useState({
    resolution: 0.5, // Reduced from 0.75 for better performance
    iterationsViscous: 12, // Reduced from 20
    iterationsPoisson: 16, // Reduced from 24
    cursorSize: 60, // Reduced from 80
    mouseForce: 10, // Reduced from 16
  });

  useEffect(() => {
    // Lock scroll on this page only
    const prevHtmlOverflow = document.documentElement.style.overflow;
    const prevBodyOverflow = document.body.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';

    const prefersReduced = typeof window !== 'undefined' && window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      setEnableEffect(false);
      return () => {
        document.documentElement.style.overflow = prevHtmlOverflow;
        document.body.style.overflow = prevBodyOverflow;
      };
    }

    // Tune simulation based on device characteristics
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const small = window.innerWidth < 768;
    setSimProps({
      resolution: small ? 0.3 : 0.5 / dpr, // Even lower resolution for better performance
      iterationsViscous: small ? 8 : 12, // Reduced iterations
      iterationsPoisson: small ? 10 : 16, // Reduced iterations
      cursorSize: small ? 40 : 60, // Smaller cursor
      mouseForce: small ? 6 : 10, // Reduced force
    });

    const run = () => setEnableEffect(true);
    if ('requestIdleCallback' in window) {
      // @ts-ignore
      (window as any).requestIdleCallback(run, { timeout: 800 });
    } else {
      setTimeout(run, 300);
    }
    return () => {
      // Restore scroll when leaving page
      document.documentElement.style.overflow = prevHtmlOverflow;
      document.body.style.overflow = prevBodyOverflow;
    };
  }, []);
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

  // Feature card data
  const featureCards = [
    {
      icon: (
        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      ),
      title: "Smart Banking",
      description: "Experience next-generation banking with AI-powered insights, instant transfers, and intelligent budgeting tools.",
      features: ["Zero-fee transactions", "Real-time notifications", "Advanced security"],
      buttonText: "Start Banking",
      colors: {
        gradientFrom: "#f2a09e",
        gradientTo: "#e89694",
        shadowLight: "#ffcfc8",
        shadowDark: "#d89592"
      }
    },
    {
      icon: (
        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      title: "Investment Platform",
      description: "Build wealth with our automated investment platform. Diversify across stocks, crypto, and retirement accounts.",
      features: ["Zero commission trading", "AI portfolio management", "Tax optimization"],
      buttonText: "Start Investing",
      colors: {
        gradientFrom: "#7B68EE",
        gradientTo: "#6A5ACD",
        shadowLight: "#8b79f0",
        shadowDark: "#6b5acc"
      }
    },
    {
      icon: (
        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      title: "Premium Cards",
      description: "Unlock exclusive rewards and benefits with our premium card offerings. Cashback, travel perks, and more.",
      features: ["Up to 5% cashback", "Travel insurance included", "No foreign fees"],
      buttonText: "Get Premium Card",
      colors: {
        gradientFrom: "#FF6B9D",
        gradientTo: "#FF4081",
        shadowLight: "#ff7cb0",
        shadowDark: "#e85a8a"
      }
    }
  ];

 

  return (
    <div className="relative h-screen overflow-hidden">
      {/* Background Gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-indigo-50/60 to-purple-50/60" style={{ backgroundColor: '#f5f5f5', zIndex: 0 }}></div>
      
      {/* Main Content */}
      <div className="relative h-screen p-1" style={{ zIndex: 10, position: 'relative' }}>
        <div className="h-screen font-sans relative overflow-x-hidden bg-opacity-90 flex flex-col" style={{ backgroundColor: 'transparent' }}>
          {enableEffect && (
            <LiquidEther
              style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1 }}
              colors={['#5227FF', '#FF9FFC', '#B19EEF']}
              resolution={simProps.resolution}
              autoDemo={true}
              autoIntensity={2.3} // Reduced from 2.0 for better performance
              mouseForce={simProps.mouseForce}
              cursorSize={simProps.cursorSize}
              isViscous={false}
              viscous={16} // Reduced from 24
              iterationsViscous={simProps.iterationsViscous}
              iterationsPoisson={simProps.iterationsPoisson}
              dt={0.014}
              BFECC={true}
              isBounce={true}
              autoSpeed={0.6} // Reduced from 0.6
              takeoverDuration={0.25}
              autoResumeDelay={2000} // Increased from 1500 for later activation
              autoRampDuration={0.6}
            />
          )}
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
          {/* Card Navigation */}
          <div className="absolute top-0 left-0 right-0 z-20">
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

        {/* Hero Section */}
        <div className="relative flex-1 w-full">
          <div className="h-full flex flex-col justify-center px-6 lg:px-8">
            <div className="max-w-7xl mx-auto w-full">
              <div className="text-center max-w-4xl mx-auto mb-12">
              <div className="inline-flex items-center px-6 py-3 rounded-full mb-6 neumorphic-inset" style={{ background: 'transparent', boxShadow: 'inset 8px 8px 16px #d0d0d0, inset -8px -8px 16px #ffffff' }}>
                <span className="w-3 h-3 rounded-full mr-3 neumorphic-circle" style={{ background: '#f2a09e', boxShadow: 'inset 2px 2px 4px #d89592, inset -2px -2px 4px #ffcfc8' }}></span>
                <span className="text-sm font-semibold" style={{ color: '#666' }}>Trusted by 50,000+ customers worldwide</span>
              </div>
              <h1 className="text-5xl lg:text-7xl font-bold mb-6 leading-tight" style={{ color: '#333' }}>
                Smart Finance for
                <span className="bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent"> Modern Life</span>
              </h1>
          
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
      </div>
    </div>
    </div>
  );
}
