#!/usr/bin/env python3
"""
🎬 ТОЛЬКО ВАШИ КАНАЛЫ!
Фильмы, сериалы, Россия, Молдова
БЕЗ ЛИШНЕГО МУСОРА!
"""

import requests
import hashlib
import os
import re
import time
from datetime import datetime

# ============================================
# 1. НАСТРОЙКИ
# ============================================

CONFIG = {
    'timeout': 15,
    'max_channels': 2000,
}

# ============================================
# 2. ВАШ СПИСОК КАНАЛОВ (ДЛЯ ПОИСКА!)
# ============================================

YOUR_CHANNELS = [
    # Фильмы и сериалы
    'amedia premium', 'viju+ premiere', 'viju+ meghit', 'viju+ serial',
    'viju history', 'tv1000', 'tv1000 русское', 'tv1000 action',
    'кинопремьера', 'киносемья', 'мужское кино', 'мосфильм',
    # Россия
    'россия 1', 'звезда', 'звезда плюс',
    # Молдова
    'tv7', 'tv9',
]

# ============================================
# 3. КАТЕГОРИИ ДЛЯ ГРУППИРОВКИ
# ============================================

CATEGORIES = {
    '🎬 ФИЛЬМЫ И СЕРИАЛЫ': [
        'amedia premium', 'viju+ premiere', 'viju+ meghit', 'viju+ serial',
        'viju history', 'tv1000', 'tv1000 русское', 'tv1000 action',
        'кинопремьера', 'киносемья', 'мужское кино', 'мосфильм',
    ],
    '🇷🇺 РОССИЯ': [
        'россия 1', 'звезда', 'звезда плюс',
    ],
    '🇲🇩 МОЛДОВА': [
        'tv7', 'tv9',
    ],
}

# ============================================
# 4. ИСТОЧНИКИ (ВСЕ, ГДЕ ЕСТЬ ВАШИ КАНАЛЫ)
# ============================================

SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    'https://iptv-org.github.io/iptv/categories/series.m3u',
    'https://iptv-org.github.io/iptv/playlist.m3u',
]

# ============================================
# 5. ФУНКЦИИ
# ============================================

def download_m3u(url):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=CONFIG['timeout'])
            if r.status_code == 200:
                return r.text
        except:
            time.sleep(2)
    return None

def parse_m3u(content):
    channels = []
    seen = set()
    if not content:
        return channels
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

def get_category(line):
    """Определить категорию по названию"""
    line_lower = line.lower()
    
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in line_lower:
                return category
    
    return None

def clean_name(line):
    """Очистить название канала"""
    # Убираем лишние теги
    line = re.sub(r'\s*\([^)]*\)', '', line)
    line = re.sub(r'\s*\[[^\]]*\]', '', line)
    line = re.sub(r'\s*HD|\s*SD|\s*FULL|\s*4K|\s*1080|\s*720', '', line, flags=re.IGNORECASE)
    return line.strip()

def get_poster(title):
    """Создать постер"""
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#1dd1a1', '#ee5a24', '#0652DD']
    color = colors[hash(title) % len(colors)]
    
    clean_title = title
    clean_title = re.sub(r'\([^)]*\)', '', clean_title)
    clean_title = re.sub(r'\[[^\]]*\]', '', clean_title)
    clean_title = re.sub(r'HD|FULL|4K|1080|720|SD', '', clean_title, flags=re.IGNORECASE)
    clean_title = clean_title.strip()
    
    if len(clean_title) > 22:
        clean_title = clean_title[:20] + '…'
    
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='200' height='280'>
        <rect width='200' height='280' fill='{color}' rx='8'/>
        <rect x='10' y='10' width='180' height='180' fill='rgba(255,255,255,0.1)' rx='4'/>
        <text x='100' y='220' font-family='Arial' font-size='16' fill='white' text-anchor='middle' font-weight='bold'>{clean_title}</text>
        <text x='100' y='245' font-family='Arial' font-size='12' fill='rgba(255,255,255,0.7)' text-anchor='middle'>▶ Нажми для просмотра</text>
    </svg>"""
    
    return "data:image/svg+xml," + svg.replace(' ', '%20').replace('\n', '')

def find_my_channels():
    """Найти только ваши каналы во всех источниках"""
    print("\n" + "="*70)
    print("🎯 ПОИСК ТОЛЬКО ВАШИХ КАНАЛОВ!")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    all_channels = []
    stats = {'found': 0, 'checked': 0}
    
    for url in SOURCES:
        print(f"📡 {url[:60]}...")
        content = download_m3u(url)
        if not content:
            print("    ❌ Недоступно")
            continue
        
        channels = parse_m3u(content)
        print(f"    ✅ Найдено: {len(channels)}")
        
        found = 0
        for line, url in channels:
            category = get_category(line)
            
            if category:
                # Чистим название
                name_match = re.search(r',([^,]+)$', line)
                if name_match:
                    name = name_match.group(1).strip()
                    clean = clean_name(name)
                    
                    # Добавляем постер для фильмов
                    if 'ФИЛЬМЫ' in category or 'СЕРИАЛЫ' in category:
                        poster = get_poster(clean)
                        line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                    
                    # Заменяем название на чистое
                    line = re.sub(r',[^,]*$', f',{clean}', line)
                
                all_channels.append((line, url, category))
                found += 1
                stats['found'] += 1
        
        if found > 0:
            print(f"    ✅ +{found} ваших каналов найдено!")
        stats['checked'] += 1
    
    print("\n" + "="*70)
    print(f"📊 НАЙДЕНО ВАШИХ КАНАЛОВ: {stats['found']}")
    print("="*70)
    
    return all_channels

def save_playlist(channels):
    """Сохранить только ваши каналы с категориями"""
    if not channels:
        print("\n❌ Ничего не найдено!")
        return False
    
    # Группировка
    grouped = {}
    for line, url, category in channels:
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(f"{line}\n{url}")
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🎯 ТОЛЬКО ВАШИ КАНАЛЫ!\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {len(channels)}\n\n')
            
            # Приоритет категорий
            priority = ['🎬 ФИЛЬМЫ И СЕРИАЛЫ', '🇷🇺 РОССИЯ', '🇲🇩 МОЛДОВА']
            
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
    channels = find_my_channels()
    if channels:
        save_playlist(channels)
        print("\n📎 ВАША ССЫЛКА:")
        print("https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
        print("\n✅ ВАШИ КАНАЛЫ:")
        print("   🎬 Фильмы и сериалы: 12 каналов")
        print("   🇷🇺 Россия: 3 канала")
        print("   🇲🇩 Молдова: 2 канала")
        print("\n🔄 Обновляется каждые 6 часов")
    else:
        print("\n❌ Каналы не найдены!")

if __name__ == "__main__":
    main()
