#!/usr/bin/env python3
"""
🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + ВОССТАНОВЛЕННЫЕ КАНАЛЫ
Обновление: добавлены каналы, исключённые из Orange TV
"""

import requests
import hashlib
import os
import json
import re
import time
from datetime import datetime

# ============================================
# 1. КАНАЛЫ, ИСКЛЮЧЁННЫЕ ИЗ ORANGE TV (восстанавливаем)
# ============================================

RESTORED_CHANNELS = [
    # Документальные (были на позициях 301-316)
    'viju History',           # был на 85 позиции[citation:15]
    'viju TV1000 русское',
    'viju+ Sport',
    'Da Vinci',
    'Планета',
    'Тайны Галактики',
    'Наука HD',
    
    # Спортивные
    'Q Sport',
    'MMA-TV.com',
    
    # Развлекательные
    'Автоплюс',
    'Здоровое ТВ',
    'Драйв',
    'ТВ 3 International',
    'Перец International',
    'РЕН ТВ International HD',
]

# ============================================
# 2. РОССИЙСКИЕ КАНАЛЫ (которые Orange больше не транслирует)
# ============================================

RUSSIAN_CHANNELS = [
    'Россия 1',
    'Россия 24',
    'НТВ',
    'ТНТ',
    'СТС',
    'Первый канал',
    'РЕН ТВ',
    'Матч ТВ',
    'Звезда',
    'Пятый канал',
    'Спас',
    'Карусель',
    'МУЗ ТВ',
    'Ю',
    'Пятница',
    'Дом кино',
]

# ============================================
# 3. МОЛДАВСКИЕ КАНАЛЫ (из сетки Orange)
# ============================================

MOLDOVAN_CHANNELS = [
    # Общественные
    'Moldova 1', 'Moldova 2',
    'Prime', 'Canal 2', 'Canal 3', 'Canal 5',
    'N4', 'NTV Moldova',
    'Publika TV', 'TV8',
    'RTR Moldova', 'Ren Moldova',
    'Accent TV', 'ITV Moldova',
    'TVC 21', 'Orhei TV',
    'TV Bălți', 'ATV Comrat',
    '10TV HD', 'Axial TV HD',
    
    # Музыкальные
    'Noroc TV', 'Busuioc TV',
    'Europa Plus TV Moldova',
    
    # Религиозные
    'Alfa Omega TV',
]

# ============================================
# 4. НАСТРОЙКИ
# ============================================

CONFIG = {
    'timeout': 10,
    'max_channels': 1500,
}

# ============================================
# 5. ИСТОЧНИКИ
# ============================================

SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
]

# ============================================
# 6. ФУНКЦИИ
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

def is_restored_channel(line):
    """Проверка, является ли канал восстановленным"""
    line_lower = line.lower()
    for channel in RESTORED_CHANNELS:
        if channel.lower() in line_lower:
            return True
    return False

def is_russian_channel(line):
    """Проверка российского канала"""
    line_lower = line.lower()
    for channel in RUSSIAN_CHANNELS:
        if channel.lower() in line_lower:
            return True
    return False

def is_moldovan_channel(line):
    """Проверка молдавского канала"""
    line_lower = line.lower()
    for channel in MOLDOVAN_CHANNELS:
        if channel.lower() in line_lower:
            return True
    return False

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

def get_category(line, url):
    """Определение категории"""
    combined = (line + ' ' + url).lower()
    
    if 'фильм' in combined or 'movie' in combined or 'кино' in combined:
        return '🎬 ФИЛЬМЫ'
    elif 'сериал' in combined or 'series' in combined or 'serial' in combined:
        return '📺 СЕРИАЛЫ'
    elif 'спорт' in combined or 'sport' in combined:
        return '⚽ СПОРТ'
    elif 'новости' in combined or 'news' in combined:
        return '📰 НОВОСТИ'
    elif 'дет' in combined or 'kids' in combined or 'cartoon' in combined:
        return '🧸 ДЕТСКИЕ'
    else:
        return '🌐 ДРУГИЕ'

def build_playlist():
    """Сборка плейлиста"""
    print("\n" + "="*60)
    print("🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + ВОССТАНОВЛЕННЫЕ КАНАЛЫ")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    all_channels = []
    stats = {
        'russia': 0,
        'moldova': 0,
        'restored': 0,
        'movies': 0,
        'series': 0,
        'other': 0
    }
    
    for url in SOURCES:
        print(f"📡 {url}")
        content = download_m3u(url)
        if not content:
            print("  ❌ Ошибка загрузки")
            continue
        
        channels = parse_m3u(content)
        print(f"  ✅ Найдено: {len(channels)}")
        
        for line, url in channels:
            if len(all_channels) >= CONFIG['max_channels']:
                break
            
            # Определяем категорию
            category = get_category(line, url)
            
            # Восстановленные каналы (были удалены из Orange)
            if is_restored_channel(line):
                # Добавляем постер
                name_match = re.search(r',([^,]+)$', line)
                if name_match:
                    name = name_match.group(1).strip()
                    poster = get_poster(name)
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                all_channels.append((line, url))
                stats['restored'] += 1
                
            # Российские каналы
            elif is_russian_channel(line):
                all_channels.append((line, url))
                stats['russia'] += 1
                
            # Молдавские каналы
            elif is_moldovan_channel(line):
                all_channels.append((line, url))
                stats['moldova'] += 1
                
            # Фильмы
            elif category == '🎬 ФИЛЬМЫ':
                name_match = re.search(r',([^,]+)$', line)
                if name_match:
                    name = name_match.group(1).strip()
                    poster = get_poster(name)
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                all_channels.append((line, url))
                stats['movies'] += 1
                
            # Сериалы
            elif category == '📺 СЕРИАЛЫ':
                name_match = re.search(r',([^,]+)$', line)
                if name_match:
                    name = name_match.group(1).strip()
                    poster = get_poster(name)
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                all_channels.append((line, url))
                stats['series'] += 1
    
    print("\n" + "="*60)
    print(f"📊 ВСЕГО: {len(all_channels)}")
    print(f"   🇷🇺 Россия: {stats['russia']}")
    print(f"   🇲🇩 Молдова: {stats['moldova']}")
    print(f"   🔄 Восстановлено (из Orange): {stats['restored']}")
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
        # Определяем категорию с приоритетом для восстановленных
        if is_restored_channel(line):
            category = '🔄 ВОССТАНОВЛЕННЫЕ (Orange)'
        elif is_russian_channel(line):
            category = '🇷🇺 РОССИЯ'
        elif is_moldovan_channel(line):
            category = '🇲🇩 МОЛДОВА'
        else:
            category = get_category(line, url)
        
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(f"{line}\n{url}")
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🇷🇺 РОССИЯ + 🇲🇩 МОЛДОВА + ВОССТАНОВЛЕННЫЕ КАНАЛЫ\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {len(channels)}\n\n')
            
            priority = [
                '🇷🇺 РОССИЯ',
                '🇲🇩 МОЛДОВА',
                '🔄 ВОССТАНОВЛЕННЫЕ (Orange)',
                '🎬 ФИЛЬМЫ',
                '📺 СЕРИАЛЫ',
                '📰 НОВОСТИ',
                '⚽ СПОРТ',
                '🧸 ДЕТСКИЕ',
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
        print("\n🔄 ВОССТАНОВЛЕННЫЕ КАНАЛЫ (были удалены из Orange):")
        for ch in RESTORED_CHANNELS[:10]:
            print(f"   ✅ {ch}")
        print(f"   ... и {len(RESTORED_CHANNELS) - 10} других")
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
