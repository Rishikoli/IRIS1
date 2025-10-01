import Header from '@/components/Header';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#ece9f0] via-[#eef1ff] to-[#e7e6ff] py-8">
      {/* Outer panel */}
      <div className="mx-auto max-w-7xl px-6">
        <div className="rounded-[32px] bg-white/80 backdrop-blur border border-black/5 shadow-[0_20px_60px_rgba(50,50,93,0.12)] overflow-hidden">
          {/* Header inside panel */}
          <div className="px-4 sm:px-6 pt-4">
            <Header />
          </div>
          <div className="h-px w-full bg-black/5" />

          {/* Content */}
          <main className="px-4 sm:px-6 pb-8 pt-6">
            {/* Top hero grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left white card */}
          <section className="bg-white rounded-[28px] p-8 sm:p-10 shadow-[0_20px_60px_rgba(0,0,0,0.05)]">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-black">
              Unleash Your
              <br />Potential With
              <br />BrainWave
              <br />Technologies
            </h1>
            <p className="mt-6 text-neutral-600 max-w-xl">
              Experience the next frontier of human capability. Harness the power of your mind through cutting‑edge BrainWave solutions.
            </p>
            <button className="mt-8 inline-flex items-center gap-3 bg-black text-white rounded-full px-6 py-3 shadow hover:bg-black/90">
              <span className="text-sm font-medium">Explore Services</span>
              <span className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 6l6 6-6 6" /></svg>
              </span>
            </button>
          </section>

          {/* Right image card */}
          <section className="relative rounded-[28px] overflow-hidden min-h-[420px] shadow-[0_30px_70px_rgba(31,38,135,0.2)]">
            <img
              src="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=1616&auto=format&fit=crop"
              alt="Brain"
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#7b61ff]/55 via-transparent to-transparent" />

            <div className="relative z-10 p-8 sm:p-10 h-full flex items-end">
              <div className="w-full">
                <h2 className="text-white text-2xl sm:text-3xl font-semibold">Innovate Your Mind, Elevate Your World</h2>
                <p className="mt-2 text-white/90 max-w-md text-sm">
                  Discover limitless potential at BrainWave Technologies, where cutting‑edge neurotech converges to amplify minds.
                </p>
                <button className="mt-4 ml-auto flex items-center justify-center w-10 h-10 rounded-full bg-white/30 border border-white/40 text-white hover:bg-white/40 transition">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 6l6 6-6 6" /></svg>
                </button>
              </div>
            </div>
          </section>
        </div>

        {/* Bottom small promo card (left) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <section className="bg-white rounded-[22px] p-5 shadow-[0_14px_36px_rgba(50,50,93,0.08)] border border-black/5 flex items-center gap-4">
            <div className="w-20 h-16 rounded-[18px] overflow-hidden">
              <img src="https://images.unsplash.com/photo-1557672172-298e090bd0f1?q=80&w=900&auto=format&fit=crop" alt="Abstract" className="w-full h-full object-cover" />
            </div>
            <div>
              <h3 className="text-[17px] font-semibold tracking-tight">Revolutionizing Minds, Transforming Futures</h3>
              <p className="text-[13px] text-neutral-600">Delve into a realm of endless potential, elevate cognitive performance.</p>
              <a className="inline-block mt-1 text-[13px] font-medium underline" href="#">Learn more</a>
            </div>
          </section>
        </div>
          </main>
        </div>
      </div>
    </div>
  );
}
