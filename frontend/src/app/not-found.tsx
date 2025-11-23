import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50/60 to-purple-50/60 p-6">
      <div className="w-full max-w-2xl mx-auto text-center">
        {/* Animated 404 Text */}
        <div className="relative mb-8">
          <h1 className="text-9xl font-bold text-gray-800 opacity-10">404</h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <h2 className="text-5xl font-bold text-indigo-600">Page Not Found</h2>
          </div>
        </div>

        {/* Error Message */}
        <p className="text-xl text-gray-600 mb-8">
          Oops! The page you're looking for doesn't exist or has been moved.
        </p>

        {/* Search Bar */}
        <div className="max-w-md mx-auto mb-10">
          <div className="relative">
            <input
              type="text"
              placeholder="Search I.R.I.S..."
              className="w-full px-6 py-4 pr-12 rounded-2xl border-0 shadow-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all duration-200"
            />
            <button className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-indigo-600">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link 
            href="/"
            className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-indigo-200"
          >
            Return Home
          </Link>
          <Link 
            href="/contact"
            className="px-8 py-4 bg-white hover:bg-gray-50 text-indigo-600 font-semibold rounded-xl border-2 border-indigo-100 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-indigo-100"
          >
            Contact Support
          </Link>
        </div>

        {/* Decorative Elements */}
        <div className="mt-16 flex justify-center space-x-4 opacity-75">
          {[1, 2, 3].map((i) => (
            <div 
              key={i}
              className="w-3 h-3 rounded-full bg-indigo-200 animate-bounce"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
