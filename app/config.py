from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o-mini"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    history_file: str = "history.json"
    max_history_items: int = 10
    parser_timeout: int = 20
    parser_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # Настройки Selenium / Chrome
    selenium_headless: bool = True
    chrome_binary_path: str = ""  # путь к chrome.exe, если он не в PATH (необязательно)
    chromedriver_path: str = ""   # путь к chromedriver, если не используется Selenium Manager
    data_links_path: str = "data/Links.txt"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
