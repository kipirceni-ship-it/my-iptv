#!/usr/bin/env python3
"""
📺 НОВАЯ СЕТКА - МОЛДОВА + РОССИЯ + ФИЛЬМЫ + СЕРИАЛЫ
С РАБОЧИМИ ИСТОЧНИКАМИ ФИЛЬМОВ!
"""

import requests
import hashlib
import os
import re
import time
import json
from datetime import datetime

# ============================================
# 1. НАСТРОЙКИ
# ============================================

CONFIG = {
    'timeout': 15,
    'max_channels': 5000,
    'max_movies': 3000,
    'max_series': 2000,
}

# ============================================
# 2. РУССКИЕ НАЗВАНИЯ КАНАЛОВ
# ============================================

RUSSIAN_NAMES = {
    'moldova1': 'Moldova 1 HD',
    'moldova2': 'Moldova 2 HD',
    'tvr moldova': 'TVR Moldova',
    'realitatea': 'Realitatea TV HD',
    'jurnal': 'Jurnal TV HD',
    'tv8': 'TV 8 HD',
    'tv9': 'TV9 HD',
    'noroc': 'Noroc TV HD',
    'pro tv': 'PRO TV Chisinau HD',
    'prima tv': 'Prima TV Moldova HD',
    'exclusiv': 'Exclusiv TV HD',
    'global24': 'Global 24 HD',
    'n4': 'N4 HD',
    'tvc21': 'TVC 21',
    '7tv': '7TV HD',
    'premiera': 'Premiera TV HD',
    'studio-l': 'Studio-L HD',
    'national tv': 'National TV',
    'rtv': 'RTV',
    'profi24': 'Profi 24',
    'kapital': 'Kapital TV HD',
    'm plus': 'M Plus TV HD',
    'nts': 'NTS HD',
    'grt': 'GRT HD',
    'axial': 'Axial TV HD',
    'next tv': 'Next TV HD',
    'elita': 'Elita TV',
    'b1 tv': 'B1 TV HD',
    
    # Россия
    'russia1': 'Россия 1 HD',
    'zvezda': 'Звезда HD',
    'russia24': 'Россия 24 HD',
    'ntv': 'НТВ HD',
    'tnt': 'ТНТ HD',
    'sts': 'СТС HD',
    'ren': 'РЕН ТВ HD',
    '5tv': 'Пятый канал HD',
    'match': 'Матч ТВ HD',
    'spas': 'Спас HD',
    'karusel': 'Карусель HD',
    '1tv': 'Первый канал HD',
    
    # Документальные
    'viju history': 'viju History HD',
    'viju explore': 'viju Explore HD',
    'national geographic': 'National Geographic HD',
    'discovery': 'Discovery Channel HD',
    'animal planet': 'Animal Planet HD',
    'history': 'History HD',
    'наука': 'Наука HD',
    'живая планета': 'Живая Планета',
    'investigation discovery': 'Investigation Discovery HD',
    'love nature': 'Love Nature HD',
    'nat geo wild': 'Nat Geo Wild HD',
    'viju nature': 'viju Nature HD',
    
    # Фильмы
    'viju tv1000': 'viju TV1000 HD',
    'viju tv1000 action': 'viju TV1000 action HD',
    'viju tv1000 новелла': 'viju TV1000 новелла HD',
    'bollywood': 'Bollywood Clasic HD',
    'родное кино': 'Родное Кино',
    'fx': 'FX HD',
    'киномикс': 'Киномикс HD',
    'bbc first': 'BBC First HD',
    'кинопремьера': 'Кинопремьера HD',
    'cinemaraton': 'Cinemaraton Moldova HD',
    'киносемья': 'Киносемья',
    'кинохит': 'Кинохит HD',
    'filmua drama': 'FilmuaDrama',
    'наше новое кино': 'Наше Новое Кино',
    'кино тв': 'Кино ТВ HD',
    'мужское кино': 'Мужское Кино',
    'viju+ meghit': 'viju+ Megahit HD',
    'viju+ premiere': 'viju+ Premiere HD',
    'viju+ comedy': 'viju+ Comedy HD',
    'viju+ serial': 'viju+ Serial HD',
    'cinewow': 'CineWow HD',
    'fx life': 'FX Life HD',
    'кинокомедия': 'Кинокомедия',
}

# ============================================
# 3. ИСКЛЮЧАЕМ УКРАИНСКИЕ И РУМЫНСКИЕ
# ============================================

EXCLUDE_KEYWORDS = [
    'ukraine', 'ukr', 'inter', 'ntn', 'tvr', 'acasa',
    'romania', 'romanian', '.ro', 'antena', 'digi', 'telekom',
    'kiss tv', 'orangesport', 'orange tv', 'procinema',
    'tvr1', 'tvr2', 'tvr3', 'acasa gold',
]

# ============================================
# 4. ИСТОЧНИКИ (РАБОЧИЕ!)
# ============================================

SOURCES = {
    'tv': [
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
        'https://iptv-org.github.io/iptv/countries/md.m3u',
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    ],
    'movies': [
        'https://iptv-org.github.io/iptv/categories/movies.m3u',
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
    ],
    'series': [
        'https://iptv-org.github.io/iptv/categories/series.m3u',
    ],
    'documentary': [
        'https://iptv-org.github.io/iptv/categories/documentary.m3u',
    ],
}

# ============================================
# 5. ФУНКЦИИ
# ============================================

def download_m3u(url):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=CONFIG['timeout'])
            if r.status_code == 200:
                return r.text
            elif r.status_code == 404:
                print(f"    ⚠️ 404 - файл не найден")
                return None
        except Exception as e:
            print(f"    ⚠️ Попытка {attempt+1}: {str(e)[:30]}")
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

