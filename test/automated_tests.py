"""File for performing automated tests using playwright"""

import re

from playwright.sync_api import sync_playwright, Playwright, expect


def test_place_order(playwright: Playwright):
    """
    Automated test for placing an order
    :param playwright: Playwright instance
    :return:
    """
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    # Load home page
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Enter credentials and log in
    page.locator("[name='email']").fill("admin@admin.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    # Add item to cart and place order
    page.locator('[href*="/add-to-cart/1"]').click()
    page.locator('[href*="/cart"]').click()
    expect(page).to_have_url("http://localhost:5000/cart")
    expect(page).to_have_title(re.compile(r".*Cart Page"))
    page.locator('[href*="/place-order"]').click()
    # other actions...
    browser.close()


def test_register(playwright: Playwright):
    """
    Automated test for creating a new user
    :param playwright: Playwright instance
    :return:
    """
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    # Load home page
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Load Register Page
    page.locator('[href*="/register"]').click()
    expect(page).to_have_title(re.compile(r".*Register Page"))
    expect(page).to_have_url("http://localhost:5000/register")
    # Enter credentials and create account
    page.locator("[name='username']").fill("test")
    page.locator("[name='email']").fill("test@test.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='confirm_password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    # other actions...
    browser.close()


def test_delete_user(playwright: Playwright):
    """
    Automated test deleting a user
    :param playwright: Playwright instance
    :return:
    """
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    # Load home page
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Login to admin account
    page.locator("[name='email']").fill("admin@admin.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    # Go to manager users page and delete the newly created user
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/customers"]').click()
    expect(page).to_have_title(re.compile(r".*Customer Page"))
    expect(page).to_have_url("http://localhost:5000/customers")
    page.locator('[href*="/customers/3"]').click()
    assert page.locator('tr').count() == 3
    browser.close()


def test_changing_order_status(playwright: Playwright):
    """
    Automated test for updating the status of an order
    :param playwright: Playwright instance
    :return:
    """
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    # Load home page
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Load Register Page
    page.locator('[href*="/register"]').click()
    expect(page).to_have_title(re.compile(r".*Register Page"))
    expect(page).to_have_url("http://localhost:5000/register")
    # Enter credentials and create account
    page.locator("[name='username']").fill("test")
    page.locator("[name='email']").fill("test@test.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='confirm_password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    # Add item to cart and place order
    page.locator('[href*="/add-to-cart/1"]').click()
    page.locator('[href*="/cart"]').click()
    expect(page).to_have_url("http://localhost:5000/cart")
    expect(page).to_have_title(re.compile(r".*Cart Page"))
    page.locator('[href*="/place-order"]').click()
    expect(page).to_have_title(re.compile(r".*Orders Page"))
    expect(page).to_have_url("http://localhost:5000/orders")
    # Logout of customer account
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/logout"]').click()
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/home")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Login to admin account
    page.locator("[name='email']").fill("admin@admin.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    # Go to manager orders page and update the order status
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/view-order"]').click()
    expect(page).to_have_title(re.compile(r".*View Orders Page"))
    expect(page).to_have_url("http://localhost:5000/view-orders")
    page.locator('[href*="/update-order/2"]').click()
    expect(page).to_have_title(re.compile(r".*Update Orders Page"))
    expect(page).to_have_url("http://localhost:5000/update-order/2")
    page.locator("[name='order_status']").select_option('Accepted')
    # page.locator("[name='order_status']").click()
    # page.locator("[value='Accepted']").click()
    page.locator("[name='update']").click()
    page.locator("[name='account-drop-down']").click()
    # Logout of admin account
    page.locator('[href*="/logout"]').click()
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/home")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Enter credentials and log in
    page.locator("[name='email']").fill("test@test.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    # View order with updated order status
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/orders"]').click()
    browser.close()


def test_edit_cart(playwright: Playwright):
    """
    Automated test for updating your cart
    :param playwright: Playwright instance
    :return:
    """
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    # Load home page
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Enter credentials and log in
    page.locator("[name='email']").fill("admin@admin.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    # Search
    page.locator("[name='search']").fill("Apple Watch")
    page.locator("[name='search_btn']").click()
    expect(page).to_have_url("http://localhost:5000/search")
    # Add item to cart and place order
    page.locator('[href*="/add-to-cart/1"]').click()
    page.locator('[href*="/cart"]').click()
    expect(page).to_have_url("http://localhost:5000/cart")
    # Edit cart
    page.locator("[name='decrease_quantity']").click()
    page.locator("[name='increase_quantity']").click()
    page.locator("[name='remove_from_cart_btn']").click()
    heading = page.query_selector("h1").text_content()
    assert heading == "Your Cart is Empty"
    # other actions...
    browser.close()


def test_error_page(playwright: Playwright):
    """
    Automated test for error pages
    :param playwright: Playwright instance
    :return:
    """
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    # Load home page
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Enter credentials and log in
    page.locator("[name='email']").fill("sam@sam.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/home")
    page.goto("http://localhost:5000/customers")
    heading = page.query_selector("h1").text_content()
    assert heading == "Access Denied"
    heading = page.query_selector("h3").text_content()
    assert heading == "You don't have permission to view this page."
    page.goto("http://localhost:5000/test")
    heading = page.query_selector("h1").text_content()
    assert heading == "404"
    heading = page.query_selector("h2").text_content()
    assert heading == "Page not found"
    browser.close()


def test_change_password(playwright: Playwright):
    """
    Automated test for changing your password
    :param playwright: Playwright instance
    :return:
    """
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    # Load home page
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Enter credentials and log in
    page.locator("[name='email']").fill("sam@sam.com")
    page.locator("[name='password']").fill("123456")
    page.locator("[name='submit']").click()
    # Change password
    expect(page).to_have_url("http://localhost:5000/home")
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/profile/1"]').click()
    expect(page).to_have_url("http://localhost:5000/profile/1")
    page.locator('[href*="/change_password/1"]').click()
    expect(page).to_have_url("http://localhost:5000/change_password/1")
    page.locator("[name='current_password']").fill("123456")
    page.locator("[name='new_password']").fill("12345678")
    page.locator("[name='confirm_password']").fill("12345678")
    page.locator("[name='submit']").click()
    expect(page).to_have_url("http://localhost:5000/profile/1")
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/logout"]').click()
    expect(page).to_have_title(re.compile(r".*Home Page"))
    expect(page).to_have_url("http://localhost:5000/home")
    # Load Login page
    page.locator("[name='account-drop-down']").click()
    page.locator('[href*="/login"]').click()
    expect(page).to_have_title(re.compile(r".*Login Page"))
    expect(page).to_have_url("http://localhost:5000/login")
    # Enter credentials and log in
    page.locator("[name='email']").fill("sam@sam.com")
    page.locator("[name='password']").fill("12345678")
    page.locator("[name='submit']").click()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        test_place_order(p)
        test_register(p)
        test_delete_user(p)
        test_changing_order_status(p)
        test_edit_cart(p)
        test_error_page(p)
        test_change_password(p)
