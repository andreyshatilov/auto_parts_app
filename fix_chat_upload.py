import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

upload_js = """
// IMAGE UPLOAD LOGIC
async function handleChatImageUpload(file, callback) {
    try {
        showToast('Завантаження фото...', 'info');
        const formData = new FormData();
        formData.append('reqtype', 'fileupload');
        formData.append('fileToUpload', file);
        const res = await fetch('https://catbox.moe/user/api.php', { method: 'POST', body: formData });
        if(!res.ok) throw new Error('Помилка завантаження');
        const url = await res.text();
        showToast('Фото завантажено!', 'success');
        callback(url);
    } catch(err) {
        showToast('Не вдалося завантажити фото: ' + err.message, 'error');
    }
}
window.handleChatImageUpload = handleChatImageUpload;
"""

def update_html(filepath, form_id, input_id):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Add photo button
    button_html = f'<button type="button" class="btn btn-secondary" style="width: 44px; padding: 10px;" onclick="document.getElementById(\'{input_id}File\').click()">📷</button>\n<input type="file" id="{input_id}File" accept="image/*" style="display:none;" onchange="uploadAndSend{input_id}File(this.files[0])">'
    
    html = re.sub(
        rf'<input type="text" id="{input_id}"([^>]+)>',
        rf'<input type="text" id="{input_id}"\1>\n                  {button_html}',
        html
    )
    # bump version
    html = re.sub(r'v=\d+\.\d+', 'v=27.0', html)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

def update_js(filepath, form_id, input_id, req_id_var, sender_type, container_id):
    with open(filepath, 'r', encoding='utf-8') as f:
        js = f.read()
        
    if "handleChatImageUpload" not in js:
        js += "\n" + upload_js
        
    upload_and_send = f"""
window.uploadAndSend{input_id}File = async function(file) {{
    if(!file || !{req_id_var}) return;
    const token = localStorage.getItem(TOKEN_STORAGE_KEY) || localStorage.getItem('admin_token');
    handleChatImageUpload(file, async (url) => {{
        try {{
            const res = await fetch(`${{API_BASE_URL}}/chat/messages?sender_type={sender_type}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json', 'X-Auth-Token': token }},
                body: JSON.stringify({{ request_id: {req_id_var}, message: '📷 Фото', attachment_url: url }})
            }});
            if(!res.ok) throw new Error('Помилка відправки');
            if (typeof loadChatMessages === 'function') await loadChatMessages({req_id_var});
            if (typeof loadAdminChatMessages === 'function') await loadAdminChatMessages({req_id_var});
        }} catch(err) {{
            showToast(err.message, 'error');
        }}
    }});
}};
"""
    if f"uploadAndSend{input_id}File" not in js:
        js += "\n" + upload_and_send
        
    # Also update rendering to show images if attachment_url is present
    render_regex = r'<div>\$\{escapeHtml\(m\.message\)\}</div>'
    new_render = r"""<div>${escapeHtml(m.message)}</div>
                  ${m.attachment_url ? `<div style="margin-top:6px;"><a href="${escapeHtml(m.attachment_url)}" target="_blank"><img src="${escapeHtml(m.attachment_url)}" style="max-width:100%; border-radius:8px;"></a></div>` : ''}"""
    
    js = re.sub(render_regex, new_render, js)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(js)


# 1. Admin
update_html('admin_frontend/index.html', 'adminChatSendForm', 'adminChatInput')
update_js('admin_frontend/app.js', 'adminChatSendForm', 'adminChatInput', 'activeAdminChatRequestId', 'manager', 'adminChatMessagesContainer')

# 2. Client
update_html('client_frontend/index.html', 'chatSendForm', 'chatInput')
update_js('client_frontend/app.js', 'chatSendForm', 'chatInput', 'activeChatRequestId', 'client', 'chatMessagesContainer')

print("Applied chat upload features.")
