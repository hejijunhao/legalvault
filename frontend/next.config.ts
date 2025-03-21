import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development'
          ? 'https://localhost:8000/api/:path*'  // Use HTTPS in development
          : (process.env.NEXT_PUBLIC_API_URL || 'https://localhost:8000/api/:path*'),
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
  // Disable SSL certificate verification in development
  serverRuntimeConfig: {
    // Will only be available on the server side
    https: process.env.NODE_ENV === 'development' ? {
      rejectUnauthorized: false
    } : undefined
  },
  publicRuntimeConfig: {
    // Will be available on both server and client
    apiUrl: process.env.NODE_ENV === 'development' ? 'http://localhost:8000/api' : process.env.NEXT_PUBLIC_API_URL
  },
};

export default nextConfig;
