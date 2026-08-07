// API Configuration for different environments
const hostname = window.location.hostname;

let API_BASE_URL;

if (hostname === 'localhost' || hostname === '127.0.0.1') {
  // Local dev: direct to backend port or proxied via nginx on :3000
  API_BASE_URL = window.location.port === '3000'
    ? ''
    : 'http://localhost:8000';
} else if (hostname.includes('vercel.app') || hostname.includes('megeb')) {
  // Vercel: use same-origin proxy rewrites (vercel.json handles the proxy)
  API_BASE_URL = '';
} else {
  // Render or any other host: direct backend URL
  API_BASE_URL = 'https://megeb-backend.onrender.com';
}
