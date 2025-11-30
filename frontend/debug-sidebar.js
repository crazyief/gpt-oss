/**
 * Debug script for sidebar visibility issue
 *
 * HOW TO USE:
 * 1. Open Chrome DevTools (F12)
 * 2. Go to Console tab
 * 3. Copy and paste this entire script
 * 4. Press Enter
 *
 * This will diagnose what's happening with the sidebar.
 */

(function debugSidebar() {
    console.log('=== SIDEBAR DEBUG START ===\n');

    // 1. Check localStorage value
    const lsKey = 'gpt-oss-sidebar-open';
    const lsValue = localStorage.getItem(lsKey);
    console.log(`1. localStorage["${lsKey}"] = "${lsValue}"`);
    console.log(`   Interpretation: ${lsValue === 'true' ? 'SIDEBAR SHOULD BE OPEN' : lsValue === 'false' ? 'SIDEBAR SHOULD BE CLOSED' : 'NO VALUE (default open)'}`);

    // 2. Check if .chat-tab element exists and its class
    const chatTab = document.querySelector('.chat-tab');
    if (chatTab) {
        console.log(`\n2. .chat-tab element found`);
        console.log(`   Classes: "${chatTab.className}"`);
        console.log(`   Has sidebar-collapsed class: ${chatTab.classList.contains('sidebar-collapsed')}`);

        // 3. Check .history-sidebar computed styles
        const sidebar = document.querySelector('.history-sidebar');
        if (sidebar) {
            const computed = window.getComputedStyle(sidebar);
            console.log(`\n3. .history-sidebar computed styles:`);
            console.log(`   width: ${computed.width}`);
            console.log(`   overflow: ${computed.overflow}`);
            console.log(`   display: ${computed.display}`);
            console.log(`   visibility: ${computed.visibility}`);

            // Check if width is 0 or very small
            const widthNum = parseFloat(computed.width);
            if (widthNum < 10) {
                console.log(`\n   ⚠️  WARNING: Sidebar width is ${widthNum}px (should be ~260px when open)`);
            } else {
                console.log(`\n   ✅ Sidebar appears to have normal width`);
            }
        } else {
            console.log(`\n3. ❌ .history-sidebar element NOT FOUND!`);
        }
    } else {
        console.log(`\n2. ❌ .chat-tab element NOT FOUND!`);
        console.log(`   This might mean you're not on the chat tab.`);
    }

    // 4. FIX SUGGESTION
    console.log('\n=== SUGGESTED FIX ===');
    console.log('Run this to force sidebar open:');
    console.log(`localStorage.setItem('${lsKey}', 'true');`);
    console.log('window.location.reload();');

    // 5. Offer to auto-fix
    console.log('\n=== AUTO-FIX (paste and run if needed) ===');
    console.log("localStorage.setItem('gpt-oss-sidebar-open', 'true'); window.location.reload();");

    console.log('\n=== SIDEBAR DEBUG END ===');
})();
