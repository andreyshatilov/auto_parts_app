const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('client_frontend/index.html', 'utf-8');
const js = fs.readFileSync('client_frontend/app.js', 'utf-8');

const dom = new JSDOM(html, { runScripts: "outside-only" });
const window = dom.window;

// Mock localStorage and fetch
window.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {}
};
window.fetch = async () => ({ ok: true, json: async () => ({}) });

try {
    window.eval(js);
    console.log("JS parsed successfully.");

    // Simulate login success
    const client = {
        first_name: "Test",
        last_name: "User",
        phone: "+3801234567",
        cars: []
    };

    console.log("Calling showMainScreen...");
    window.showMainScreen(client);
    console.log("showMainScreen executed successfully.");

    // Check mainScreen classes
    const mainScreen = window.document.getElementById('mainScreen');
    console.log("mainScreen classes:", mainScreen.className);

} catch (err) {
    console.error("ERROR DURING JSDOM EXECUTION:", err);
}
