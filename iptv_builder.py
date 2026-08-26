#!/usr/bin/env python3
"""
🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + 🎬 ФИЛЬМЫ + 📺 СЕРИАЛЫ
РЕАЛЬНЫЕ СЕРИАЛЫ ИЗ РАЗНЫХ ИСТОЧНИКОВ!
"""

import requests
import hashlib
import os
import json
import re
import time
from datetime import datetime

# ============================================
# 1. НАСТРОЙКИ
# ============================================

CONFIG = {
    'timeout': 10,
    'max_channels': 2000,
}

# ============================================
# 2. РУССКИЕ НАЗВАНИЯ КАНАЛОВ
# ============================================

RUSSIAN_NAMES = {
    '1tv': 'Первый канал',
    'russia1': 'Россия 1',
    'russia24': 'Россия 24',
    'rtr': 'Россия 1',
    'ntv': 'НТВ',
    'tnt': 'ТНТ',
    'sts': 'СТС',
    'ren': 'РЕН ТВ',
    '5tv': 'Пятый канал',
    'zvezda': 'Звезда',
    'match': 'Матч ТВ',
    'spas': 'Спас',
    'karusel': 'Карусель',
    'muz': 'МУЗ ТВ',
    'yu': 'Ю',
    'friday': 'Пятница',
    'domkino': 'Дом кино',
}

# ============================================
# 3. ТОЛЬКО МОЛДАВСКИЕ КАНАЛЫ
# ============================================

MOLDOVAN_CHANNELS = [
    'primul', 'publika', 'jurnal', 'tv8',
    'noroc', 'renato', 'muzic', 'chisinau',
    'moldova 1', 'moldova2', 'gagauz',
    'comrat', 'tiraspol', 'balti',
]

ROMANIAN_EXCLUDE = [
    'pro tv', 'antena 1', 'antena 2', 'antena 3',
    'kiss tv', 'romania tv', 'digi', 'telekom',
    'tvr 1', 'tvr 2', 'tvr 3', 'romanian',
]

# ============================================
# 4. НОВЫЕ ИСТОЧНИКИ (ДЛЯ СЕРИАЛОВ!)
# ============================================

SOURCES = {
    # Российские каналы
    'ru': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    ],
    # Молдавские каналы
    'md': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    ],
    # Фильмы
    'movies': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
        'https://raw.githubusercontent.com/Free-IPTV/Countries/master/movies.m3u',
    ],
    # СЕРИАЛЫ - НОВЫЕ ИСТОЧНИКИ!
    'series': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
        'https://raw.githubusercontent.com/Free-IPTV/Countries/master/movies.m3u',
        # Добавляем каналы с сериалами
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/series.m3u',
    ],
}

# ============================================
# 5. ФУНКЦИИ
# ============================================

def download_m3u(url):
    for attempt in range(2):
        try:
            r = requests.get(url, timeout=CONFIG['timeout'])
            if r.status_code == 200:
                return r.text
        except:
            time.sleep(1)
    return None

def parse_m3u(content):
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

def get_russian_name(line):
    line_lower = line.lower()
    for eng, rus in RUSSIAN_NAMES.items():
        if eng in line_lower:
            return rus
    return None

def get_poster(title):
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#1dd1a1', '#ee5a24', '#0652DD']
    color = colors[hash(title) % len(colors)]
    
    clean_title = re.sub(r'\([^)]*\)', '', title)
    clean_title = re.sub(r'\[[^\]]*\]', '', clean_title)
    clean_title = re.sub(r'\d{3,4}p', '', clean_title)
    clean_title = re.sub(r'HD|FULL|4K|1080|720|SD', '', clean_title, flags=re.IGNORECASE)
    clean_title = clean_title.strip()
    
    if len(clean_title) > 20:
        clean_title = clean_title[:18] + '...'
    
    return f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='300'><rect width='200' height='300' fill='{color}'/><text x='100' y='150' font-family='Arial' font-size='18' fill='white' text-anchor='middle'>{clean_title}</text></svg>"

def is_russian_federal(line):
    line_lower = line.lower()
    russian_keywords = [
        'первый канал', '1 канал', '1kanal',
        'россия 1', 'russia 1', 'ртр', 'rtr',
        'россия 24', 'russia 24',
        'нтв', 'ntv', 'тнт', 'tnt', 'сТС', 'sts',
        'рен тв', 'ren tv', 'пятый канал', '5 канал',
        'звезда', 'zvezda', 'матч тв', 'match tv',
        'спас', 'spas', 'карусель', 'karusel',
        'муз тв', 'muz tv', 'ю', 'yu', 'пятница', 'friday',
        'дом кино', 'dom kino'
    ]
    for keyword in russian_keywords:
        if keyword.lower() in line_lower:
            return True
    return False

def is_moldovan_channel(line):
    line_lower = line.lower()
    for exclude in ROMANIAN_EXCLUDE:
        if exclude.lower() in line_lower:
            return False
    for channel in MOLDOVAN_CHANNELS:
        if channel.lower() in line_lower:
            return True
    moldovan_keywords = ['moldova', 'молдова', 'mold', 'chisinau', '.md']
    for keyword in moldovan_keywords:
        if keyword.lower() in line_lower:
            if 'romania' not in line_lower:
                return True
    return False

