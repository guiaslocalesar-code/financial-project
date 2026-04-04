/** @type {import('next').NextConfig} */
const nextConfig = {
    // output: 'standalone', // Disabled for Vercel compatibility in monorepo
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'api.guiaslocales.com.ar',
                pathname: '/uploads/**',
            },
            {
                protocol: 'https',
                hostname: 'storage.googleapis.com',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'fumejzkghviszmyfjegg.supabase.co',
                pathname: '/storage/v1/object/public/**',
            },
            {
                protocol: 'http',
                hostname: 'localhost',
                port: '4000',
                pathname: '/uploads/**',
            },
        ],
    },
    // Proxy API requests to backends
    async rewrites() {
        const authBackendUrl = process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:4000';
        const financeBackendUrl = process.env.NEXT_PUBLIC_FINANCE_API_URL || 'http://127.0.0.1:8000';
        return [
            // Auth routes → Node.js backend (cutguias)
            {
                source: '/auth/:path*',
                destination: `${authBackendUrl}/auth/:path*`,
            },
            // Main API routes → Node.js backend (cutguias)
            {
                source: '/api/v1/:path*',
                destination: `${authBackendUrl}/api/v1/:path*`,
            },
            // Finance API routes → Python backend (FastAPI)
            {
                source: '/finance-api/:path*',
                destination: `${financeBackendUrl}/api/v1/:path*`,
            },
        ];
    },
}

module.exports = nextConfig
