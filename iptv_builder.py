#!/usr/bin/env python3
"""
🎬 ПОЛНАЯ СБОРКА - ВСЕ КАНАЛЫ С ФИЛЬМАМИ И СЕРИАЛАМИ!
- Все фильмовые каналы
- Все сериальные каналы
- Киноканалы
- Мультфильмы
- Российские федеральные
- Молдавские каналы
"""

import requests
import hashlib
import os
import json
import re
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================
# 1. НАСТРОЙКИ
# ============================================

CONFIG = {
    'timeout': 15,
    'max_channels': 10000,
    'threads': 10,
}

# ============================================
# 2. ВСЕ ИСТОЧНИКИ (МАКСИМУМ!)
# ============================================

SOURCES = [
    # РОССИЯ
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://iptv-org.github.io/iptv/countries/ru.m3u',
    'https://raw.githubusercontent.com/Free-IPTV/Countries/master/RU.m3u',
    
    # МОЛДОВА
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/countries/md.m3u',
    
    # ФИЛЬМЫ (ВСЕ!)
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    'https://raw.githubusercontent.com/Free-IPTV/Countries/master/movies.m3u',
    
    # КИНОКАНАЛЫ
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    
    # МУЛЬТФИЛЬМЫ
    'https://iptv-org.github.io/iptv/categories/kids.m3u',
    
    # ДОКУМЕНТАЛЬНЫЕ
    'https://iptv-org.github.io/iptv/categories/documentary.m3u',
    
    # НОВОСТИ
    'https://iptv-org.github.io/iptv/categories/news.m3u',
    
    # СПОРТ
    'https://iptv-org.github.io/iptv/categories/sport.m3u',
    
    # МИР
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/gb.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/de.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/fr.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/es.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/it.m3u',
]

# ============================================
# 3. КЛЮЧЕВЫЕ СЛОВА ДЛЯ ФИЛЬМОВ
# ============================================

MOVIE_KEYWORDS = [
    # Русские
    'фильм', 'кино', 'кинофильм', 'кинокомедия', 'кинодрама',
    'боевик', 'триллер', 'детектив', 'мелодрама', 'комедия',
    'фантастика', 'приключения', 'ужасы', 'мистика', 'вестерн',
    'семейный', 'романтический', 'приключенческий',
    'военный', 'исторический', 'криминальный',
    'мультфильм', 'мультик', 'аниме', 'анимация',
    
    # Английские
    'movie', 'movies', 'film', 'films', 'cinema',
    'action', 'drama', 'comedy', 'thriller', 'horror',
    'sci-fi', 'fantasy', 'adventure', 'western',
    'romance', 'family', 'animation', 'anime',
    'cartoon', 'cartoons', 'disney', 'pixar',
    
    # Названия каналов с фильмами
    'кинохит', 'киносвидание', 'киносемья', 'киноужас',
    'кинокомедия', 'кинодетектив', 'кинобоевик',
    'tv1000', 'tv1000 action', 'tv1000 русское',
    'кинопремьера', 'кинозал', 'кинотв',
    'dom kino', 'дом кино',
    'mosfilm', 'мосфильм',
    'иллюзион', 'nostalgia', 'ностальгия',
    'ivi', 'megogo', 'kinopoisk', 'кинопоиск',
    'filmua', 'film ua',
    'hd movie', 'ultra movie',
    'cinema', 'cine',
    'filmbox', 'film box',
    'hollywood', 'голливуд',
]

