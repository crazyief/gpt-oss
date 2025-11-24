#!/usr/bin/env node
/**
 * Apply toast notification fixes to API client and SSE client
 *
 * This script automatically adds toast notifications to:
 * - src/lib/services/api-client.ts (11 functions)
 * - src/lib/services/sse-client.ts (3 error handlers)
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 Applying toast notification fixes...\n');

// File paths
const API_CLIENT_PATH = path.join(__dirname, 'src', 'lib', 'services', 'api-client.ts');
const SSE_CLIENT_PATH = path.join(__dirname, 'src', 'lib', 'services', 'sse-client.ts');

// Backup files
console.log('📦 Creating backups...');
fs.copyFileSync(API_CLIENT_PATH, API_CLIENT_PATH + '.backup');
fs.copyFileSync(SSE_CLIENT_PATH, SSE_CLIENT_PATH + '.backup');
console.log('✅ Backups created\n');

// Update API Client
console.log('📝 Updating API client...');
let apiClient = fs.readFileSync(API_CLIENT_PATH, 'utf8');

// Add import if not present
if (!apiClient.includes('from \'$lib/stores/toast\'')) {
    apiClient = apiClient.replace(
        /import { API_ENDPOINTS } from '\$lib\/config';/,
        `import { API_ENDPOINTS } from '$lib/config';\nimport { toast, getErrorMessage } from '$lib/stores/toast';`
    );
    console.log('  ✅ Added toast import');
}

// Helper function to wrap function body with try-catch
function addToastToFunction(content, functionName, hasSuccessToast, successMessage) {
    const functionRegex = new RegExp(
        `(export async function ${functionName}\\([^)]*\\): Promise<[^>]+> {)[\\s\\S]*?(?=\\n}\\n)`,
        'm'
    );

    const match = content.match(functionRegex);
    if (!match) {
        console.log(`  ⚠️  Could not find function: ${functionName}`);
        return content;
    }

    const originalBody = match[0];

    // Check if already has try-catch
    if (originalBody.includes('try {')) {
        console.log(`  ℹ️  ${functionName} already has toast support`);
        return content;
    }

    // Add try-catch wrapper
    let newBody = originalBody.replace(
        new RegExp(`(export async function ${functionName}\\([^)]*\\): Promise<[^>]+> {)`, 'm'),
        '$1\n\ttry {'
    );

    // Add error handling for !response.ok
    newBody = newBody.replace(
        /if \(!response\.ok\) {\s*const error = await response\.json\(\);\s*throw new Error\((.*?)\);/s,
        `if (!response.ok) {
\t\t\tconst error = await response.json();
\t\t\tconst message = getErrorMessage(error);
\t\t\ttoast.error(\`Failed to ${functionName.replace('fetch', 'load').replace('create', 'create').replace('delete', 'delete').replace('update', 'update')}: \${message}\`);
\t\t\tthrow new Error($1);`
    );

    // Add success toast if applicable
    if (hasSuccessToast) {
        newBody = newBody.replace(
            /return await response\.json\(\);/,
            `const result = await response.json();\n\t\ttoast.success('${successMessage}');\n\t\treturn result;`
        );
    }

    // Add catch block
    newBody += '\n\t} catch (err) {\n\t\tif (err instanceof TypeError) {\n\t\t\ttoast.error(\'Network error. Please check your connection.\');\n\t\t}\n\t\tthrow err;\n\t}';

    console.log(`  ✅ Updated ${functionName}`);
    return content.replace(originalBody, newBody);
}

// Update each function
const apiUpdates = [
    ['fetchProjects', false, ''],
    ['fetchProject', false, ''],
    ['createProject', true, 'Project created successfully'],
    ['deleteProject', true, 'Project deleted successfully'],
    ['fetchConversations', false, ''],
    ['fetchConversation', false, ''],
    ['createConversation', true, 'New conversation started'],
    ['updateConversation', true, 'Conversation updated'],
    ['deleteConversation', true, 'Conversation deleted'],
    ['fetchMessages', false, ''],
    ['updateMessageReaction', false, '']
];

for (const [funcName, hasSuccess, successMsg] of apiUpdates) {
    apiClient = addToastToFunction(apiClient, funcName, hasSuccess, successMsg);
}

fs.writeFileSync(API_CLIENT_PATH, apiClient);
console.log('✅ API client updated\n');

// Update SSE Client
console.log('📝 Updating SSE client...');
let sseClient = fs.readFileSync(SSE_CLIENT_PATH, 'utf8');

// Add import if not present
if (!sseClient.includes('import { toast }')) {
    sseClient = sseClient.replace(
        /import { logger } from '\$lib\/utils\/logger';/,
        `import { logger } from '$lib/utils/logger';\nimport { toast } from '$lib/stores/toast';`
    );
    console.log('  ✅ Added toast import');
}

// Replace FUTURE comment with actual toast
sseClient = sseClient.replace(
    /\/\/ FUTURE \(Stage 2\): Show user-facing notification in UI toast/,
    `toast.warning(\`Reconnecting... (\${this.retryCount}/\${APP_CONFIG.sse.maxRetries})\`);`
);
console.log('  ✅ Added reconnection toast');

// Add toast to handleError
sseClient = sseClient.replace(
    /(private handleError\(error: string\): void {\s*logger\.error\('SSE stream error', { error }\);)/,
    `$1\n\t\ttoast.error(error);`
);
console.log('  ✅ Added error toast');

// Add toast to max retries exceeded
sseClient = sseClient.replace(
    /(\/\/ Max retries exceeded, give up\s*this\.handleError\()\s*'Unable to connect[^']*'/,
    `$1\n\t\t\t'Unable to connect after multiple retries. Please check your connection and try again.'`
);
console.log('  ✅ Added max retries toast');

fs.writeFileSync(SSE_CLIENT_PATH, sseClient);
console.log('✅ SSE client updated\n');

console.log('🎉 All fixes applied successfully!');
console.log('\nBackup files created:');
console.log('  - api-client.ts.backup');
console.log('  - sse-client.ts.backup');
console.log('\nTo restore backups if needed:');
console.log('  mv src/lib/services/api-client.ts.backup src/lib/services/api-client.ts');
console.log('  mv src/lib/services/sse-client.ts.backup src/lib/services/sse-client.ts');
