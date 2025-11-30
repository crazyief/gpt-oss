const fs = require('fs');
const path = 'src/lib/components/MessageList.svelte';
let content = fs.readFileSync(path, 'utf8');
content = content.replace(
  '{:else if $messages.error}',
  '{:else if $messages.error && $messages.items.length === 0}'
);
fs.writeFileSync(path, content);
console.log('Fixed!');
