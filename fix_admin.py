import io, sys, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Admin Index HTML
with open('admin_frontend/index.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

admin_html = admin_html.replace(
    '<button onclick="closeAdminChatModal()" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;"></button>',
    '<button onclick="closeAdminChatModal()" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">✕</button>'
)
# bump cache
admin_html = re.sub(r'v=\d+\.\d+', 'v=26.0', admin_html)
with open('admin_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

# 2. Admin App JS
with open('admin_frontend/app.js', 'r', encoding='utf-8') as f:
    admin_js = f.read()

# Add X-Auth-Token to chat send
old_fetch = r"""const res = await fetch\(`\$\{API_BASE_URL\}/chat/messages\?sender_type=manager`, \{\s*method: 'POST',\s*headers: \{ 'Content-Type': 'application/json' \},"""
new_fetch = r"""const token = localStorage.getItem('admin_token');
            const res = await fetch(`${API_BASE_URL}/chat/messages?sender_type=manager`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },"""
admin_js = re.sub(old_fetch, new_fetch, admin_js)

# Original message in chat:
# Change openAdminChatModal signature
admin_js = admin_js.replace('onclick="openAdminChatModal(${req.id})"', 'onclick="openAdminChatModal(${req.id}, \`${escapeHtml(req.client_message)}\`)"')
admin_js = admin_js.replace('async function openAdminChatModal(requestId) {', 'async function openAdminChatModal(requestId, initialMessage) {\n    window.currentAdminChatInitialMessage = initialMessage;')
# In loadAdminChatMessages, inject the original message
old_render = r"""adminChatMessagesContainer\.innerHTML = messages\.map\(m => `"""
new_render = r"""
        const initialMsgHtml = window.currentAdminChatInitialMessage ? `
            <div style="align-self: flex-start; background: rgba(255,255,255,0.05); padding:12px; border-radius:10px; max-width:90%; font-size:13px; border-left: 3px solid #f59e0b; margin-bottom:10px;">
                <div style="font-size:10px; color:#f59e0b; margin-bottom:4px; font-weight:700;">ОРИГІНАЛЬНИЙ ЗАПИТ КЛІЄНТА</div>
                <div>${window.currentAdminChatInitialMessage}</div>
            </div>` : '';
            
        adminChatMessagesContainer.innerHTML = initialMsgHtml + messages.map(m => `"""
admin_js = re.sub(old_render, new_render, admin_js)

with open('admin_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(admin_js)

# 3. Client App JS - Move applyPreset to top
with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    client_js = f.read()

preset_match = re.search(r'function applyPreset\(text\) \{[\s\S]*?\n\}', client_js)
if preset_match:
    func_text = preset_match.group(0)
    client_js = client_js.replace(func_text, '')
    client_js = func_text + '\n\n' + client_js
    
    # ensure it is on window
    client_js += '\nwindow.applyPreset = applyPreset;\n'
    
with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(client_js)

print("All fixes applied successfully.")