def get_poster(title):
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

def should_exclude(line):
    combined = line.lower()
    for keyword in EXCLUDE_KEYWORDS:
        if keyword.lower() in combined:
            return True
    return False

def is_movie(line):
    combined = line.lower()
    movie_keywords = [
        'фильм', 'кино', 'movie', 'film', 'кинокомедия', 'кинодрама',
        'bollywood', 'tv1000', 'мосфильм', 'кинопремьера', 'кинохит',
        'киносемья', 'мужское кино', 'родное кино'
    ]
    for keyword in movie_keywords:
        if keyword in combined:
            return True
    return False

def is_series(line):
    combined = line.lower()
    series_keywords = ['сериал', 'сериалы', 'series', 'serial', 'сез', 'season', 'эпизод']
    for keyword in series_keywords:
        if keyword in combined:
            return True
    return False

def is_moldovan(line):
    combined = line.lower()
    moldovan_keywords = ['moldova', 'молдова', 'md', 'primul', 'publika', 'jurnal', 'tv8', 'tv9', 'noroc']
    for keyword in moldovan_keywords:
        if keyword in combined:
            return True
    return False

def is_russian(line):
    combined = line.lower()
    russian_keywords = ['russia', 'россия', '1tv', 'rtr', 'russia1', 'zvezda', 'russia24', 'ntv', 'тнт']
    for keyword in russian_keywords:
        if keyword in combined:
            return True
    return False

def get_russian_name(line):
    combined = line.lower()
    for eng, rus in RUSSIAN_NAMES.items():
        if eng in combined:
            return rus
    return None

def get_category(line, url):
    combined = (line + ' ' + url).lower()
    
    if should_exclude(line):
        return '🚫 ИСКЛЮЧЕН'
    
    if is_series(line):
        return '📺 СЕРИАЛЫ (онлайн)'
    
    if is_movie(line):
        return '🎬 ФИЛЬМЫ (онлайн)'
    
    if is_moldovan(line):
        return '🇲🇩 МОЛДОВА'
    
    if is_russian(line):
        return '🇷🇺 РОССИЯ'
    
    return '📺 ТВ-КАНАЛЫ'

def build_playlist():
    print("\n" + "="*70)
    print("📺 СБОРКА - МОЛДОВА + РОССИЯ + ФИЛЬМЫ + СЕРИАЛЫ")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    all_channels = []
    stats = {'movies': 0, 'series': 0, 'russia': 0, 'moldova': 0, 'other': 0, 'excluded': 0}
    
    for source_type, urls in SOURCES.items():
        if source_type == 'tv':
            print("📡 ТВ-КАНАЛЫ:")
        elif source_type == 'movies':
            print("\n🎬 ФИЛЬМЫ (ищу источники...):")
        elif source_type == 'series':
            print("\n📺 СЕРИАЛЫ (ищу источники...):")
        elif source_type == 'documentary':
            print("\n🌍 ДОКУМЕНТАЛЬНЫЕ:")
        
        for url in urls:
            print(f"  📥 {url}")
            content = download_m3u(url)
            if not content:
                print("    ❌ Недоступно")
                continue
            
            channels = parse_m3u(content)
            print(f"    ✅ Найдено: {len(channels)}")
            added = 0
            
            for line, url in channels:
                if len(all_channels) >= CONFIG['max_channels']:
                    break
                
                category = get_category(line, url)
                
                if category == '🚫 ИСКЛЮЧЕН':
                    stats['excluded'] += 1
                    continue
                
                if category in ['🎬 ФИЛЬМЫ (онлайн)', '📺 СЕРИАЛЫ (онлайн)']:
                    # Проверяем лимиты
                    if category == '🎬 ФИЛЬМЫ (онлайн)' and stats['movies'] >= CONFIG['max_movies']:
                        continue
                    if category == '📺 СЕРИАЛЫ (онлайн)' and stats['series'] >= CONFIG['max_series']:
                        continue
                    
                    # Добавляем постер
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        name = name_match.group(1).strip()
                        poster = get_poster(name)
                        line = re.sub(r',[^,]*$', f',{name}', line)
                        line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
                    
                    all_channels.append((line, url))
                    if category == '🎬 ФИЛЬМЫ (онлайн)':
                        stats['movies'] += 1
                    else:
                        stats['series'] += 1
                    added += 1
                
                elif category in ['🇷🇺 РОССИЯ', '🇲🇩 МОЛДОВА']:
                    name = get_russian_name(line)
                    if name:
                        line = re.sub(r',[^,]*$', f',{name}', line)
                    all_channels.append((line, url))
                    if category == '🇷🇺 РОССИЯ':
                        stats['russia'] += 1
                    else:
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
    print(f"   🚫 Исключено: {stats['excluded']}")
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
    
    priority = [
        '🎬 ФИЛЬМЫ (онлайн)',
        '📺 СЕРИАЛЫ (онлайн)',
        '🇷🇺 РОССИЯ',
        '🇲🇩 МОЛДОВА',
        '📺 ТВ-КАНАЛЫ'
    ]
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 📺 МОЛДОВА + РОССИЯ + ФИЛЬМЫ + СЕРИАЛЫ\n')
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
        print("\n✅ ЧТО СДЕЛАНО:")
        print("   🎬 Фильмы - ищем в 2-х источниках")
        print("   📺 Сериалы - ищем в 1-м источнике")
        print("   🇷🇺 Россия - все федеральные")
        print("   🇲🇩 Молдова - все каналы")
        print("   🚫 Убраны украинские и румынские")
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