def is_movie(line):
    line_lower = line.lower()
    movie_keywords = ['film', 'movie', 'кино', 'фильм']
    for keyword in movie_keywords:
        if keyword in line_lower:
            return True
    return False

def is_series(line):
    """Проверка сериала (расширенная)"""
    line_lower = line.lower()
    series_keywords = [
        'series', 'serial', 'сериал', 'сериалы',
        'сез', 'season', 'эпизод', 'episode',
        'сборник', 'collection', 'box set',
        'серия', 'серий', 'выпуск', 'выпуски',
        '1 сезон', '2 сезон', '3 сезон', '4 сезон',
        's01', 's02', 's03', 's04', 's05',
        'закрытый', 'открытый', 'финал',
        'тв шоу', 'tv show', 'show',
    ]
    for keyword in series_keywords:
        if keyword in line_lower:
            return True
    return False

def get_category(line, url):
    combined = (line + ' ' + url).lower()
    
    # Сначала проверяем сериалы (важно!)
    if is_series(line):
        return '📺 СЕРИАЛЫ'
    elif is_movie(line):
        return '🎬 ФИЛЬМЫ'
    elif is_moldovan_channel(line):
        return '🇲🇩 МОЛДОВА'
    elif is_russian_federal(line):
        return '🇷🇺 РОССИЯ'
    elif 'новости' in combined or 'news' in combined:
        return '📰 НОВОСТИ'
    elif 'спорт' in combined or 'sport' in combined:
        return '⚽ СПОРТ'
    else:
        return '🌐 ДРУГИЕ'

def build_playlist():
    """Сборка плейлиста"""
    print("\n" + "="*60)
    print("🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + 🎬 ФИЛЬМЫ + 📺 СЕРИАЛЫ")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    all_channels = []
    stats = {'russia': 0, 'moldova': 0, 'movies': 0, 'series': 0, 'other': 0}
    
    # Обрабатываем каждый тип источника
    for source_type, urls in SOURCES.items():
        if source_type == 'ru':
            print("🇷🇺 РОССИЙСКИЕ КАНАЛЫ:")
        elif source_type == 'md':
            print("\n🇲🇩 МОЛДАВСКИЕ КАНАЛЫ:")
        elif source_type == 'movies':
            print("\n🎬 ФИЛЬМЫ:")
        elif source_type == 'series':
            print("\n📺 СЕРИАЛЫ (ИЩЕМ...):")
        
        for url in urls:
            print(f"  📡 {url}")
            content = download_m3u(url)
            if not content:
                print("    ❌ Ошибка")
                continue
            
            channels = parse_m3u(content)
            print(f"    ✅ Найдено: {len(channels)}")
            
            added = 0
            for line, url in channels:
                if len(all_channels) >= CONFIG['max_channels']:
                    break
                
                category = get_category(line, url)
                
                # Для сериалов - ищем ВЕЗДЕ
                if source_type == 'series' and category == '📺 СЕРИАЛЫ':
                    # Добавляем постер
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        name = name_match.group(1).strip()
                        poster = get_poster(name)
                        line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                    all_channels.append((line, url))
                    stats['series'] += 1
                    added += 1
                
                # Для фильмов
                elif source_type == 'movies' and category == '🎬 ФИЛЬМЫ':
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        name = name_match.group(1).strip()
                        poster = get_poster(name)
                        line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                    all_channels.append((line, url))
                    stats['movies'] += 1
                    added += 1
                
                # Для России
                elif source_type == 'ru' and category == '🇷🇺 РОССИЯ':
                    name = get_russian_name(line)
                    if name:
                        line = re.sub(r',[^,]*$', f',{name}', line)
                    all_channels.append((line, url))
                    stats['russia'] += 1
                    added += 1
                
                # Для Молдовы
                elif source_type == 'md' and category == '🇲🇩 МОЛДОВА':
                    all_channels.append((line, url))
                    stats['moldova'] += 1
                    added += 1
            
            if added > 0:
                print(f"    ✅ +{added} добавлено")
    
    print("\n" + "="*60)
    print(f"📊 ВСЕГО: {len(all_channels)}")
    print(f"   🇷🇺 Россия: {stats['russia']}")
    print(f"   🇲🇩 Молдова: {stats['moldova']}")
    print(f"   🎬 Фильмы: {stats['movies']}")
    print(f"   📺 Сериалы: {stats['series']}")
    print("="*60)
    
    return all_channels

def save_playlist(channels):
    """Сохранить плейлист"""
    if not channels:
        print("\n❌ Нет каналов!")
        return False
    
    grouped = {}
    for line, url in channels:
        category = get_category(line, url)
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(f"{line}\n{url}")
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + 🎬 ФИЛЬМЫ + 📺 СЕРИАЛЫ\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {len(channels)}\n\n')
            
            priority = ['🇷🇺 РОССИЯ', '🇲🇩 МОЛДОВА', '🎬 ФИЛЬМЫ', '📺 СЕРИАЛЫ', '📰 НОВОСТИ', '⚽ СПОРТ', '🌐 ДРУГИЕ']
            
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
        print("\n📺 ТЕПЕРЬ ЕСТЬ СЕРИАЛЫ!")
        print("   ✅ Ищем сериалы во ВСЕХ источниках")
        print("   ✅ Добавляем постеры")
        print("   ✅ Отдельная категория")
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
