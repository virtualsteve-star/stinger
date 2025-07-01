#!/usr/bin/env node

const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

// Determine backend URL based on environment or defaults
const BACKEND_PROTOCOL = process.env.BACKEND_PROTOCOL || 'https';
const BACKEND_HOST = process.env.BACKEND_HOST || 'localhost';
const BACKEND_PORT = process.env.BACKEND_PORT || '8000';
const BACKEND_URL = `${BACKEND_PROTOCOL}://${BACKEND_HOST}:${BACKEND_PORT}`;

// Serve static files from the React build
const buildPath = path.join(__dirname, 'frontend', 'build');
app.use(express.static(buildPath));

// Proxy API requests to backend
app.use('/api', createProxyMiddleware({
  target: BACKEND_URL,
  changeOrigin: true,
  secure: false, // Accept self-signed certificates
  logLevel: 'warn',
  onError: (err, req, res) => {
    console.error(`Proxy error: ${err.message}`);
    res.status(502).json({
      error: 'Backend service unavailable',
      details: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
  }
}));

// Handle React routing - serve index.html for all non-API routes
app.get('*', (req, res) => {
  res.sendFile(path.join(buildPath, 'index.html'));
});

// Check if SSL certificates exist
const certPath = path.join(__dirname, 'backend', 'cert.pem');
const keyPath = path.join(__dirname, 'backend', 'key.pem');

if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
  // Use HTTPS with existing certificates
  const httpsOptions = {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath)
  };

  https.createServer(httpsOptions, app).listen(PORT, () => {
    console.log(`✅ Production server running on https://localhost:${PORT}`);
    console.log(`📋 Backend API expected at ${BACKEND_URL}`);
    console.log(`\n🌐 Open https://localhost:${PORT} in your browser`);
  });
} else {
  // Fallback to HTTP if no certificates
  app.listen(PORT, () => {
    console.log(`✅ Production server running on http://localhost:${PORT}`);
    console.log(`⚠️  Warning: Running without HTTPS. Generate SSL certificates for secure operation.`);
    console.log(`📋 Backend API expected at ${BACKEND_URL}`);
    console.log(`\n🌐 Open http://localhost:${PORT} in your browser`);
    console.log(`\n💡 Tip: If backend is also HTTP, set BACKEND_PROTOCOL=http`);
  });
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('\nShutting down server...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\nShutting down server...');
  process.exit(0);
});