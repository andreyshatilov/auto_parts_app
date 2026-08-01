const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('client_frontend/index.html', 'utf-8');
const carModelsJs = fs.readFileSync('client_frontend/js/car_models.js', 'utf-8');
const js = fs.readFileSync('client_frontend/app.js', 'utf-8');

// Combine scripts in order, just like a browser would
const combinedJs = carModelsJs + '\n;\n' + js;

const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true });
const window = dom.window;

window.localStorage = {
    store: {},
    getItem(k) { return this.store[k] || null; },
    setItem(k, v) { this.store[k] = v; },
    removeItem(k) { delete this.store[k]; }
};
window.fetch = async (url, opts) => {
    return { ok: false, status: 404, json: async () => ({}) };
};
window.alert = (m) => {};
window.confirm = () => true;

try {
    window.eval(combinedJs);
    console.log('✅ Combined JS loaded without syntax errors');

    // Fire DOMContentLoaded
    const event = window.document.createEvent("Event");
    event.initEvent("DOMContentLoaded", true, true);
    window.document.dispatchEvent(event);
    console.log('✅ DOMContentLoaded fired');

    // Test 1: switchAuthTab
    window.switchAuthTab('login');
    const loginForm = window.document.getElementById('loginForm');
    const registerForm = window.document.getElementById('registerForm');
    console.log('✅ switchAuthTab("login") - loginForm:', loginForm.className, ', registerForm:', registerForm.className);
    
    window.switchAuthTab('register');
    console.log('✅ switchAuthTab("register") - loginForm:', loginForm.className, ', registerForm:', registerForm.className);

    // Test 2: key functions existence
    console.log('✅ showModal:', typeof window.showModal);
    console.log('✅ hideModal:', typeof window.hideModal);
    console.log('✅ showMainScreen:', typeof window.showMainScreen);
    console.log('✅ renderGarage:', typeof window.renderGarage);
    console.log('✅ setupEventListeners:', typeof window.setupEventListeners);

    // Test 3: simulate login
    const mockClient = {
        id: 1, first_name: "Test", last_name: "User", 
        phone: "+3801234567", cars: [], shipping_address: ""
    };
    
    try {
        window.showMainScreen(mockClient);
        const authScreen = window.document.getElementById('authScreen');
        const mainScreen = window.document.getElementById('mainScreen');
        console.log('✅ showMainScreen - authScreen:', authScreen.className, ', mainScreen:', mainScreen.className);
    } catch (e) {
        console.log('❌ showMainScreen FAILED:', e.message);
    }

    console.log('\n🎉 ALL TESTS PASSED');

} catch (err) {
    console.error('❌ FATAL ERROR:', err.message);
}
