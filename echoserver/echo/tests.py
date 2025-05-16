from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytest
@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_login(browser):
    # Открываем страницу входа
    browser.get("http://127.0.0.1:8000/login/")  # Замените на ваш URL

    username_input = browser.find_element(By.NAME, "username")
    password_input = browser.find_element(By.NAME, "password")

    username_input.send_keys("test_user")
    password_input.send_keys("Tk4#m7Xq!Lp9")

    # Отправляем форму
    browser.find_element(By.XPATH, "//button[contains(text(), 'Войти')]").click()
    time.sleep(2)
    assert "Книжный магазин" in browser.title
    assert browser.current_url == "http://127.0.0.1:8000/books/"


def test_order_placement(browser):
    browser.get("http://127.0.0.1:8000/login/")
    browser.find_element(By.NAME, "username").send_keys("test_user")
    browser.find_element(By.NAME, "password").send_keys("Tk4#m7Xq!Lp9")
    browser.find_element(By.XPATH, "//button[contains(text(), 'Войти')]").click()
    time.sleep(2)

    browser.get("http://127.0.0.1:8000/books/")
    xpath = "//div[contains(., 'Мартин Иден')]/following-sibling::div//a[contains(., 'В корзину')]"
    add_to_cart_button = browser.find_element(By.XPATH, xpath)
    add_to_cart_button.click()
    time.sleep(1)

    cart_link = browser.find_element(By.LINK_TEXT, "Корзина")
    cart_link.click()

    assert "Убить пересмешника" in browser.page_source
    assert "599.50 руб." in browser.page_source
    checkout_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Оформить заказ')]")
    checkout_btn.click()

    try:
        order_row = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(), 'Вы оформили заказ!')]"))
    )
        assert True
    except:
        assert False, "Заказ не появился в списке!"