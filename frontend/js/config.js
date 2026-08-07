// API Configuration for different environments
const hostname = window.location.hostname;

let API_BASE_URL;

// Local development with Docker/nginx proxy
if (hostname === 'localhost' || hostname === '127.0.0.1') {
  // If port is 3000, use same-origin (proxied via nginx)
  // Otherwise use direct backend port
  API_BASE_URL = window.location.port === '3000' 
    ? '' 
    : 'http://localhost:8000';
}
// Render deployment
else if (hostname.includes('onrender.com')) {
  API_BASE_URL = 'https://megeb-backend.onrender.com';
}
// Other environments (custom domain)
else {
  API_BASE_URL = ''; // Same-origin
}
