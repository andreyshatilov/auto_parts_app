import io
import re

with io.open('client_frontend/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Add JSDocs to functions
replacements = {
    "function switchNavTab(tabName) {": """/**
 * Switches the main navigation tabs in the client interface.
 * Hides all main views and displays the requested view.
 * @param {string} tabName - The ID of the view to display (e.g., 'viewGarage', 'viewRequests').
 */
function switchNavTab(tabName) {""",

    "function switchAuthTab(tabName) {": """/**
 * Switches between Login and Register tabs on the Authentication screen.
 * @param {string} tabName - 'login' or 'register'.
 */
function switchAuthTab(tabName) {""",

    "function setupEventListeners() {": """/**
 * Initializes all global event listeners for the application.
 * Binds form submissions (login, register, add car, etc.) and global UI clicks.
 * @returns {void}
 */
function setupEventListeners() {""",

    "function showMainScreen(client) {": """/**
 * Transitions the UI from the Authentication screen to the Main application screen.
 * Updates the UI with the client's profile information.
 * @param {Object} client - The authenticated client object containing profile data.
 */
function showMainScreen(client) {""",

    "function showModal(modalEl) {": """/**
 * Displays a modal dialog with a smooth fade-in animation.
 * Uses requestAnimationFrame to ensure CSS transitions trigger correctly.
 * @param {HTMLElement} modalEl - The DOM element of the modal to show.
 */
function showModal(modalEl) {""",

    "function hideModal(modalEl) {": """/**
 * Hides a modal dialog with a smooth fade-out animation.
 * Waits for the CSS transition to complete before setting display:none.
 * @param {HTMLElement} modalEl - The DOM element of the modal to hide.
 */
function hideModal(modalEl) {""",

    "function initYearSelect() {": """/**
 * Populates the 'Year of Release' dropdown in the Add Car modal.
 * Generates options from the current year down to 1970.
 */
function initYearSelect() {""",

    "function initBrandAndModelSelects() {": """/**
 * Initializes the Brand and Model dropdowns in the Add Car modal.
 * Uses the global CAR_DATABASE (loaded from car_models.js) to populate brands.
 * Binds an event listener to dynamically update models when a brand is selected.
 */
function initBrandAndModelSelects() {""",

    "function getBrandEmblem(brandName) {": """/**
 * Generates an HTML snippet for a car brand emblem.
 * Uses a public CDN (car-logos.org) for high-quality PNG logos.
 * Includes an 'onerror' fallback to display a text-based initial if the logo fails to load.
 * @param {string} brandName - The name of the car brand.
 * @returns {string} HTML string representing the emblem image or fallback.
 */
function getBrandEmblem(brandName) {""",

    "function renderGarage(cars) {": """/**
 * Renders the Garage view, displaying a list of the client's cars.
 * Updates the Add Car button state (large dashed if empty, small solid if populated).
 * @param {Array<Object>} cars - Array of car objects belonging to the client.
 */
function renderGarage(cars) {""",

    "function renderRequests(requests) {": """/**
 * Renders the active Requests list for the client.
 * Groups items and displays statuses using badges.
 * @param {Array<Object>} requests - Array of request objects.
 */
function renderRequests(requests) {""",

    "function renderMyOrders(orders) {": """/**
 * Renders the Order History view (completed or processing orders).
 * Allows the user to initiate returns for eligible orders.
 * @param {Array<Object>} orders - Array of order objects.
 */
function renderMyOrders(orders) {""",

    "function handleLogout() {": """/**
 * Logs out the current user by removing tokens from localStorage and resetting UI state.
 */
function handleLogout() {""",

    "function showToast(msg, type = 'info') {": """/**
 * Displays a temporary toast notification on the screen.
 * Automatically dismisses after 3.5 seconds.
 * @param {string} msg - The message to display.
 * @param {string} [type='info'] - The type of toast ('info', 'success', 'error').
 */
function showToast(msg, type = 'info') {"""
}

for old, new_ in replacements.items():
    code = code.replace(old, new_)

# Add section headers if not already there
if "/* ==========================================" not in code:
    code = code.replace("// DOM ", """
/* ==========================================
 * 1. DOM ELEMENTS & GLOBAL STATE
 * ========================================== */
// DOM """)
    
    code = code.replace("async function checkAuth() {", """
/* ==========================================
 * 2. AUTHENTICATION & INITIALIZATION
 * ========================================== */
async function checkAuth() {""")

    code = code.replace("function setupEventListeners() {", """
/* ==========================================
 * 3. EVENT LISTENERS
 * ========================================== */
/**""")

    code = code.replace("function showModal(modalEl) {", """
/* ==========================================
 * 4. UI COMPONENTS (MODALS, TOASTS)
 * ========================================== */
/**""")

    code = code.replace("function renderGarage(cars) {", """
/* ==========================================
 * 5. GARAGE & CAR MANAGEMENT
 * ========================================== */
/**""")

    code = code.replace("function renderRequests(requests) {", """
/* ==========================================
 * 6. REQUESTS & ORDERS HISTORY
 * ========================================== */
/**""")

with io.open('client_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added JSDoc comments and section headers.")
