import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy API requests from the Next.js dev server to the FastAPI backend
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
