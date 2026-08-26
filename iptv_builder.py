#!/usr/bin/env python3
"""
🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + 🎬 ФИЛЬМЫ + 📺 СЕРИАЛЫ
Только то, что вам нужно!
"""

import requests
import hashlib
import os
import json
import re
from datetime import datetime

# ============================================
# 1. ТОЛЬКО НУЖНЫЕ ИСТОЧНИКИ
# ============================================

SOURCES = {
    # Российские федеральные каналы
    'ru': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    ],
    # Молдавские каналы
    'md': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    ],
    # Фильмы (русские)
    'movies': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
    ],
}

# ============================================
# 2. РОССИЙСКИЕ ФЕДЕРАЛЬНЫЕ КАНАЛЫ (список)
# ============================================

RUSSIAN_FEDERAL = [
    'первый канал', '1 канал', '1kanal',
    'россия 1', 'russia 1', 'rtr',
    'россия 24', 'russia 24',
    'россия культура', 'russia k',
    'нтв', 'ntv',
    'тнт', 'tnt',
    'сТС', 'sts',
    'рен тв', 'ren tv',
    'пятый канал', '5 канал',
    'звезда', 'zvezda',
    'матч тв', 'match tv',
    'спас', 'spas',
    'карусель', 'carousel',
    'муз тв', 'muz tv',
    'ю', 'yu',
    'пятница', 'friday',
    'дом кино', 'dom kino',
    'телеканал россия',
]

# ============================================
# 3. ФУНКЦИИ
# ============================================

def download_m3u(url):
    """Скачать плейлист"""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except:
        pass
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

def is_russian_federal(line, url):
    """Проверка, является ли канал российским федеральным"""
    combined = (line + ' ' + url).lower()
    
    # Только федеральные каналы
    for channel in RUSSIAN_FEDERAL:
        if channel.lower() in combined:
            return True
    return False

def is_moldovan(line, url):
    """Проверка, является ли канал молдавским"""
    combined = (line + ' ' + url).lower()
    moldovan_keywords = [
        'молдова', 'moldova', 'md', 'молд',
        'primul', 'mold', 'chisinau', 'кишинёв',
        'pro tv', 'publika', 'jurnal', 'tv8',
        'noroc', 'renato', 'muzic'
    ]
    for keyword in moldovan_keywords:
        if keyword.lower() in combined:
            return True
    return False

def get_poster(title):
    """Создать постер для фильма/сериала"""
    # Простой цветной постер с названием
    import random
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
    color = colors[hash(title) % len(colors)]
    
    # Очищаем название от лишнего
    clean_title = re.sub(r'\([^)]*\)', '', title)
    clean_title = re.sub(r'\[[^\]]*\]', '', clean_title)
    clean_title = re.sub(r'\d{3,4}p', '', clean_title)
    clean_title = clean_title.strip()
    
    return f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='300'><rect width='200' height='300' fill='{color}'/><text x='100' y='150' font-family='Arial' font-size='18' fill='white' text-anchor='middle'>{clean_title[:25]}</text></svg>"

def get_category(line, url):
    """Определить категорию"""
    combined = (line + ' ' + url).lower()
    
    if 'фильм' in combined or 'movie' in combined or 'кино' in combined:
        return '🎬 ФИЛЬМЫ'
    elif 'сериал' in combined or 'series' in combined or 'serial' in combined:
        return '📺 СЕРИАЛЫ'
    elif is_moldovan(line, url):
        return '🇲🇩 МОЛДОВА'
    elif is_russian_federal(line, url):
        return '🇷🇺 РОССИЯ'
    elif 'новости' in combined or 'news' in combined:
        return '📰 НОВОСТИ'
    elif 'спорт' in combined or 'sport' in combined:
        return '⚽ СПОРТ'
    else:
        return '🌐 ДРУГИЕ'

