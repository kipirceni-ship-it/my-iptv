#!/usr/bin/env python3
"""
🎯 17 ВАШИХ КАНАЛОВ - С РАСШИРЕННЫМ ПОИСКОМ!
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
# 2. ВАШИ КАНАЛЫ С СИНОНИМАМИ (ДЛЯ ПОИСКА!)
# ============================================

CHANNELS_WITH_SYNONYMS = {
    # Фильмы и сериалы (12)
    'amedia premium hd': ['amedia premium', 'amedia', 'amedia hd'],
    'viju+ premiere': ['viju+ premiere', 'viju premiere', 'premiere'],
    'viju+ meghit': ['viju+ meghit', 'viju meghit', 'megahit'],
    'viju+ serial': ['viju+ serial', 'viju serial', 'serial'],
    'viju history': ['viju history', 'viju history hd', 'history'],
    'tv1000': ['tv1000', 'tv 1000'],
    'tv1000 русское кино': ['tv1000 русское', 'tv1000 русское кино', 'russian cinema'],
    'tv1000 action': ['tv1000 action', 'tv1000 action hd'],
    'кинопремьера': ['кинопремьера', 'kinopremiera'],
    'киносемья': ['киносемья', 'kinosemya'],
    'мужское кино': ['мужское кино', 'muzhskoe kino'],
    'мосфильм золотая коллекция': ['мосфильм', 'mosfilm', 'золотая коллекция'],
    
    # Россия (3)
    'россия 1': ['россия 1', 'russia 1', 'rtr', 'ртр', 'россия-1'],
    'звезда': ['звезда', 'zvezda', 'star'],
    'звезда плюс': ['звезда плюс', 'zvezda plus', 'star plus'],
    
    # Молдова (2)
    'tv7': ['tv7', '7tv', 'tv 7', 'seven tv', 'tv7 moldova'],
    'tv9': ['tv9', '9tv', 'tv 9', 'nine tv', 'tv9 moldova'],
}

# ============================================
# 3. КАТЕГОРИИ
# ============================================

CATEGORIES = {
    '🎬 ФИЛЬМЫ И СЕРИАЛЫ': list(CHANNELS_WITH_SYNONYMS.keys())[:12],
    '🇷🇺 РОССИЯ': list(CHANNELS_WITH_SYNONYMS.keys())[12:15],
    '🇲🇩 МОЛДОВА': list(CHANNELS_WITH_SYNONYMS.keys())[15:17],
}

# ============================================
# 4. ИСТОЧНИКИ (РАСШИРЕННЫЕ)
# ============================================

SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/countries/ru.m3u',
    'https://iptv-org.github.io/iptv/countries/md.m3u',
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    'https://iptv-org.github.io/iptv/categories/series.m3u',
    'https://raw.githubusercontent.com/Free-IPTV/Countries/master/RU.m3u',
    'https://raw.githubusercontent.com/Free-IPTV/Countries/master/MD.m3u',
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
                    key = hashlib.md5(line.lower().encode()).hexdigest()
                    if key not in seen:
                        seen.add(key)
                        channels.append((line, url))
                        i += 1
        i += 1
    return channels

def find_channel(line):
    """Поиск канала с учётом синонимов"""
    line_lower = line.lower()
    
    for main_name, synonyms in CHANNELS_WITH_SYNONYMS.items():
        for synonym in synonyms:
            if synonym.lower() in line_lower:
                return main_name
    
    return None

def get_category(main_name):
    """Определить категорию"""
    for category, channels in CATEGORIES.items():
        if main_name in channels:
            return category
    return None

def clean_name(line):
    """Очистить название"""
    line = re.sub(r'\([^)]*\)', '', line)
    line = re.sub(r'\[[^\]]*\]', '', line)
    line = re.sub(r'HD|SD|FULL|4K|1080|720', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+', ' ', line)
    return line.strip()

def get_poster(title):
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    color = colors[hash(title) % len(colors)]
    clean = title[:20] + '…' if len(title) > 20 else title
    
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='200' height='280'>
        <rect width='200' height='280' fill='{color}' rx='8'/>
        <text x='100' y='150' font-family='Arial' font-size='18' fill='white' text-anchor='middle' font-weight='bold'>{clean}</text>
        <text x='100' y='245' font-family='Arial' font-size='12' fill='rgba(255,255,255,0.7)' text-anchor='middle'>▶ Нажми для просмотра</text>
    </svg>"""
    
    return "data:image/svg+xml," + svg.replace(' ', '%20').replace('\n', '')

def build_playlist():
    """Сборка только ваших каналов"""
    print("\n" + "="*60)
    print("🎯 ПОИСК 17 ВАШИХ КАНАЛОВ (С СИНОНИМАМИ!)")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    found = {}
    seen_urls = set()
    
    for url in SOURCES:
        print(f"📡 {url[:50]}...")
        content = download_m3u(url)
        if not content:
            print("    ❌ Недоступно")
            continue
        
        channels = parse_m3u(content)
        print(f"    ✅ Найдено: {len(channels)}")
        
        for line, url in channels:
            # Проверяем, есть ли этот канал в вашем списке
            main_name = find_channel(line)
            if not main_name:
                continue
            
            # Проверяем дубликаты (по URL)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Определяем категорию
            category = get_category(main_name)
            if not category:
                continue
            
            # Чистим название
            name_match = re.search(r',([^,]+)$', line)
            if name_match:
                name = name_match.group(1).strip()
                clean = clean_name(name)
                
                # Добавляем постер для фильмов
                if 'ФИЛЬМЫ' in category or 'СЕРИАЛЫ' in category:
                    poster = get_poster(clean)
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                
                # Заменяем название на чистое (используем главное имя)
                line = re.sub(r',[^,]*$', f',{main_name}', line)
            
            # Сохраняем
            if main_name not in found:
                found[main_name] = []
            found[main_name].append((line, url, category))
    
    print("\n" + "="*60)
    print(f"📊 НАЙДЕНО КАНАЛОВ: {len(found)} из 17")
    print("="*60)
    
    # Показываем, что найдено
    for name in YOUR_CHANNELS:
        if name in found:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} - НЕ НАЙДЕН")
    
    return found

def save_playlist(found):
    """Сохранить плейлист"""
    if not found:
        print("\n❌ Каналы не найдены!")
        return False
    
    # Сортируем по категориям
    grouped = {}
    for main_name, channels in found.items():
        category = get_category(main_name)
        if category not in grouped:
            grouped[category] = []
        for line, url, _ in channels:
            grouped[category].append(f"{line}\n{url}")
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🎯 17 ВАШИХ КАНАЛОВ!\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {sum(len(v) for v in found.values())}\n\n')
            
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
        print(f"📊 Каналов: {sum(len(v) for v in found.values())}")
        print(f"📁 Размер: {size:.1f} KB")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    found = build_playlist()
    if found:
        save_playlist(found)
        print("\n📎 ВАША ССЫЛКА:")
        print("https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
        print("\n🔄 Обновляется каждые 6 часов")
    else:
        print("\n❌ Каналы не найдены!")

if __name__ == "__main__":
    main()
