import React from 'react';

// DotGrid Placeholder Component
const DotGrid = ({ 
  dotSize, 
  gap, 
  baseColor, 
  activeColor, 
  proximity, 
  shockRadius, 
  shockStrength, 
  resistance, 
  returnDuration 
}) => {
  return (
    <div className="absolute inset-0 w-full h-full pointer-events-none">
      {/* Custom canvas code will go here */}
      <div className="w-full h-full bg-gradient-to-br from-purple-50/30 to-blue-50/30"></div>
    </div>
  );
};

// Orb Placeholder Component
const Orb = ({ hoverIntensity, rotateOnHover, hue, forceHoverState }) => {
  return (
    <div className="relative w-80 h-80 flex items-center justify-center">
      {/* Three.js visualizer code will be implemented here */}
      <div className="w-64 h-64 rounded-full bg-gradient-to-br from-purple-200 via-blue-200 to-pink-200 shadow-2xl opacity-80 animate-pulse"></div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="min-h-screen bg-gray-50 relative overflow-hidden">
      {/* DotGrid Background */}
      <DotGrid 
        dotSize={10}
        gap={15}
        baseColor="#5227FF"
        activeColor="#5227FF"
        proximity={120}
        shockRadius={250}
        shockStrength={5}
        resistance={750}
        returnDuration={1.5}
      />

      {/* Main Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="flex items-center justify-between px-8 py-6">
          {/* Logo */}
          <div className="flex items-center space-x-8">
            <div className="text-2xl font-bold text-black">iris</div>
            
            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8 text-sm text-gray-600">
              <a href="#" className="hover:text-black transition-colors">About</a>
              <a href="#" className="hover:text-black transition-colors">Accessories</a>
              <a href="#" className="hover:text-black transition-colors">API</a>
              <a href="#" className="hover:text-black transition-colors">Blog</a>
              <a href="#" className="hover:text-black transition-colors">Services</a>
            </nav>
          </div>

          {/* Right Side - User Section */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-medium">A</span>
              </div>
              <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-medium">C</span>
              </div>
            </div>
            <span className="text-sm text-gray-600">Hello, Maria !</span>
            <div className="w-10 h-10 rounded-full overflow-hidden">
              <img 
                src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face" 
                alt="User avatar" 
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </header>

        {/* Floating Notifications - Top Right */}
        <div className="absolute top-20 right-8 space-y-3 z-20">
          <div className="bg-yellow-100 rounded-lg p-3 shadow-lg max-w-xs">
            <div className="flex items-center justify-between">
              <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
              <span className="text-xs text-gray-600">2 Hour</span>
            </div>
            <div className="mt-1">
              <div className="text-sm font-medium text-gray-900">Meeting</div>
              <div className="text-xs text-gray-600">We need to discuss the presentation.</div>
            </div>
          </div>
          
          <div className="bg-orange-100 rounded-lg p-3 shadow-lg max-w-xs">
            <div className="flex items-center justify-between">
              <div className="w-3 h-3 bg-orange-400 rounded-full"></div>
              <span className="text-xs text-gray-600">2 Hour</span>
            </div>
            <div className="mt-1">
              <div className="text-sm font-medium text-gray-900">New Email</div>
              <div className="text-xs text-gray-600">We need to check the presentation.</div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="px-8 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Side - Text Content */}
            <div className="space-y-8">
              <div className="text-sm text-gray-500 uppercase tracking-wide">
                Workflow management
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-bold text-black leading-tight">
                Technical Aspects of Brain Rhythms and Breathing Disorder
              </h1>
              
              <button className="inline-flex items-center px-8 py-3 bg-white border border-gray-300 rounded-full text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                Join Community
                <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
            </div>

            {/* Right Side - Orb Component */}
            <div className="flex justify-center">
              <Orb 
                hoverIntensity={0.5}
                rotateOnHover={true}
                hue={0}
                forceHoverState={false}
              />
            </div>
          </div>
        </div>

        {/* Bottom Section - Data Cards */}
        <div className="px-8 pb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Left Card - 3D Sphere */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="flex items-center justify-center h-32 mb-4">
                <div className="w-20 h-20 bg-gray-200 rounded-full shadow-lg"></div>
              </div>
              <div className="text-xs text-gray-500 transform -rotate-90 absolute left-4 top-1/2">
                FEATURES
              </div>
            </div>

            {/* Middle Card - Person Image */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="flex items-center justify-center h-32 mb-4">
                <div className="w-20 h-20 rounded-full overflow-hidden">
                  <img 
                    src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&crop=face" 
                    alt="Person" 
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>

            {/* Right Card - Delta Brain Waves */}
            <div className="bg-yellow-200 rounded-2xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                  <div className="w-4 h-4 bg-white rounded-full"></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-3xl font-bold text-black">3.2Hz</div>
                <div className="text-sm font-medium text-black">Delta Brain Waves</div>
                <div className="text-xs text-gray-700">
                  Various regions of the brain do not work the same brain wave
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Neurofeedback Card - Bottom Right */}
        <div className="absolute bottom-8 right-8 bg-white rounded-2xl p-6 shadow-lg max-w-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-medium text-gray-900">Neurofeedback</div>
          </div>
          <div className="flex items-center justify-center mb-4">
            <div className="relative w-20 h-20">
              <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#E5E7EB"
                  strokeWidth="2"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#FCD34D"
                  strokeWidth="2"
                  strokeDasharray="78, 100"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-gray-900">78%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
