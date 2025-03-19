import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL || 'https://localhost:8000/api/:path*',
      },
    ];
  },
  // This helps with HTTPS in development
  webpack: (config, { dev }) => {
    if (dev) {
      // Ensure the Node.js environment variable is respected
      config.resolve.fallback = { 
        ...config.resolve.fallback, 
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

export default nextConfig;
