"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import CardNav from "@/components/CardNav";
// Lazy-load heavy WebGL background to reduce initial JS
const LiquidEther = dynamic(() => import('@/components/LiquidEther'), {
  ssr: false,
  loading: () => null,
}) as any;




export default function Home() {
  const router = useRouter();
  const [currentSlide, setCurrentSlide] = useState(0);
  
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
      label: "Home",
      bgColor: "#f2a09e",
      textColor: "#ffffff",
      links: [
        { label: "About IRIS", href: "#about", ariaLabel: "About IRIS Platform" },
        { label: "Features", href: "#features", ariaLabel: "Platform Features" },
        { label: "Documentation", href: "#docs", ariaLabel: "Documentation" }
      ]
    },
    {
      label: "Analytics",
      bgColor: "#7B68EE",
      textColor: "#ffffff",
      links: [
        { label: "Forensic Analysis", href: "/iris", ariaLabel: "Forensic Analysis Dashboard" },
        { label: "Risk Assessment", href: "/iris", ariaLabel: "Risk Assessment Tools" },
        { label: "Compliance Check", href: "/iris", ariaLabel: "Compliance Validation" }
      ]
    },
    {
      label: "Resources",
      bgColor: "#FF6B9D",
      textColor: "#ffffff",
      links: [
        { label: "API Documentation", href: "#api", ariaLabel: "API Documentation" },
        { label: "Tutorials", href: "#tutorials", ariaLabel: "Tutorials" },
        { label: "Support", href: "#support", ariaLabel: "Support" }
      ]
    }
  ];

  // Carousel data
  const carouselSlides = [
    {
      id: 0,
      title: "Forensic Analysis",
      description: "Comprehensive financial statement analysis including vertical, horizontal, and ratio analysis with 29 comprehensive forensic metrics.",
      features: [
        "29 Forensic metrics",
        "Real-time data from Yahoo Finance",
        "Altman Z-Score & Beneish M-Score"
      ],
      buttonText: "Launch Forensic Analysis",
      icon: <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
      </svg>,
      colors: {
        gradientFrom: "#f2a09e",
        gradientTo: "#e89694",
        shadowLight: "#ffcfc8",
        shadowDark: "#d89592"
      }
    },
    {
      id: 1,
      title: "Anomaly Detection",
      description: "Advanced algorithms to detect irregularities and potential financial manipulation using statistical methods and pattern recognition.",
      features: [
        "Benford's Law analysis",
        "Statistical fraud detection",
        "Pattern irregularity detection"
      ],
      buttonText: "Detect Anomalies",
      icon: <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>,
      colors: {
        gradientFrom: "#7B68EE",
        gradientTo: "#6A5ACD",
        shadowLight: "#8b79f0",
        shadowDark: "#6b5acc"
      }
    },
    {
      id: 2,
      title: "Risk Assessment",
      description: "Multi-factor risk scoring with confidence levels and detailed risk factor analysis across six comprehensive categories.",
      features: [
        "6-category weighted scoring",
        "Investment recommendations",
        "Confidence level scoring"
      ],
      buttonText: "Calculate Risk Score",
      icon: <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>,
      colors: {
        gradientFrom: "#FF6B9D",
        gradientTo: "#FF4081",
        shadowLight: "#ff7cb0",
        shadowDark: "#e85a8a"
      }
    }
  ];

  // Auto-play carousel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % carouselSlides.length);
    }, 1500);
    return () => clearInterval(timer);
  }, [carouselSlides.length]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % carouselSlides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + carouselSlides.length) % carouselSlides.length);
  };

 

  return (
    <div className="relative h-screen overflow-hidden">
      {/* Background Gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-indigo-50/60 to-purple-50/60" style={{ backgroundColor: '#f5f5f5', zIndex: 0 }} />
      
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
          `}</style>

          <div className="relative flex-1 w-full">
            <div className="h-full flex items-center px-6 lg:px-12">
              <div className="max-w-7xl mx-auto w-full">
          {/* Split Layout: Hero Left, Carousel Right */}
                <div className="flex flex-col lg:flex-row items-center gap-16 mb-12">
                  {/* Left Hero Content */}
                  <div className="flex-1 space-y-8">
            <div className="inline-flex items-center px-6 py-3 rounded-full mb-6 neumorphic-inset" style={{ background: 'transparent', boxShadow: 'inset 8px 8px 16px #d0d0d0, inset -8px -8px 16px #ffffff' }}>
                      <span className="w-3 h-3 rounded-full mr-3 neumorphic-circle" style={{ background: '#f2a09e', boxShadow: 'inset 2px 2px 4px #d89592, inset -2px -2px 4px #ffcfc8' }} />
                      <span className="text-sm font-semibold" style={{ color: '#666' }}>AI-Powered Financial Forensics Platform</span>
                    </div>
                    <h1 className="text-4xl lg:text-6xl font-bold mb-6 leading-tight" style={{ color: '#333' }}>
                      Investment Risk Intelligence
                      <span className="bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent"> System (IRIS)</span>
                    </h1>
                    <p className="text-lg lg:text-xl mb-8 leading-relaxed" style={{ color: '#666' }}>
                      Comprehensive financial forensics platform for analyzing Indian public companies with fraud detection, risk assessment, and regulatory compliance powered by AI/ML
                    </p>
            </div>
                  {/* End Left Hero Content */}

                  {/* Quick Action Buttons */}
                  <div className="flex gap-4">
                    <button 
                      onClick={() => router.push('/iris')}
                      className="px-8 py-4 rounded-xl font-semibold text-white transition-all neumorphic-button cursor-pointer" 
                      style={{ background: 'linear-gradient(135deg, #f2a09e 0%, #e89694 100%)', boxShadow: '8px 8px 16px #d89592, -8px -8px 16px #ffcfc8' }}
                    >
                      Launch Dashboard
                    </button>
                    <button 
                      className="px-8 py-4 rounded-xl font-semibold transition-all neumorphic-button cursor-pointer" 
                      style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff', color: '#666' }}
                    >
                      Learn More
                    </button>
                  </div>
                  {/* End Left Hero Content */}

                  {/* Right Carousel Section */}
                  <div className="flex-1 max-w-2xl w-full">
              {/* Carousel Card */}
                    <div className="w-full">
                      <div 
                        className="neumorphic-card rounded-3xl p-8 transition-all duration-500"
                        style={{ 
                          background: '#f0f0f0', 
                          boxShadow: '16px 16px 32px #d0d0d0, -16px -16px 32px #ffffff',
                          transform: 'translateY(0)',
                        }}
                      >
                  <div 
                          className="flex items-center justify-center w-24 h-24 rounded-3xl mb-8 mx-auto neumorphic-icon" 
                          style={{ 
                            background: 'linear-gradient(135deg, ' + carouselSlides[currentSlide].colors.gradientFrom + ' 0%, ' + carouselSlides[currentSlide].colors.gradientTo + ' 100%)', 
                            boxShadow: '8px 8px 16px ' + carouselSlides[currentSlide].colors.shadowDark + ', -8px -8px 16px ' + carouselSlides[currentSlide].colors.shadowLight
                          }}
                        >
                          {carouselSlides[currentSlide].icon}
                        </div>
                        <h3 className="text-3xl font-bold mb-6 text-center" style={{ color: '#333' }}>
                          {carouselSlides[currentSlide].title}
                        </h3>
                        <p className="text-lg leading-relaxed text-center mb-8" style={{ color: '#666' }}>
                          {carouselSlides[currentSlide].description}
                        </p>

                  {/* Visual Stats/Numbers */}
                        <div className="grid grid-cols-3 gap-4 mb-8">
                          {carouselSlides[currentSlide].features.map((feature, index) => (
                            <div 
                              key={index}
                              className="neumorphic-inset rounded-2xl p-4 text-center"
                              style={{ background: 'transparent', boxShadow: 'inset 4px 4px 8px #d0d0d0, inset -4px -4px 8px #ffffff' }}
                            >
                              <div className="text-2xl font-bold mb-1" style={{ color: carouselSlides[currentSlide].colors.gradientFrom }}>
                                {index === 0 ? '29' : index === 1 ? '100%' : '6'}
                              </div>
                              <div className="text-xs" style={{ color: '#999' }}>
                                {index === 0 ? 'Metrics' : index === 1 ? 'Real-time' : 'Categories'}
                              </div>
                            </div>
                          ))}
                        </div>

                  <button 
                          onClick={() => router.push('/iris')}
                          className="w-full py-4 rounded-xl font-semibold text-white transition-all neumorphic-button cursor-pointer" 
                          style={{ 
                            background: 'linear-gradient(135deg, ' + carouselSlides[currentSlide].colors.gradientFrom + ' 0%, ' + carouselSlides[currentSlide].colors.gradientTo + ' 100%)', 
                            boxShadow: '8px 8px 16px ' + carouselSlides[currentSlide].colors.shadowDark + ', -8px -8px 16px ' + carouselSlides[currentSlide].colors.shadowLight
                          }}
                        >
                          {carouselSlides[currentSlide].buttonText}
                        </button>
                      </div>

                {/* Carousel Navigation Below Card */}
                      <div className="flex items-center justify-center gap-6 mt-8">
                        <button 
                          onClick={prevSlide}
                          className="w-12 h-12 rounded-full flex items-center justify-center transition-all neumorphic-button"
                          style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}
                          aria-label="Previous slide"
                        >
                          <svg className="w-6 h-6" style={{ color: '#666' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                          </svg>
                        </button>

                  {/* Slide Indicators */}
                        <div className="flex gap-3">
                          {carouselSlides.map((_, index) => (
                            <button
                              key={index}
                              onClick={() => setCurrentSlide(index)}
                              className="transition-all"
                              style={{
                                width: currentSlide === index ? '40px' : '12px',
                                height: '12px',
                                borderRadius: '6px',
                                background: currentSlide === index ? carouselSlides[index].colors.gradientFrom : '#d0d0d0',
                                boxShadow: currentSlide === index ? 'inset 2px 2px 4px rgba(0,0,0,0.1)' : 'none'
                              }}
                              aria-label={'Go to slide ' + (index + 1)}
                            />
                          ))}
                        </div>

                  <button 
                          onClick={nextSlide}
                          className="w-12 h-12 rounded-full flex items-center justify-center transition-all neumorphic-button"
                          style={{ background: '#f0f0f0', boxShadow: '8px 8px 16px #d0d0d0, -8px -8px 16px #ffffff' }}
                          aria-label="Next slide"
                        >
                          <svg className="w-6 h-6" style={{ color: '#666' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      </div>
                      {/* End Carousel Navigation */}
                    </div>
                    {/* End Carousel Card */}
                  </div>
                  {/* End Right Carousel Section */}
                </div>
                {/* End Split Layout */}
              </div>
              {/* End max-w-7xl */}
            </div>
            {/* End h-full flex items-center */}
          </div>
          {/* End relative flex-1 w-full */}
        </div>
        {/* End h-screen font-sans */}
      </div>
      {/* End Main Content */}
    </div>
  );
}

