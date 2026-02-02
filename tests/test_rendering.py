from playwright.sync_api import sync_playwright
import pytest

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

def test_homepage_renders_correctly(browser):
    page = browser.new_page()
    page.goto("http://localhost:5000/", wait_until="networkidle")
    
    assert page.title() == "Your App Title"
    assert page.locator("h1").inner_text() == "Welcome to the App!"
    assert page.locator("text=Some dynamic content").is_visible()
    
    # Optional: screenshot for visual proof
    page.screenshot(path="homepage.png")
