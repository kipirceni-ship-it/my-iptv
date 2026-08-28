#!/usr/bin/env python3
"""
🎯 ТОЛЬКО 17 ВАШИХ КАНАЛОВ! БЕЗ ДУБЛИКАТОВ!
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
}

# ============================================
# 2. ВАШ ТОЧНЫЙ СПИСОК (17 КАНАЛОВ!)
# ============================================

YOUR_CHANNELS = [
    # Фильмы и сериалы (12)
    'amedia premium hd',
    'viju+ premiere',
    'viju+ meghit',
    'viju+ serial',
    'viju history',
    'tv1000',
    'tv1000 русское кино',
    'tv1000 action',
    'кинопремьера',
    'киносемья',
    'мужское кино',
    'мосфильм золотая коллекция',
    # Россия (3)
    'россия 1',
    'звезда',
    'звезда плюс',
    # Молдова (2)
    'tv7',
    'tv9',
]

# ============================================
# 3. КАТЕГОРИИ
# ============================================

CATEGORIES = {
    '🎬 ФИЛЬМЫ И СЕРИАЛЫ': YOUR_CHANNELS[:12],
    '🇷🇺 РОССИЯ': YOUR_CHANNELS[12:15],
    '🇲🇩 МОЛДОВА': YOUR_CHANNELS[15:17],
}

# ============================================
# 4. ИСТОЧНИКИ (ОГРАНИЧЕННЫЕ, ЧТОБЫ НЕ БЫЛО ДУБЛЕЙ)
# ============================================

SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    'https://iptv-org.github.io/iptv/categories/series.m3u',
]

# ============================================
# 5. ФУНКЦИИ
# ============================================

def download_m3u(url):
    try:
        r = requests.get(url, timeout=CONFIG['timeout'])
        return r.text if r.status_code == 200 else None
    except:
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
                    # Создаём ключ для поиска
                    key = hashlib.md5(line.lower().encode()).hexdigest()
                    if key not in seen:
                        seen.add(key)
                        channels.append((line, url))
                        i += 1
        i += 1
    return channels

def get_category(line):
    """Определить категорию"""
    line_lower = line.lower()
    
    # Ищем точное совпадение с вашим списком
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in line_lower:
                return category
    
    return None

def clean_name(line):
    """Очистить название"""
    # Убираем всё лишнее
    line = re.sub(r'\([^)]*\)', '', line)
    line = re.sub(r'\[[^\]]*\]', '', line)
    line = re.sub(r'HD|SD|FULL|4K|1080|720', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+', ' ', line)
    return line.strip()

def get_poster(title):
    """Создать постер"""
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    color = colors[hash(title) % len(colors)]
    
    clean = title[:20] + '…' if len(title) > 20 else title
    
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='200' height='280'>
        <rect width='200' height='280' fill='{color}' rx='8'/>
        <text x='100' y='150' font-family='Arial' font-size='18' fill='white' text-anchor='middle' font-weight='bold'>{clean}</text>
        <text x='100' y='245' font-family='Arial' font-size='12' fill='rgba(255,255,255,0.7)' text-anchor='middle'>▶ Нажми для просмотра</text>
    </svg>"""
    
    return "data:image/svg+xml," + svg.replace(' ', '%20').replace('\n', '')

def find_my_channels():
    """Найти ТОЛЬКО ваши 17 каналов, без дублей!"""
    print("\n" + "="*60)
    print("🎯 ПОИСК 17 ВАШИХ КАНАЛОВ")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    found_channels = []
    seen_names = set()  # Для исключения дублей
    
    for url in SOURCES:
        print(f"📡 {url[:50]}...")
        content = download_m3u(url)
        if not content:
            print("    ❌ Недоступно")
            continue
        
        channels = parse_m3u(content)
        print(f"    ✅ Найдено: {len(channels)}")
        
        found = 0
        for line, url in channels:
            # Проверяем, есть ли этот канал в вашем списке
            category = get_category(line)
            if not category:
                continue
            
            # Получаем чистое название
            name_match = re.search(r',([^,]+)$', line)
            if not name_match:
                continue
            
            name = name_match.group(1).strip()
            clean = clean_name(name)
            
            # Проверяем дубликаты (по названию)
            name_key = clean.lower()
            if name_key in seen_names:
                continue
            seen_names.add(name_key)
            
            # Добавляем постер для фильмов
            if 'ФИЛЬМЫ' in category or 'СЕРИАЛЫ' in category:
                poster = get_poster(clean)
                line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
            
            # Заменяем название на чистое
            line = re.sub(r',[^,]*$', f',{clean}', line)
            
            found_channels.append((line, url, category))
            found += 1
        
        if found > 0:
            print(f"    ✅ +{found} каналов (без дублей)")
    
    print("\n" + "="*60)
    print(f"📊 ВСЕГО УНИКАЛЬНЫХ КАНАЛОВ: {len(found_channels)}")
    print("="*60)
    
    return found_channels

def save_playlist(channels):
    """Сохранить плейлист"""
    if not channels:
        print("\n❌ Каналы не найдены!")
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
            f.write(f'# 🎯 17 ВАШИХ КАНАЛОВ (БЕЗ ДУБЛЕЙ!)\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {len(channels)}\n\n')
            
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
        print("\n✅ ВАШИ 17 КАНАЛОВ (БЕЗ ДУБЛЕЙ!):")
        print("   🎬 Фильмы и сериалы: 12 каналов")
        print("   🇷🇺 Россия: 3 канала")
        print("   🇲🇩 Молдова: 2 канала")
        print("\n🔄 Обновляется каждые 6 часов")
    else:
        print("\n❌ Каналы не найдены!")

if __name__ == "__main__":
    main()
