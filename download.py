#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import sys
from urllib.request import urlopen, URLError
from urllib.error import HTTPError
from bs4 import BeautifulSoup as BS
import requests
import sys

INDEX = 'http://thejadednetwork.com/sfx/index/'
REQUEST_DELAY = 5  # секунд между запросами

def bs(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # выбросит исключение, если HTTP статус не 200
        return BS(response.text, 'html5lib')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе {url}: {e}", file=sys.stderr)
        return None

def text(el):
    """Извлекает и очищает все текстовые узлы внутри элемента."""
    if el is None:
        return []
    return [l.strip() for l in el.find_all(text=True) if l.strip()]

def definitions(tbl):
    """
    Извлекает определения из таблицы с классом 'definitions'.
    Возвращает список словарей.
    """
    if tbl is None:
        return []
    
    rows = tbl.find_all('tr')
    result = []
    for row in rows:
        cells = row.find_all('td')
        if not cells:
            continue
        # Пропускаем строки-заголовки (с классом 'title' в первом td)
        if 'title' in cells[0].get('class', []):
            continue
        # Проверяем, что ячеек ровно 4 (ожидаемая структура)
        if len(cells) < 4:
            print(f"    Предупреждение: строка содержит {len(cells)} ячеек, ожидалось 4", file=sys.stderr)
            continue
        result.append({
            'japanese': text(cells[0]),
            'romaji': text(cells[1]),
            'english': text(cells[2]),
            'explanation': text(cells[3]),
        })
    return result

def main():
    print("Запуск парсинга базы японских звукоподражаний...")
    print(f"Индексная страница: {INDEX}")
    
    # Загрузка индексной страницы
    soup = bs(INDEX)
    if soup is None:
        print("Не удалось загрузить индексную страницу. Завершение.", file=sys.stderr)
        input("\nНажмите Enter для выхода...")
        return
    
    # Поиск таблицы меню по хирагане
    menu_table = soup.find('table', class_='hiraganaMenuTable')
    if menu_table is None:
        print("Не найдена таблица меню хираганы на индексной странице.", file=sys.stderr)
        input("\nНажмите Enter для выхода...")
        return
    
    # Извлечение ссылок на разделы
    kana_links = [
        td.a['href']
        for td in menu_table.find_all('td')
        if td.a and td.a.get('href')
    ]
    
    if not kana_links:
        print("Не найдено ни одной ссылки на разделы каны.", file=sys.stderr)
        input("\nНажмите Enter для выхода...")
        return
    
    print(f"Найдено {len(kana_links)} разделов по кане.")
    
    all_translations = []
    total_pages_processed = 0
    
    for idx, link in enumerate(kana_links, start=1):
        print(f"\n--- Обработка раздела {idx}/{len(kana_links)}: {link} ---")
        time.sleep(REQUEST_DELAY)
        
        # Загрузка первой страницы раздела
        soup_page = bs(link)
        if soup_page is None:
            print(f"  Пропуск раздела {link} из-за ошибки загрузки.")
            continue
        
        # Поиск таблицы определений
        tbl = soup_page.find('table', class_='definitions')
        if tbl is None:
            print(f"  На странице {link} нет таблицы определений. Пропуск.")
            continue
        
        # Извлечение записей с первой страницы
        entries = definitions(tbl)
        print(f"  Страница 1: найдено {len(entries)} записей.")
        all_translations.extend(entries)
        total_pages_processed += 1
        
        # Обработка пагинации
        pagin = soup_page.find('div', class_='pagin')
        if pagin:
            # Находим все ссылки внутри пагинации
            page_links = pagin.find_all('a')
            if len(page_links) >= 2:
                try:
                    # Предпоследняя ссылка обычно содержит номер последней страницы
                    last_page_num = int(page_links[-2].text.strip())
                except (ValueError, AttributeError):
                    last_page_num = 1
                print(f"  Всего страниц в разделе: {last_page_num}")
                
                # Обходим страницы со 2-й по последнюю
                for page_no in range(2, last_page_num + 1):
                    page_url = link + str(page_no)
                    print(f"  Загрузка страницы {page_no}...")
                    time.sleep(REQUEST_DELAY)
                    
                    soup_page_n = bs(page_url)
                    if soup_page_n is None:
                        print(f"    Ошибка загрузки страницы {page_no}, пропускаем.")
                        continue
                    
                    tbl_n = soup_page_n.find('table', class_='definitions')
                    if tbl_n is None:
                        print(f"    На странице {page_no} нет таблицы определений, пропускаем.")
                        continue
                    
                    entries_n = definitions(tbl_n)
                    print(f"    Страница {page_no}: найдено {len(entries_n)} записей.")
                    all_translations.extend(entries_n)
                    total_pages_processed += 1
            else:
                print("  Блок пагинации содержит менее двух ссылок, пропускаем пагинацию.")
        else:
            print("  Блок пагинации не найден, раздел состоит из одной страницы.")
    
    # Итоговая статистика
    print("\n" + "=" * 50)
    print(f"Обработано разделов: {len(kana_links)}")
    print(f"Загружено страниц: {total_pages_processed}")
    print(f"Всего собрано записей: {len(all_translations)}")
    
    # Сохранение в JSON
    output_file = 'translations.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_translations, f, ensure_ascii=False, indent=2)
        print(f"Данные успешно сохранены в файл: {output_file}")
    except Exception as e:
        print(f"Ошибка при записи файла: {e}", file=sys.stderr)
    
    # Ожидание нажатия Enter перед завершением
    input("\nНажмите Enter для выхода...")

if __name__ == '__main__':
    main()
