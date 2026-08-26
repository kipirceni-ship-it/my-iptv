#!/usr/bin/env python3
"""
🎬 LAMPA СТИЛЬ - ФИЛЬМЫ И СЕРИАЛЫ С ПОСТЕРАМИ!
Тысячи фильмов и сериалов с постерами для любого плеера
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
    'max_movies': 3000,
    'max_series': 2000,
}

# ============================================
# 2. РУССКИЕ НАЗВАНИЯ КАНАЛОВ
# ============================================

RUSSIAN_NAMES = {
    '1tv': 'Первый канал',
    'russia1': 'Россия 1',
    'russia24': 'Россия 24',
    'ntv': 'НТВ',
    'tnt': 'ТНТ',
    'sts': 'СТС',
    'ren': 'РЕН ТВ',
    '5tv': 'Пятый канал',
    'zvezda': 'Звезда',
    'match': 'Матч ТВ',
    'spas': 'Спас',
    'karusel': 'Карусель',
    'primul': 'Primul Canal',
    'publika': 'Publika TV',
    'jurnal': 'Jurnal TV',
    'tv8': 'TV8',
    'moldova1': 'Moldova 1',
    'moldova2': 'Moldova 2',
}

# ============================================
# 3. ИСТОЧНИКИ
# ============================================

SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    'https://iptv-org.github.io/iptv/categories/series.m3u',
    'https://iptv-org.github.io/iptv/categories/kids.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
    'https://raw.githubusercontent.com/Free-IPTV/Countries/master/movies.m3u',
]

# ============================================
# 4. КЛЮЧЕВЫЕ СЛОВА
# ============================================

MOVIE_KEYWORDS = [
    'film', 'movie', 'кино', 'фильм', 'кинокомедия', 'кинодрама',
    'боевик', 'триллер', 'детектив', 'мелодрама', 'комедия',
    'фантастика', 'приключения', 'ужасы', 'мистика',
    'tv1000', 'мосфильм', 'mosfilm', 'dom kino', 'дом кино',
    'hollywood', 'голливуд', 'filmua',
    'кинохит', 'киносвидание', 'кинопремьера', 'иллюзион',
]

SERIES_KEYWORDS = [
    'series', 'serial', 'сериал', 'сериалы', 'сез', 'season',
    'эпизод', 'episode', 'серия', 'сборник', 'тв шоу', 'tv show',
    'telenovela', 'soap opera', 'sitcom',
    'детективный сериал', 'криминальный сериал', 'турецкий сериал',
    'бразильский сериал', 'мексиканский сериал', 'американский сериал',
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
    """Создать красивый постер для фильма/сериала"""
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
    combined = line.lower()
    for keyword in MOVIE_KEYWORDS:
        if keyword.lower() in combined:
            return True
    return False

def is_series(line):
    combined = line.lower()
    for keyword in SERIES_KEYWORDS:
        if keyword.lower() in combined:
            return True
    return False

def is_russian(line):
    combined = line.lower()
    russian_keywords = ['1tv', 'russia', 'россия', 'rtr', 'ntv', 'тнт', 'tnt', 'sts', 'рен', 'ren']
    for keyword in russian_keywords:
        if keyword.lower() in combined:
            return True
    return False

def is_moldovan(line):
    combined = line.lower()
    moldovan_keywords = ['moldova', 'молдова', 'md', 'primul', 'publika', 'jurnal', 'tv8']
    for keyword in moldovan_keywords:
        if keyword.lower() in combined:
            return True
    return False

def get_category(line, url):
    combined = (line + ' ' + url).lower()
    
    if is_series(line):
        return '📺 СЕРИАЛЫ (онлайн)'
    elif is_movie(line):
        return '🎬 ФИЛЬМЫ (онлайн)'
    elif is_moldovan(line):
        return '🇲🇩 МОЛДОВА'
    elif is_russian(line):
        return '🇷🇺 РОССИЯ'
    else:
        return '📺 ТВ-КАНАЛЫ'

def build_playlist():
    print("\n" + "="*70)
    print("🎬 LAMPA СТИЛЬ - ФИЛЬМЫ И СЕРИАЛЫ С ПОСТЕРАМИ!")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    all_channels = []
    stats = {'movies': 0, 'series': 0, 'russia': 0, 'moldova': 0, 'other': 0}
    total_sources = len(SOURCES)
    
    for i, url in enumerate(SOURCES, 1):
        print(f"[{i}/{total_sources}] 📡 {url[:60]}...")
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
                
            elif category == '🇷🇺 РОССИЯ':
                for eng, rus in RUSSIAN_NAMES.items():
                    if eng.lower() in line.lower():
                        line = re.sub(r',[^,]*$', f',{rus}', line)
                        break
                all_channels.append((line, url))
                stats['russia'] += 1
                added += 1
                
            elif category == '🇲🇩 МОЛДОВА':
                all_channels.append((line, url))
                stats['moldova'] += 1
                added += 1
                
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
    print(f"   📺 Другие каналы: {stats['other']}")
    print("="*70)
    
    return all_channels

def save_playlist(channels):
    if not channels:
        print("\n❌ Нет каналов!")
        return False
    
    grouped = {}
    for line, url in channels:
        category = get_category(line, url)
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(f"{line}\n{url}")
    
    priority = ['🎬 ФИЛЬМЫ (онлайн)', '📺 СЕРИАЛЫ (онлайн)', '🇷🇺 РОССИЯ', '🇲🇩 МОЛДОВА', '📺 ТВ-КАНАЛЫ']
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🎬 LAMPA СТИЛЬ - ФИЛЬМЫ И СЕРИАЛЫ!\n')
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
        print("\n🎬 КАК ЭТО РАБОТАЕТ:")
        print("   1. В плейлисте есть категории:")
        print("      🎬 ФИЛЬМЫ (онлайн) - тысячи фильмов с постерами")
        print("      📺 СЕРИАЛЫ (онлайн) - тысячи сериалов с постерами")
        print("   2. Вы видите ПОСТЕРЫ фильмов и сериалов")
        print("   3. Нажимаете на постер → начинается просмотр")
        print("   4. Это работает в ЛЮБОМ плеере (VLC, TiviMate, IPTV Smarters)")
        print("\n📱 ЛУЧШИЕ ПЛЕЕРЫ:")
        print("   📺 TiviMate (Android TV) - показывает постеры!")
        print("   📺 IPTV Smarters (все платформы)")
        print("   📺 VLC (компьютер, телефон)")
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
