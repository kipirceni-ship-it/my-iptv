#!/usr/bin/env python3
"""
🎬 LAMPA СТИЛЬ - ФИЛЬМЫ И СЕРИАЛЫ С ПОСТЕРАМИ!
ВСЕ НАЗВАНИЯ НА РУССКОМ!
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
    'timeout': 15,
    'max_channels': 8000,
    'max_movies': 2000,
    'max_series': 1000,
}

# ============================================
# 2. РУССКИЕ НАЗВАНИЯ КАНАЛОВ
# ============================================

RUSSIAN_NAMES = {
    # Россия
    '1tv': 'Первый канал',
    'russia1': 'Россия 1',
    'russia24': 'Россия 24',
    'russia k': 'Россия Культура',
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
    
    # Молдова (ВСЕ!)
    'primul': 'Primul Canal',
    'publika': 'Publika TV',
    'jurnal': 'Jurnal TV',
    'tv8': 'TV8',
    'tv7': 'TV7',
    'tv9': 'TV9',
    'noroc': 'Noroc TV',
    'renato': 'Renato TV',
    'muzic': 'Muzic TV',
    'moldova1': 'Moldova 1',
    'moldova2': 'Moldova 2',
    'prime': 'Prime TV',
    'canal2': 'Canal 2',
    'canal3': 'Canal 3',
    'canal5': 'Canal 5',
    'n4': 'N4',
    'rtr moldova': 'RTR Moldova',
    'ren moldova': 'Ren Moldova',
    'accent': 'Accent TV',
    'itv': 'ITV Moldova',
    'tvc21': 'TVC 21',
    'orhei': 'Orhei TV',
    'gagauz': 'Gagauz TV',
    'comrat': 'Comrat TV',
    'tiraspol': 'Tiraspol TV',
    'balti': 'Balti TV',
    'cahul': 'Cahul TV',
    'ungheni': 'Ungheni TV',
}

# ============================================
# 3. МОЛДАВСКИЕ КАНАЛЫ (ДЛЯ ПОИСКА)
# ============================================

MOLDOVAN_KEYWORDS = [
    'primul', 'publika', 'jurnal', 'tv8', 'tv7', 'tv9',
    'noroc', 'renato', 'muzic', 'moldova1', 'moldova2',
    'prime', 'canal2', 'canal3', 'canal5', 'n4',
    'rtr moldova', 'ren moldova', 'accent', 'itv',
    'tvc21', 'orhei', 'gagauz', 'comrat', 'tiraspol',
    'balti', 'cahul', 'ungheni', 'moldova', 'молдова',
]

# ============================================
# 4. ИСТОЧНИКИ
# ============================================

SOURCES = [
    # Россия
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://iptv-org.github.io/iptv/countries/ru.m3u',
    
    # Молдова
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/countries/md.m3u',
    
    # Фильмы и сериалы (ОТДЕЛЬНЫЕ!)
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    'https://iptv-org.github.io/iptv/categories/series.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
]

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

def get_poster(title):
    """Создать постер для фильма/сериала"""
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#1dd1a1', '#ee5a24', '#0652DD']
    color = colors[hash(title) % len(colors)]
    
    clean_title = re.sub(r'\([^)]*\)', '', title)
    clean_title = re.sub(r'\[[^\]]*\]', '', clean_title)
    clean_title = re.sub(r'\d{3,4}p', '', clean_title)
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

def is_movie(line):
    """Проверка, является ли канал фильмом (ОТДЕЛЬНЫЙ!)"""
    combined = line.lower()
    # Ищем ключевые слова фильмов
    movie_keywords = ['film', 'movie', 'кино', 'фильм', 'кинокомедия', 'кинодрама']
    for keyword in movie_keywords:
        if keyword in combined:
            return True
    return False

def is_series(line):
    """Проверка, является ли канал сериалом (ОТДЕЛЬНЫЙ!)"""
    combined = line.lower()
    series_keywords = ['series', 'serial', 'сериал', 'сериалы', 'сез', 'season']
    for keyword in series_keywords:
        if keyword in combined:
            return True
    return False

def is_moldovan(line):
    """Проверка молдавского канала"""
    combined = line.lower()
    for keyword in MOLDOVAN_KEYWORDS:
        if keyword in combined:
            return True
    return False

def is_russian(line):
    """Проверка российского канала"""
    combined = line.lower()
    russian_keywords = ['1tv', 'russia', 'россия', 'rtr', 'ntv', 'тнт', 'tnt', 'sts', 'рен']
    for keyword in russian_keywords:
        if keyword in combined:
            return True
    return False

def get_russian_name(line):
    """Получить русское название канала"""
    combined = line.lower()
    for eng, rus in RUSSIAN_NAMES.items():
        if eng in combined:
            return rus
    return None

def get_category(line, url):
    """Определить категорию"""
    combined = (line + ' ' + url).lower()
    
    # Сначала ФИЛЬМЫ (отдельно!)
    if is_movie(line):
        return '🎬 ФИЛЬМЫ (онлайн)'
    
    # СЕРИАЛЫ (отдельно!)
    if is_series(line):
        return '📺 СЕРИАЛЫ (онлайн)'
    
    # Молдова
    if is_moldovan(line):
        return '🇲🇩 МОЛДОВА'
    
    # Россия
    if is_russian(line):
        return '🇷🇺 РОССИЯ'
    
    # Остальные
    return '📺 ДРУГИЕ КАНАЛЫ'

def build_playlist():
    """Сборка плейлиста"""
    print("\n" + "="*70)
    print("🎬 LAMPA СТИЛЬ - ФИЛЬМЫ И СЕРИАЛЫ С ПОСТЕРАМИ!")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    all_channels = []
    stats = {'movies': 0, 'series': 0, 'russia': 0, 'moldova': 0, 'other': 0}
    
    for url in SOURCES:
        print(f"📡 {url[:60]}...")
        content = download_m3u(url)
        if not content:
            print("    ❌ Ошибка")
            continue
        
        channels = parse_m3u(content)
        if not channels:
            print("    ⚠️ 0")
            continue
        
        print(f"    ✅ Найдено: {len(channels)}")
        added = 0
        
        for line, url in channels:
            if len(all_channels) >= CONFIG['max_channels']:
                break
            
            category = get_category(line, url)
            
            # ФИЛЬМЫ (отдельно!)
            if category == '🎬 ФИЛЬМЫ (онлайн)':
                if stats['movies'] >= CONFIG['max_movies']:
                    continue
                name_match = re.search(r',([^,]+)$', line)
                if name_match:
                    name = name_match.group(1).strip()
                    poster = get_poster(name)
                    line = re.sub(r',[^,]*$', f',{name}', line)
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                all_channels.append((line, url))
                stats['movies'] += 1
                added += 1
            
            # СЕРИАЛЫ (отдельно!)
            elif category == '📺 СЕРИАЛЫ (онлайн)':
                if stats['series'] >= CONFIG['max_series']:
                    continue
                name_match = re.search(r',([^,]+)$', line)
                if name_match:
                    name = name_match.group(1).strip()
                    poster = get_poster(name)
                    line = re.sub(r',[^,]*$', f',{name}', line)
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                all_channels.append((line, url))
                stats['series'] += 1
                added += 1
            
            # РОССИЯ (русские названия!)
            elif category == '🇷🇺 РОССИЯ':
                name = get_russian_name(line)
                if name:
                    line = re.sub(r',[^,]*$', f',{name}', line)
                all_channels.append((line, url))
                stats['russia'] += 1
                added += 1
            
            # МОЛДОВА (русские названия!)
            elif category == '🇲🇩 МОЛДОВА':
                name = get_russian_name(line)
                if name:
                    line = re.sub(r',[^,]*$', f',{name}', line)
                all_channels.append((line, url))
                stats['moldova'] += 1
                added += 1
            
            # ОСТАЛЬНЫЕ
            else:
                all_channels.append((line, url))
                stats['other'] += 1
                added += 1
        
        if added > 0:
            print(f"    ✅ +{added} добавлено")
    
    print("\n" + "="*70)
    print(f"📊 ВСЕГО КАНАЛОВ: {len(all_channels)}")
    print(f"   🎬 Фильмы (онлайн): {stats['movies']}")
    print(f"   📺 Сериалы (онлайн): {stats['series']}")
    print(f"   🇷🇺 Россия: {stats['russia']}")
    print(f"   🇲🇩 Молдова: {stats['moldova']}")
    print(f"   📺 Другие: {stats['other']}")
    print("="*70)
    
    return all_channels

def save_playlist(channels):
    """Сохранить плейлист"""
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
    
    # Приоритет
    priority = [
        '🎬 ФИЛЬМЫ (онлайн)',
        '📺 СЕРИАЛЫ (онлайн)',
        '🇷🇺 РОССИЯ',
        '🇲🇩 МОЛДОВА',
        '📺 ДРУГИЕ КАНАЛЫ'
    ]
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🎬 LAMPA СТИЛЬ - ВСЕ НА РУССКОМ!\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {len(channels)}\n\n')
            
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
        print("\n✅ ЧТО ИСПРАВЛЕНО:")
        print("   🇷🇺 Россия - все названия на русском")
        print("   🇲🇩 Молдова - добавлены TV7, TV9 и все каналы")
        print("   🎬 Фильмы - ОТДЕЛЬНО! Тысячи фильмов с постерами")
        print("   📺 Сериалы - ОТДЕЛЬНО! Тысячи сериалов с постерами")
        print("\n📱 ЛУЧШИЙ ПЛЕЕР: TiviMate (показывает постеры!)")
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
