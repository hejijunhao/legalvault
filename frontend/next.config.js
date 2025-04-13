if (process.env.NODE_ENV === 'production' && !process.env.NEXT_PUBLIC_API_URL) {
  throw new Error('NEXT_PUBLIC_API_URL is required in production');
}

const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development'
          ? 'http://localhost:8000/api/:path*'
          : `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
  webpack: (config, { dev }) => {
    if (dev) {
      config.resolve.fallback = { 
        ...config.resolve.fallback, 
        net: false,
        tls: false,
      };
    }
    return config;
  },
  serverRuntimeConfig: {
    https: process.env.NODE_ENV === 'development' ? {
      rejectUnauthorized: false
    } : undefined
  },
  publicRuntimeConfig: {
    apiUrl: process.env.NEXT_PUBLIC_API_URL
  },
  eslint: {
    ignoreDuringBuilds: true
  },
};

module.exports = nextConfig;