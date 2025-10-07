"use client";

import dynamic from 'next/dynamic';
import React from 'react';

const LiquidEther = dynamic(() => import('@/components/LiquidEther'), {
  ssr: false,
  loading: () => null,
}) as any;

type AuthShellProps = {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
};

export default function AuthShell({ title, subtitle, children }: AuthShellProps) {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="fixed inset-0 bg-gradient-to-br from-indigo-50/60 to-purple-50/60" style={{ backgroundColor: '#f5f5f5', zIndex: 0 }}></div>
      <div className="relative min-h-screen flex items-center justify-center p-6" style={{ zIndex: 10 }}>
        <div className="absolute inset-0" aria-hidden>
          <LiquidEther
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 1 }}
            colors={["#5227FF", "#FF9FFC", "#B19EEF"]}
            resolution={0.4}
            autoDemo={true}
            autoIntensity={2.0}
            mouseForce={8}
            cursorSize={50}
            isViscous={false}
            viscous={16}
            iterationsViscous={10}
            iterationsPoisson={14}
            dt={0.014}
            BFECC={true}
            isBounce={false}
            autoSpeed={0.6}
            takeoverDuration={0.25}
            autoResumeDelay={1600}
            autoRampDuration={0.6}
          />
        </div>

        <div className="relative z-20 w-full max-w-md">
          <div className="rounded-3xl p-8" style={{ background: '#f0f0f0', boxShadow: '16px 16px 32px #d0d0d0, -16px -16px 32px #ffffff' }}>
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)', boxShadow: '8px 8px 16px #6b5acc, -8px -8px 16px #8b79f0' }}>
                <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 1v22" />
                  <path d="M5 5h14v14H5z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-gray-800">{title}</h1>
              {subtitle && <p className="text-gray-600 mt-1">{subtitle}</p>}
            </div>
            {children}
          </div>
          <div className="text-center text-sm text-gray-500 mt-4">
            <span className="inline-flex items-center px-3 py-1 rounded-full" style={{ background: '#ededed', boxShadow: 'inset 6px 6px 12px #d8d8d8, inset -6px -6px 12px #ffffff' }}>
              Secure by design
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}