SERIES_KEYWORDS = [
    # Русские
    'сериал', 'сериалы', 'серия', 'сезон', 'эпизод',
    'телесериал', 'многосерийный', 'мыльная опера',
    'детективный сериал', 'криминальный сериал',
    'исторический сериал', 'комедийный сериал',
    'драматический сериал', 'фантастический сериал',
    'русский сериал', 'турецкий сериал',
    'латиноамериканский сериал', 'мексиканский сериал',
    'бразильский сериал', 'аргентинский сериал',
    'колумбийский сериал', 'испанский сериал',
    'итальянский сериал', 'французский сериал',
    'немецкий сериал', 'британский сериал',
    'американский сериал', 'канадский сериал',
    'австралийский сериал', 'новозеландский сериал',
    'южнокорейский сериал', 'японский сериал',
    'китайский сериал', 'тайваньский сериал',
    'индийский сериал', 'пакистанский сериал',
    'египетский сериал', 'турецкий сериал',
    'израильский сериал', 'палестинский сериал',
    'ливанский сериал', 'сирийский сериал',
    'иорданский сериал', 'иракский сериал',
    'саудовский сериал', 'эмиратский сериал',
    'кувейтский сериал', 'бахрейнский сериал',
    'катарский сериал', 'оманский сериал',
    'йеменский сериал', 'суданский сериал',
    'алжирский сериал', 'марокканский сериал',
    'тунисский сериал', 'ливийский сериал',
    
    # Английские
    'series', 'serial', 'season', 'episode',
    'tv series', 'tv show', 'show',
    'drama series', 'comedy series', 'crime series',
    'historical series', 'fantasy series', 'sci-fi series',
    'thriller series', 'horror series', 'mystery series',
    'family series', 'kids series', 'animated series',
    'mini series', 'anthology series', 'reality series',
    'telenovela', 'soap opera', 'sitcom',
    'detective series', 'police series', 'legal series',
    'medical series', 'military series', 'political series',
    'spy series', 'superhero series', 'western series',
    'teen series', 'romantic series', 'musical series',
    'documentary series', 'true crime series',
    'game show', 'talk show', 'variety show',
    'reality show', 'competition show', 'talent show',
]

# ============================================
# 4. ФУНКЦИИ
# ============================================

def download_m3u(url):
    """Скачать плейлист"""
    for attempt in range(2):
        try:
            r = requests.get(url, timeout=CONFIG['timeout'])
            if r.status_code == 200:
                return r.text
        except:
            time.sleep(1)
    return None

def parse_m3u(content):
    """Разобрать M3U файл"""
    channels = []
    seen = set()
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    key = hashlib.md5(f"{line}|{url}".encode()).hexdigest()
                    if key not in seen:
                        seen.add(key)
                        channels.append((line, url))
                        i += 1
        i += 1
    return channels

def get_poster(title):
    """Создать постер"""
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#1dd1a1', '#ee5a24', '#0652DD', '#c0392b', '#2980b9']
    color = colors[hash(title) % len(colors)]
    
    clean_title = re.sub(r'\([^)]*\)', '', title)
    clean_title = re.sub(r'\[[^\]]*\]', '', clean_title)
    clean_title = re.sub(r'\d{3,4}p', '', clean_title)
    clean_title = re.sub(r'HD|FULL|4K|1080|720|SD', '', clean_title, flags=re.IGNORECASE)
    clean_title = clean_title.strip()
    
    if len(clean_title) > 20:
        clean_title = clean_title[:18] + '...'
    
    return f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='300'><rect width='200' height='300' fill='{color}'/><text x='100' y='150' font-family='Arial' font-size='18' fill='white' text-anchor='middle'>{clean_title}</text></svg>"

def is_movie_channel(line, url):
    """Проверка, является ли канал фильмовым"""
    combined = (line + ' ' + url).lower()
    for keyword in MOVIE_KEYWORDS:
        if keyword.lower() in combined:
            return True
    return False

def is_series_channel(line, url):
    """Проверка, является ли канал сериальным"""
    combined = (line + ' ' + url).lower()
    for keyword in SERIES_KEYWORDS:
        if keyword.lower() in combined:
            return True
    return False

def get_category(line, url):
    """Определение категории с приоритетами"""
    combined = (line + ' ' + url).lower()
    
    # Молдова
    if 'moldova' in combined or 'молдова' in combined or '.md' in combined:
        return '🇲🇩 МОЛДОВА'
    
    # Россия
    if 'russia' in combined or 'россия' in combined or 'ru' in combined:
        return '🇷🇺 РОССИЯ'
    
    # Фильмы
    if is_movie_channel(line, url):
        return '🎬 ФИЛЬМЫ'
    
    # Сериалы
    if is_series_channel(line, url):
        return '📺 СЕРИАЛЫ'
    
    # Мультфильмы
    if 'cartoon' in combined or 'мульт' in combined or 'disney' in combined:
        return '🧸 МУЛЬТФИЛЬМЫ'
    
    # Новости
    if 'news' in combined or 'новости' in combined:
        return '📰 НОВОСТИ'
    
    # Спорт
    if 'sport' in combined or 'спорт' in combined:
        return '⚽ СПОРТ'
    
    # Документальные
    if 'documentary' in combined or 'документ' in combined:
        return '🌍 ДОКУМЕНТАЛЬНЫЕ'
    
    return '🌐 ДРУГИЕ'

