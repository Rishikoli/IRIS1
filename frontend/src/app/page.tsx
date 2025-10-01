// Define TypeScript interfaces
interface DotGridProps {
  dotSize: number;
  gap: number;
  baseColor: string;
  activeColor: string;
  proximity: number;
  shockRadius: number;
  shockStrength: number;
  resistance: number;
  returnDuration: number;
}

interface OrbProps {
  hoverIntensity: number;
  rotateOnHover: boolean;
  hue: number;
  forceHoverState: boolean;
}

// DotGrid Placeholder Component
const DotGrid: React.FC<DotGridProps> = ({ 
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
const Orb: React.FC<OrbProps> = ({ hoverIntensity, rotateOnHover, hue, forceHoverState }) => {
  return (
    <div className="relative w-80 h-80 flex items-center justify-center">
      {/* Three.js visualizer code will be implemented here */}
      <div className="w-64 h-64 rounded-full bg-gradient-to-br from-purple-200 via-blue-200 to-pink-200 shadow-2xl opacity-80 animate-pulse"></div>
    </div>
  );
};

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30 relative overflow-hidden">
      {/* Background gradient blobs matching the original */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-gradient-to-br from-yellow-300/40 via-orange-300/30 to-yellow-400/40 rounded-full blur-3xl transform -translate-x-48 -translate-y-48"></div>
        <div className="absolute top-1/4 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-pink-300/40 via-purple-300/30 to-blue-300/40 rounded-full blur-3xl transform translate-x-32"></div>
        <div className="absolute bottom-0 left-1/3 w-[400px] h-[400px] bg-gradient-to-tr from-cyan-300/30 via-blue-300/30 to-purple-300/30 rounded-full blur-3xl transform translate-y-32"></div>
      </div>

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
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Proper Navigation Bar */}
        <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-8">
            <div className="flex items-center justify-between h-20">
              {/* Logo */}
              <div className="flex items-center">
                <div className="text-3xl font-bold text-black">iris</div>
              </div>

              {/* Center Navigation Links */}
              <div className="hidden md:flex items-center space-x-12">
                <a href="#" className="text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors relative group">
                  About
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
                </a>
                <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors relative group">
                  Accessories
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
                </a>
                <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors relative group">
                  API
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
                </a>
                <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors relative group">
                  Blog
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
                </a>
                <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors relative group">
                  Services
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
                </a>
              </div>

              {/* Right Side - Actions & User */}
              <div className="flex items-center space-x-6">
                {/* Search Button */}
                <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>

                {/* Notifications */}
                <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors relative">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5-5 5-5h-5m-6 10v-2a6 6 0 10-12 0v2l-2 2h16l-2-2z" />
                  </svg>
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

                {/* User Profile */}
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                      <span className="text-white text-xs font-medium">A</span>
                    </div>
                    <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                      <span className="text-white text-xs font-medium">C</span>
                    </div>
                  </div>
                  <span className="text-sm text-gray-700 font-medium">Hello, Maria!</span>
                  <div className="w-10 h-10 rounded-full overflow-hidden ring-2 ring-gray-200 hover:ring-blue-300 transition-all cursor-pointer">
                    <img 
                      src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face" 
                      alt="User avatar" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>

                {/* Mobile menu button */}
                <button className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content Area - Centered Layout */}
        <div className="flex-1 flex items-center">
          <div className="w-full px-16">
            <div className="grid grid-cols-2 gap-24 items-center max-w-7xl mx-auto">
              {/* Left Side - Text Content */}
              <div className="space-y-10">
                <div className="text-sm text-gray-600 uppercase tracking-wider font-medium">
                  Workflow management
                </div>
                
                <h1 className="text-6xl font-bold text-black leading-tight">
                  Technical Aspects of<br />
                  Brain Rhythms and<br />
                  Breathing Disorder
                </h1>
                
                <button className="inline-flex items-center px-10 py-4 bg-white border-2 border-gray-900 rounded-full text-sm font-medium text-gray-900 hover:bg-gray-50 transition-colors shadow-sm">
                  Join Community
                  <svg className="ml-3 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </button>
              </div>

              {/* Right Side - Brain Visualization */}
              <div className="flex justify-center relative">
                <div className="relative w-96 h-96">
                  {/* Main brain sphere */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white via-gray-100 to-gray-200 rounded-full shadow-2xl"></div>
                  <div className="absolute inset-4 bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 rounded-full shadow-inner"></div>
                  <div className="absolute inset-8 bg-gradient-to-br from-white via-gray-50 to-blue-50 rounded-full"></div>
                  <div className="absolute inset-12 bg-gradient-to-br from-gray-100 via-gray-50 to-white rounded-full opacity-90"></div>
                  
                  {/* Brain details/texture */}
                  <div className="absolute inset-16 bg-gradient-to-br from-gray-200 via-gray-100 to-gray-50 rounded-full opacity-80"></div>
                  <div className="absolute top-20 left-24 w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full opacity-60"></div>
                  <div className="absolute top-32 right-20 w-12 h-12 bg-gradient-to-br from-purple-100 to-purple-200 rounded-full opacity-50"></div>
                  
                  {/* Surrounding colorful glow */}
                  <div className="absolute -inset-8 bg-gradient-to-br from-yellow-200/40 via-pink-200/40 to-purple-200/40 rounded-full blur-2xl"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section - Data Cards */}
        <div className="px-16 pb-16">
          <div className="grid grid-cols-3 gap-8 max-w-7xl mx-auto">
            {/* Left Card - 3D Sphere with FEATURES label */}
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-lg border border-white/50 relative">
              <div className="flex items-center justify-center h-32 mb-4">
                <div className="w-24 h-24 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full shadow-xl relative">
                  <div className="absolute inset-2 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full"></div>
                  <div className="absolute top-4 left-5 w-2 h-2 bg-gray-400 rounded-full opacity-60"></div>
                  <div className="absolute top-7 right-4 w-1.5 h-1.5 bg-gray-400 rounded-full opacity-40"></div>
                  <div className="absolute bottom-5 left-7 w-1 h-1 bg-gray-400 rounded-full opacity-50"></div>
                  <div className="absolute top-12 left-8 w-1.5 h-1.5 bg-gray-400 rounded-full opacity-30"></div>
                  <div className="absolute bottom-8 right-6 w-1 h-1 bg-gray-400 rounded-full opacity-40"></div>
                </div>
              </div>
              <div className="absolute left-4 top-1/2 transform -translate-y-1/2 -rotate-90 text-xs text-gray-500 font-medium tracking-[0.2em]">
                FEATURES
              </div>
            </div>

            {/* Middle Card - Person Image */}
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-lg border border-white/50">
              <div className="flex items-center justify-center h-32 mb-4">
                <div className="w-24 h-24 rounded-full overflow-hidden shadow-xl">
                  <img 
                    src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=96&h=96&fit=crop&crop=face" 
                    alt="Person" 
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>

            {/* Right Card - Delta Brain Waves */}
            <div className="bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-3xl p-8 shadow-lg">
              <div className="flex items-center justify-between mb-8">
                <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center">
                  <div className="w-4 h-4 bg-white rounded-full"></div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="text-5xl font-bold text-black">3.2Hz</div>
                <div className="text-base font-semibold text-black">Delta Brain Waves</div>
                <div className="text-sm text-gray-800 leading-relaxed">
                  Various regions of the brain do not work the same brain wave
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Neurofeedback Card - Bottom Right */}
        <div className="absolute bottom-16 right-16 bg-white/90 backdrop-blur-sm rounded-3xl p-8 shadow-xl w-72 border border-white/50">
          <div className="flex items-center justify-between mb-6">
            <div className="text-base font-semibold text-gray-900">Neurofeedback</div>
          </div>
          <div className="flex items-center justify-center">
            <div className="relative w-28 h-28">
              <svg className="w-28 h-28 transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#E5E7EB"
                  strokeWidth="3"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#FCD34D"
                  strokeWidth="3"
                  strokeDasharray="78, 100"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-3xl font-bold text-gray-900">78%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
