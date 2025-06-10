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
      // Add secure handling and headers
      secure: false,
      // Force HTTP/1.1 for better compatibility
      agent: false,
      xfwd: false,
      headers: {
        'Connection': 'close',
        'User-Agent': 'proxy-client/1.0'
      },
      onError: (err, req, res) => {
        console.warn('Proxy error occurred:', err.message);
        // Check if response is already closed or headers sent
        if (!res.headersSent && !res.destroyed && res.writable) {
          try {
            res.status(503).json({
              error: 'Backend service unavailable',
              message: 'The backend server is not responding. Please check if it\'s running on port 5000.'
            });
          } catch (writeError) {
            console.warn('Failed to send error response:', writeError.message);
          }
        }
      },
      onProxyReq: (proxyReq, req, res) => {
        // Handle connection drops more gracefully
        proxyReq.on('error', (err) => {
          console.warn('Proxy request error:', err.message);
          // Don't try to write if the request is already destroyed
          if (!proxyReq.destroyed) {
            proxyReq.destroy();
          }
        });
        
        // Set proper headers to handle HTTP/1.0 responses better
        proxyReq.setHeader('Connection', 'close');
        proxyReq.setHeader('Accept', 'application/json');
        
        // Handle request timeouts
        proxyReq.setTimeout(10000, () => {
          console.warn('Proxy request timeout');
          if (!proxyReq.destroyed) {
            proxyReq.destroy();
          }
        });
      },
      onProxyRes: (proxyRes, req, res) => {
        // Handle response errors and connection issues
        proxyRes.on('error', (err) => {
          console.warn('Proxy response error:', err.message);
          // Safely end the response if it's still writable
          if (res.writable && !res.headersSent) {
            try {
              res.status(500).end('Proxy response error');
            } catch (endError) {
              console.warn('Failed to end response:', endError.message);
            }
          }
        });

        // Handle aborted requests
        req.on('aborted', () => {
          console.warn('Request aborted');
          if (!proxyRes.destroyed) {
            proxyRes.destroy();
          }
        });

        // Handle response close events
        res.on('close', () => {
          if (!proxyRes.destroyed) {
            proxyRes.destroy();
          }
        });

        // Add timeout handling for responses
        proxyRes.setTimeout(10000, () => {
          console.warn('Proxy response timeout');
          if (!proxyRes.destroyed) {
            proxyRes.destroy();
          }
        });

        // Force connection close for HTTP/1.0 compatibility
        if (proxyRes.headers) {
          proxyRes.headers.connection = 'close';
        }
      },
      // Add additional options for better connection handling
      followRedirects: false, // Disable redirects for better control
      ws: false, // Disable websocket proxying to avoid additional complexity
      // Add parser options to handle malformed responses better
      parser: {
        timeout: 10000
      }
    })
  );
}; 