def build_playlist():
    """Сборка плейлиста"""
    print("\n" + "="*70)
    print("🎬 ПОЛНАЯ СБОРКА - ФИЛЬМЫ, СЕРИАЛЫ, КИНО!")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    all_channels = []
    stats = {'movies': 0, 'series': 0, 'russia': 0, 'moldova': 0, 'other': 0}
    
    total_sources = len(SOURCES)
    
    for i, url in enumerate(SOURCES, 1):
        print(f"[{i}/{total_sources}] 📡 {url}")
        content = download_m3u(url)
        if not content:
            print("    ❌ Ошибка")
            continue
        
        channels = parse_m3u(content)
        if not channels:
            print("    ⚠️ 0")
            continue
        
        added = 0
        print(f"    ✅ Найдено: {len(channels)}")
        
        for line, url in channels:
            if len(all_channels) >= CONFIG['max_channels']:
                break
            
            category = get_category(line, url)
            
            # Для фильмов и сериалов добавляем постеры
            if category in ['🎬 ФИЛЬМЫ', '📺 СЕРИАЛЫ', '🧸 МУЛЬТФИЛЬМЫ']:
                name_match = re.search(r',([^,]+)$', line)
                if name_match:
                    name = name_match.group(1).strip()
                    poster = get_poster(name)
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
            
            all_channels.append((line, url))
            added += 1
            
            if category == '🎬 ФИЛЬМЫ':
                stats['movies'] += 1
            elif category == '📺 СЕРИАЛЫ':
                stats['series'] += 1
            elif category == '🇷🇺 РОССИЯ':
                stats['russia'] += 1
            elif category == '🇲🇩 МОЛДОВА':
                stats['moldova'] += 1
            else:
                stats['other'] += 1
        
        if added > 0:
            print(f"    ✅ +{added} добавлено")
    
    print("\n" + "="*70)
    print(f"📊 ВСЕГО КАНАЛОВ: {len(all_channels)}")
    print(f"   🎬 Фильмы: {stats['movies']}")
    print(f"   📺 Сериалы: {stats['series']}")
    print(f"   🇷🇺 Россия: {stats['russia']}")
    print(f"   🇲🇩 Молдова: {stats['moldova']}")
    print(f"   🌐 Другие: {stats['other']}")
    print("="*70)
    
    return all_channels

def save_playlist(channels):
    """Сохранить плейлист с категориями"""
    if not channels:
        print("\n❌ Нет каналов!")
        return False
    
    # Группировка
    grouped = {}
    for line, url in channels:
        category = get_category(line, url)
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(f"{line}\n{url}")
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🎬 ПОЛНАЯ СБОРКА - ВСЕ ФИЛЬМЫ И СЕРИАЛЫ!\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {len(channels)}\n\n')
            
            # Приоритет категорий
            priority = [
                '🎬 ФИЛЬМЫ',
                '📺 СЕРИАЛЫ',
                '🧸 МУЛЬТФИЛЬМЫ',
                '🇷🇺 РОССИЯ',
                '🇲🇩 МОЛДОВА',
                '📰 НОВОСТИ',
                '⚽ СПОРТ',
                '🌍 ДОКУМЕНТАЛЬНЫЕ',
                '🌐 ДРУГИЕ'
            ]
            
            for cat in priority:
                if cat in grouped:
                    f.write(f'# ==========================================\n')
                    f.write(f'#  📁 {cat} ({len(grouped[cat])})\n')
                    f.write(f'# ==========================================\n\n')
                    for ch in grouped[cat]:
                        f.write(f'{ch}\n')
                    f.write('\n')
        
        size = os.path.getsize('playlist.m3u') / 1024
        print(f"\n💾 Сохранено: playlist.m3u")
        print(f"📊 Каналов: {len(channels)}")
        print(f"📂 Категорий: {len(grouped)}")
        print(f"📁 Размер: {size:.1f} KB")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    channels = build_playlist()
    if channels:
        save_playlist(channels)
        print("\n📎 ССЫЛКА ДЛЯ ПЛЕЕРА:")
        print("https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
        print("\n🎬 ТЕПЕРЬ ЕСТЬ ВСЁ!")
        print("   ✅ Тысячи фильмов")
        print("   ✅ Тысячи сериалов")
        print("   ✅ Мультфильмы")
        print("   ✅ Российские каналы")
        print("   ✅ Молдавские каналы")
        print("   ✅ Постеры")
        print("   ✅ Автообновление")
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
