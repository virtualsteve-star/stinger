const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      logLevel: 'debug',
      onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.writeHead(502, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ error: 'Backend service unavailable' }));
      },
    })
  );
};