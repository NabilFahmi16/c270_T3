from playwright.sync_api import sync_playwright, expect
import pytest
import time

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
    
    page.goto("http://localhost:5000/login", wait_until="networkidle")
    
    # Fill login form (assumes user already exists or you pre-create in another test/fixture)
    page.fill('input[name="username"]', "testuser")
    page.fill('input[name="password"]', "testpass123")
    
    page.click('button:has-text("Login")')
    
    page.wait_for_url("http://localhost:5000/", timeout=15000)
    page.wait_for_selector("h1", timeout=10000)
    
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
