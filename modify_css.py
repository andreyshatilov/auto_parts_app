with open('client_frontend/styles.css', 'a', encoding='utf-8') as f:
    f.write('''

/* Animations for smooth transitions */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

.screen.active {
    animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.view-content.active {
    animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.modal-backdrop {
    transition: opacity 0.3s ease;
}

.modal-content {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
''')
    print('CSS appended')

with open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()
js = js.replace('v=21.0', 'v=22.0')
with open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=21.0', 'v=22.0')

# Also replace display: none; inline styles for view-content with just the class, 
# because JS will handle display via .active
html = html.replace('class="view-content" style="display: none;"', 'class="view-content"')

with open('client_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done!')
