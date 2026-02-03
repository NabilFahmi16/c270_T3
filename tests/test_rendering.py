from playwright.sync_api import sync_playwright, expect
import pytest
import time
import uuid

# Increase timeout if needed (Kubernetes startup can be slow)
pytestmark = pytest.mark.timeout(60)

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def logged_in_page(browser):
    page = browser.new_page()

    page.goto("http://127.0.0.1:5000/login", wait_until="domcontentloaded")

    # Click Register tab
    page.click('div.tab:has-text("Register")')

    # Wait until Register form is visible
    register_form = page.locator("#registerForm")
    expect(register_form).to_be_visible(timeout=10000)

    # Use selectors scoped INSIDE the register form (avoids picking hidden login inputs)
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    register_form.locator('input[name="username"]').fill(username)
    register_form.locator('input[name="email"]').fill(f"{username}@example.com")
    register_form.locator('input[name="password"]').fill("testpass123")
    register_form.locator('button:has-text("Register")').click()

    # Wait for redirect to home
    page.wait_for_url("http://127.0.0.1:5000/", timeout=20000)

    # Confirm logged in
    expect(page.locator(f"text=Welcome, {username}")).to_be_visible(timeout=10000)

    yield page
    page.close()
    
def test_homepage_renders_correctly_after_login(logged_in_page):
    page = logged_in_page
    
    # Wait for important elements
    page.wait_for_selector("h1", timeout=10000)
    
    # Check title
    expect(page).to_have_title("URL Shortener Pro v2.0")
    
    # Check main heading
    expect(page.locator("h1")).to_have_text("🔗 URL Shortener Pro v2.0")
    
    # Check welcome message
    expect(page.locator("text=Welcome,")).to_be_visible()
    
    # Check that the create form exists
    expect(page.locator("h2:has-text('Create New Short Link')")).to_be_visible()
    
    # Check that the stats grid is present
    expect(page.locator(".stats-grid")).to_be_visible()
    
    # Optional: take screenshot for debugging
    page.screenshot(path="home_logged_in.png", full_page=True)

def test_login_page_loads(browser):
    page = browser.new_page()
    page.goto("http://localhost:5000/login", wait_until="networkidle")
    
    expect(page).to_have_title("Login - URL Shortener")
    expect(page.locator("h2:has-text('Login')")).to_be_visible()
    expect(page.locator("button:has-text('Login')")).to_be_visible()
    
    page.screenshot(path="login_page.png")
    page.close()
