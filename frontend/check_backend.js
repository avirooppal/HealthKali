/**
 * Simple script to check backend connection
 * Run with: node check_backend.js
 */

const http = require('http');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/health',
  method: 'GET',
  timeout: 5000
};

console.log('Testing connection to Cancer Digital Twin backend...');

const req = http.request(options, (res) => {
  console.log(`Status Code: ${res.statusCode}`);
  
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('Response body:', data);
    console.log('Backend connection test completed!');
    console.log('\nIf you received a 200 status code, your backend is running and accessible.');
    console.log('If you received an error, make sure your FastAPI backend is running on port 8000.');
  });
});

req.on('error', (error) => {
  console.error('Error connecting to backend:', error.message);
  console.log('\nConnection test failed. Make sure your FastAPI backend is running on port 8000.');
  console.log('To start your backend, run: uvicorn main:app --reload');
});

req.end();