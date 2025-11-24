/**
 * Fix MSW URL Matching
 *
 * Updates handlers.ts to use full BASE_URL in all http method calls.
 * Run this before integration tests.
 */

const fs = require('fs');
const path = require('path');

const handlersPath = path.join(__dirname, 'src', 'mocks', 'handlers.ts');

console.log('Reading handlers.ts...');
let content = fs.readFileSync(handlersPath, 'utf8');

console.log('Replacing API paths with BASE_URL...');
content = content.replace(/http\.get\('\/api\//g, "http.get(`${BASE_URL}/api/");
content = content.replace(/http\.post\('\/api\//g, "http.post(`${BASE_URL}/api/");
content = content.replace(/http\.put\('\/api\//g, "http.put(`${BASE_URL}/api/");
content = content.replace(/http\.patch\('\/api\//g, "http.patch(`${BASE_URL}/api/");
content = content.replace(/http\.delete\('\/api\//g, "http.delete(`${BASE_URL}/api/");

// Fix closing quotes to backticks
content = content.replace(/(`\$\{BASE_URL\}\/api\/[^']+)'/g, "$1`");

console.log('Writing updated handlers.ts...');
fs.writeFileSync(handlersPath, content, 'utf8');

console.log('✅ MSW URLs fixed! Run: npm run test:integration');
