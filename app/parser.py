from __future__ import annotations

import asyncio

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from .config import settings


def _build_driver() -> webdriver.Chrome:
    """Создать экземпляр Chrome WebDriver под настройки приложения."""
    options = Options()
    if settings.selenium_headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={settings.parser_user_agent}")
    options.page_load_strategy = "eager"

    if settings.chrome_binary_path:
        options.binary_location = settings.chrome_binary_path

    # Если путь к драйверу не задан — Selenium Manager (встроен в Selenium 4.6+)
    # сам скачает совместимый chromedriver/Chrome for Testing.
    service = Service(executable_path=settings.chromedriver_path) if settings.chromedriver_path else Service()
    return webdriver.Chrome(options=options, service=service)


def _fetch_html(url: str) -> str:
    """Синхронно загрузить страницу в Chrome и вернуть её HTML."""
    driver = _build_driver()
    try:
        driver.set_page_load_timeout(settings.parser_timeout)
        driver.get(url)
        # Дать странице время отрисовать контент (в т.ч. через JavaScript).
        WebDriverWait(driver, settings.parser_timeout).until(
            lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
        )
        return driver.page_source
    finally:
        driver.quit()


def _extract(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    h1 = ""
    h1_tag = soup.find("h1")
    if h1_tag and h1_tag.get_text(strip=True):
        h1 = h1_tag.get_text(strip=True)

    first_p = ""
    p_tag = soup.find("p")
    if p_tag and p_tag.get_text(strip=True):
        first_p = p_tag.get_text(strip=True)

    return {"title": title, "h1": h1, "first_paragraph": first_p}


async def parse_url(url: str) -> dict[str, str]:
    """Загрузить страницу через headless Chrome (Selenium) и извлечь title/h1/первый абзац.

    Selenium синхронный, поэтому блокирующая работа вынесена в отдельный поток,
    чтобы не блокировать event loop FastAPI.
    """
    html = await asyncio.to_thread(_fetch_html, url)
    return _extract(html)
