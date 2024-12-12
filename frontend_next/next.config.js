const { config } = require('localforage');

/** @type {import('next').NextConfig} */
const nextConfig = {
    // TODO Start: [Student] Enable standalone build
    output: "standalone",
    // TODO End
    reactStrictMode: false, /* @note: To prevent duplicated call of useEffect */
    swcMinify: true,

    async rewrites() {
        return [{
            source: "/api/:path*",
            // TODO Start: [Student] Change to standard backend URL
            destination: "https://127.0.0.1:8001/api/:path*",
            // TODO End
        }];
    }
};


// eslint-disable-next-line no-undef
module.exports = nextConfig;