def main():
    print("\n" + "="*60)
    print("🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + 🎬 ФИЛЬМЫ + 📺 СЕРИАЛЫ")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    all_channels = []
    stats = {'russia': 0, 'moldova': 0, 'movies': 0, 'series': 0, 'other': 0}
    
    # 1. РОССИЙСКИЕ ФЕДЕРАЛЬНЫЕ
    print("🇷🇺 РОССИЙСКИЕ ФЕДЕРАЛЬНЫЕ КАНАЛЫ:")
    for url in SOURCES['ru']:
        print(f"  📥 {url}")
        content = download_m3u(url)
        if content:
            channels = parse_m3u(content)
            for line, url in channels:
                if is_russian_federal(line, url):
                    all_channels.append((line, url))
                    stats['russia'] += 1
            print(f"    ✅ +{stats['russia']} каналов")
    
    # 2. МОЛДОВСКИЕ
    print("\n🇲🇩 МОЛДОВСКИЕ КАНАЛЫ:")
    for url in SOURCES['md']:
        print(f"  📥 {url}")
        content = download_m3u(url)
        if content:
            channels = parse_m3u(content)
            for line, url in channels:
                if is_moldovan(line, url):
                    all_channels.append((line, url))
                    stats['moldova'] += 1
            print(f"    ✅ +{stats['moldova']} каналов")
    
    # 3. ФИЛЬМЫ НА РУССКОМ
    print("\n🎬 ФИЛЬМЫ НА РУССКОМ:")
    for url in SOURCES['movies']:
        print(f"  📥 {url}")
        content = download_m3u(url)
        if content:
            channels = parse_m3u(content)
            for line, url in channels:
                # Проверяем, что фильм на русском
                if 'ru' in line.lower() or 'russian' in line.lower():
                    # Добавляем постер
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        name = name_match.group(1).strip()
                        poster = get_poster(name)
                        line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                    all_channels.append((line, url))
                    stats['movies'] += 1
            print(f"    ✅ +{stats['movies']} фильмов")
    
    # 4. СЕРИАЛЫ НА РУССКОМ
    print("\n📺 СЕРИАЛЫ НА РУССКОМ:")
    # Используем те же источники, но ищем сериалы
    for url in SOURCES['movies']:
        print(f"  📥 {url}")
        content = download_m3u(url)
        if content:
            channels = parse_m3u(content)
            for line, url in channels:
                if ('ru' in line.lower() or 'russian' in line.lower()) and ('series' in line.lower() or 'сериал' in line.lower()):
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        name = name_match.group(1).strip()
                        poster = get_poster(name)
                        line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                    all_channels.append((line, url))
                    stats['series'] += 1
            print(f"    ✅ +{stats['series']} сериалов")
    
    print("\n" + "="*60)
    print(f"📊 ВСЕГО КАНАЛОВ: {len(all_channels)}")
    print(f"   🇷🇺 Россия: {stats['russia']}")
    print(f"   🇲🇩 Молдова: {stats['moldova']}")
    print(f"   🎬 Фильмы: {stats['movies']}")
    print(f"   📺 Сериалы: {stats['series']}")
    print("="*60)
    
    # СОХРАНЕНИЕ
    if all_channels:
        # Группировка
        grouped = {}
        for line, url in all_channels:
            category = get_category(line, url)
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(f"{line}\n{url}")
        
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + 🎬 ФИЛЬМЫ + 📺 СЕРИАЛЫ\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {len(all_channels)}\n')
            f.write(f'# 🇷🇺 Россия: {stats["russia"]}\n')
            f.write(f'# 🇲🇩 Молдова: {stats["moldova"]}\n')
            f.write(f'# 🎬 Фильмы: {stats["movies"]}\n')
            f.write(f'# 📺 Сериалы: {stats["series"]}\n\n')
            
            # Приоритет категорий
            priority = ['🇷🇺 РОССИЯ', '🇲🇩 МОЛДОВА', '🎬 ФИЛЬМЫ', '📺 СЕРИАЛЫ', '📰 НОВОСТИ', '⚽ СПОРТ', '🌐 ДРУГИЕ']
            
            for cat in priority:
                if cat in grouped:
                    f.write(f'# ==========================================\n')
                    f.write(f'#  📁 {cat} ({len(grouped[cat])})\n')
                    f.write(f'# ==========================================\n\n')
                    for ch in grouped[cat]:
                        f.write(f'{ch}\n')
                    f.write('\n')
        
        print("\n💾 Сохранено: playlist.m3u")
        print("\n📎 ССЫЛКА ДЛЯ ПЛЕЕРА:")
        print("https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
        print("\n📱 КАК ИСПОЛЬЗОВАТЬ:")
        print("   1. Вставьте ссылку в любой IPTV плеер")
        print("   2. Вы увидите категории:")
        print("      🇷🇺 РОССИЯ - федеральные каналы")
        print("      🇲🇩 МОЛДОВА - молдавские каналы")
        print("      🎬 ФИЛЬМЫ - с постерами")
        print("      📺 СЕРИАЛЫ - с постерами")
        print("\n" + "="*60)

if __name__ == "__main__":
    main()
