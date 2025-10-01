import React from 'react';

export default function Header() {
  return (
    <header className="w-full max-w-7xl mx-auto flex items-center justify-between px-6 py-5">
      {/* Left: logo */}
      <div className="flex items-center gap-2 select-none">
        <div className="w-8 h-8 rounded-md bg-gradient-to-br from-purple-500 to-blue-500" />
        <div className="leading-tight">
          <div className="text-xs tracking-[0.3em] font-semibold">BRAIN</div>
          <div className="text-xs tracking-[0.3em] font-semibold">WAVE</div>
        </div>
      </div>

      {/* Center: nav */}
      <nav className="hidden md:flex items-center gap-8 text-[15px] text-neutral-700">
        <a className="relative font-medium text-black after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-full after:rounded-full after:bg-black" href="#">Home</a>
        <a className="hover:text-black/60" href="#">About Us</a>
        <a className="hover:text-black/60" href="#">Products</a>
        <a className="hover:text-black/60" href="#">Services</a>
        <a className="hover:text-black/60" href="#">Contact Us</a>
      </nav>

      {/* Right: icons */}
      <div className="flex items-center gap-3">
        <button aria-label="Search" className="w-9 h-9 rounded-full border border-black/10 bg-white/70 backdrop-blur hover:bg-white transition-colors flex items-center justify-center">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </button>
        <button aria-label="Account" className="w-9 h-9 rounded-full border border-black/10 bg-white/70 backdrop-blur hover:bg-white transition-colors flex items-center justify-center">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21a8 8 0 1 0-16 0"/><circle cx="12" cy="7" r="4"/></svg>
        </button>
      </div>
    </header>
  );
}
