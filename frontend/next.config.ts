import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  devIndicators: {
    buildActivity: false,
    appIsrStatus: false,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      {
        source: '/qa-api/:path*',
        destination: 'http://127.0.0.1:8000/qa-api/:path*',
      },
      {
        source: '/qa-api-2/:path*',
        destination: 'http://127.0.0.1:8000/qa-api-2/:path*',
      },
    ];
  },
};

export default nextConfig;