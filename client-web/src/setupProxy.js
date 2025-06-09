const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      timeout: 10000, // 10 second timeout
      proxyTimeout: 10000,
      logLevel: 'warn',
      onError: (err, req, res) => {
        console.warn('Proxy error occurred:', err.message);
        if (!res.headersSent) {
          res.status(503).json({
            error: 'Backend service unavailable',
            message: 'The backend server is not responding. Please check if it\'s running on port 5000.'
          });
        }
      },
      onProxyReq: (proxyReq, req, res) => {
        // Handle connection drops more gracefully
        proxyReq.on('error', (err) => {
          console.warn('Proxy request error:', err.message);
        });
      },
      onProxyRes: (proxyRes, req, res) => {
        // Handle response errors
        proxyRes.on('error', (err) => {
          console.warn('Proxy response error:', err.message);
        });
      },
      // Retry configuration
      retry: {
        limit: 3,
        delay: 1000
      }
    })
  );
}; 