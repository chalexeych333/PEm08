# Анализ конкурентов

Простое приложение для анализа конкурентов на Python с FastAPI.

## Что реализовано

- API `POST /analyze_text` — анализ текста конкурента.
- API `POST /analyze_image` — анализ загруженного изображения с описанием.
- API `POST /parse_demo` — парсинг сайта, извлечение `title`, `h1`, `first paragraph` и анализ.
- API `GET /history` — просмотр последних 10 запросов.
- Веб-интерфейс `GET /` для отправки текста, изображения и ссылки.

## Структура

- `app/main.py` — основной сервер FastAPI.
- `app/config.py` — настройки приложения.
- `app/history.py` — сохранение истории в `history.json`.
- `app/parser.py` — парсер сайтов на Selenium (headless Chrome).
- `app/openai_client.py` — обёртка вызовов OpenAI.
- `static/index.html` — минимальный UI.
- `data/Links.txt` — список конкурентов для анализа.

## Запуск

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Создайте `.env` рядом с `requirements.txt`:

```env
OPENAI_API_KEY=ваш_ключ
OPENAI_MODEL=gpt-4o-mini
```

3. Запустите сервер:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Откройте в браузере `http://127.0.0.1:8000`

## Дополнительный эндпоинт

- `GET /links` — возвращает список ссылок из `data/Links.txt`.
- `POST /analyze_links` — анализирует все ссылки из `data/Links.txt`.

## Как использовать

- Вставьте текст конкурента и нажмите «Проанализировать текст».
- Загрузите изображение и добавьте описание для визуального анализа.
- Вставьте URL и нажмите «Собрать и проанализировать».
- История последних запросов отображается внизу.

## Примечания

- Веб-парсер использует Selenium с headless Chrome и выполняет JavaScript на странице.
- При первом запуске Selenium Manager автоматически скачивает совместимый драйвер (и при необходимости Chrome for Testing). Нужен установленный Chrome или доступ в интернет для загрузки.
- Параметры Selenium настраиваются через `.env`: `SELENIUM_HEADLESS`, `CHROME_BINARY_PATH`, `CHROMEDRIVER_PATH`, `PARSER_TIMEOUT`.
- История хранится в `history.json`.
