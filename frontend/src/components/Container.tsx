import React, { PropsWithChildren } from 'react';

export default function Container({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#ece9f0] via-[#eef1ff] to-[#e7e6ff] py-8">
      <div className="mx-auto max-w-7xl px-6">
        <div className="rounded-[32px] bg-white/80 backdrop-blur border border-black/5 shadow-[0_20px_60px_rgba(50,50,93,0.12)] overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  );
}
