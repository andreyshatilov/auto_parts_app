const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('client_frontend/index.html', 'utf-8');
const carModelsJs = fs.readFileSync('client_frontend/js/car_models.js', 'utf-8');
const js = fs.readFileSync('client_frontend/app.js', 'utf-8');

const dom = new JSDOM(html, { runScripts: "outside-only" });
const window = dom.window;

window.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {}
};
window.fetch = async () => ({ ok: true, json: async () => ({}) });

try {
    window.eval(carModelsJs);
    console.log("carModelsJs evaluated.");

    window.eval(js);
    console.log("app.js evaluated without syntax errors.");

    // Fire DOMContentLoaded
    const event = window.document.createEvent("Event");
    event.initEvent("DOMContentLoaded", true, true);
    window.document.dispatchEvent(event);
    console.log("DOMContentLoaded fired cleanly.");

    // Switch to login tab
    window.switchAuthTab('login');
    console.log("switchAuthTab('login') executed successfully.");

    const loginForm = window.document.getElementById('loginForm');
    const registerForm = window.document.getElementById('registerForm');
    console.log("loginForm class:", loginForm.className);
    console.log("registerForm class:", registerForm.className);

} catch (err) {
    console.error("ERROR IN JSDOM:", err);
}
