// components/FeatureCard.tsx
import React from 'react';

type FeatureCardProps = {
  icon: React.ReactNode;
  title: string;
  description: string;
  features: string[];
  buttonText: string;
  colors: {
    gradientFrom: string;
    gradientTo: string;
    shadowLight: string;
    shadowDark: string;
  };
};

const FeatureCard = ({ icon, title, description, features, buttonText, colors }: FeatureCardProps) => (
  <div className="neumorphic-card rounded-3xl p-8 transition-all group" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
    <div
      className="flex items-center justify-center w-20 h-20 rounded-3xl mb-6 mx-auto neumorphic-icon"
      style={{
        background: `linear-gradient(135deg, ${colors.gradientFrom} 0%, ${colors.gradientTo} 100%)` ,
        boxShadow: `8px 8px 16px ${colors.shadowDark}, -8px -8px 16px ${colors.shadowLight}` ,
      }}
    >
      {icon}
    </div>
    <h3 className="text-2xl font-bold mb-4 text-center text-gray-800">{title}</h3>
    <p className="leading-relaxed text-center mb-6 text-gray-600">{description}</p>
    <div className="space-y-4 mb-8">
      {features.map((feature, index) => (
        <div key={index} className="flex items-center text-sm text-gray-600">
          <div className="w-2 h-2 rounded-full mr-3 neumorphic-dot" style={{ background: '#4ade80', boxShadow: 'inset 1px 1px 2px #3bb370, inset -1px -1px 2px #61eb90' }}></div>
          {feature}
        </div>
      ))}
    </div>
    <button
      className="w-full py-4 rounded-xl font-semibold text-white transition-all neumorphic-button"
      style={{
        background: `linear-gradient(135deg, ${colors.gradientFrom} 0%, ${colors.gradientTo} 100%)` ,
        boxShadow: `8px 8px 16px ${colors.shadowDark}, -8px -8px 16px ${colors.shadowLight}` ,
      }}
    >
      {buttonText}
    </button>
  </div>
);

export default FeatureCard;
