# mangasfx-cli2026
Создает фввлайн версию библеотеки sfx с сайта http://thejadednetwork.com/sfx/.

## DISCLAIMER
Doesn't contain any actual content from the site. Only the means to download an offline copy of it and use it from the command line.

## How
First, use `./download.py` to download the site. Then `./search.py [search terms or leave empty for interactive mode]`.


Установите pip install beautifulsoup4 html5lib requests
Эти три библеотеки теперь необходимы, чтобы сервер сайтта нек послал нафиг.

Запускаете файл скачивания:
python download.py


Вовремя скачивания окно будет иметь вид:

___________________
--- Обработка раздела 30/42: http://thejadednetwork.com/sfx/index/ho/ ---
  Страница 1: найдено 15 записей.
  Всего страниц в разделе: 7
  Загрузка страницы 2...
    Страница 2: найдено 15 записей.
  Загрузка страницы 3...
    Страница 3: найдено 15 записей.
  Загрузка страницы 4...
    Страница 4: найдено 15 записей.
  Загрузка страницы 5...
    Страница 5: найдено 15 записей.
  Загрузка страницы 6...
    Страница 6: найдено 15 записей.
  Загрузка страницы 7...
    Страница 7: найдено 5 записей.

--- Обработка раздела 31/42: http://thejadednetwork.com/sfx/index/ma/ ---
  Страница 1: найдено 2 записей.
  Блок пагинации не найден, раздел состоит из одной страницы.

--- Обработка раздела 32/42: http://thejadednetwork.com/sfx/index/mi/ ---
  Страница 1: найдено 7 записей.
  Блок пагинации не найден, раздел состоит из одной страницы.
___________________


