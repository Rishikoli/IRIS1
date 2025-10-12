import type { NextConfig } from "next";

// next.config.js
const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "connect-src 'self' http://localhost:8000 https://rsyyqooksg.supabase.co ws://localhost:8000;",
          },
        ],
      },
    ];
  },
};