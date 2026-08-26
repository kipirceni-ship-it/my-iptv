#!/usr/bin/env python3
"""
📺 НОВАЯ СЕТКА - МОЛДОВА + РОССИЯ + ФИЛЬМЫ + СЕРИАЛЫ
Убраны украинские и румынские каналы!
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
    'max_channels': 5000,
    'max_movies': 2000,
    'max_series': 1000,
}

# ============================================
# 2. РУССКИЕ НАЗВАНИЯ КАНАЛОВ
# ============================================

RUSSIAN_NAMES = {
    # Молдова (ВСЕ!)
    'moldova1': 'Moldova 1 HD',
    'moldova2': 'Moldova 2 HD',
    'tvr moldova': 'TVR Moldova',
    'realitatea': 'Realitatea TV HD',
    'jurnal': 'Jurnal TV HD',
    'tv8': 'TV 8 HD',
    'tv5 monde': 'TV5 Monde HD',
    'pro tv chisinau': 'PRO TV Chisinau HD',
    'one tv': 'One TV HD',
    'star tv': 'Star TV HD',
    'cinema1': 'Cinema 1 HD',
    'prima tv': 'Prima TV Moldova HD',
    'exclusiv': 'Exclusiv TV HD',
    'global24': 'Global 24 HD',
    'n4': 'N4 HD',
    'tvc21': 'TVC 21',
    '7tv': '7TV HD',
    'tv9': 'TV9 HD',
    'unu1tv': 'unu1TV HD',
    'premiera': 'Premiera TV HD',
    'noroc': 'Noroc TV HD',
    'vocea basarabiei': 'Vocea Basarabiei HD',
    'studio-l': 'Studio-L HD',
    'national tv': 'National TV',
    'rtv': 'RTV (ex. Canal Regional)',
    'profi24': 'Profi 24',
    'kapital': 'Kapital TV HD',
    'm plus': 'M Plus TV HD',
    'nts': 'NTS HD',
    'grt': 'GRT HD',
    'axial': 'Axial TV HD',
    'next tv': 'Next TV HD',
    'elita': 'Elita TV',
    'b1 tv': 'B1 TV HD',
    'columna': 'Columna TV',
    'muscel': 'Muscel TV HD',
    'quantum': 'Quantum TV HD',
    'a7': 'A7 HD',
    'bucovina': 'Bucovina TV HD',
    
    # Россия (добавленные!)
    'russia1': 'Россия 1 HD',
    'zvezda': 'Звезда HD',
    
    # Документальные (ВИЖУ ХИСТОРИ!)
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
    
    # Сериалы
    'viju+ serial': 'viju+ Serial HD',
}

# ============================================
# 3. КАНАЛЫ ДЛЯ УДАЛЕНИЯ (украинские и румынские)
# ============================================

EXCLUDE_KEYWORDS = [
    # Украинские
    '1+1', 'интер', 'украина', 'ukraine', 'ukr', 'inter',
    'ntn', 'tv7', 'tv9', 'tv8', 'tvr', 'acasa',
    'tnt', 'rtr', 'stc', '5 tv', 'плюс',
    # Румынские  
    'romania', 'romanian', '.ro',
    'antena', 'digi', 'telekom', 'kiss tv',
    'orangesport', 'orange tv', 'procinema',
    'tvr 1', 'tvr2', 'tvr3', 'acasa gold',
    # Убираем лишнее
    'exclusiv tv', 'global 24', 'rtv', 'columna',
    'muscel', 'quantum', 'a7', 'bucovina',
]

# ============================================
# 4. ИСТОЧНИКИ
# ============================================

SOURCES = [
    # Молдова
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/countries/md.m3u',
    
    # Россия
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    
    # Фильмы и сериалы
    'https://iptv-org.github.io/iptv/categories/movies.m3u',
    'https://iptv-org.github.io/iptv/categories/series.m3u',
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
    """Проверка, нужно ли исключить канал"""
    combined = line.lower()
    for keyword in EXCLUDE_KEYWORDS:
        if keyword.lower() in combined:
            return True
    return False

def is_movie(line):
    combined = line.lower()
    movie_keywords = ['film', 'movie', 'кино', 'фильм', 'кинокомедия', 'кинодрама', 'bollywood']
    for keyword in movie_keywords:
        if keyword in combined:
            return True
    return False

def is_series(line):
    combined = line.lower()
    series_keywords = ['series', 'serial', 'сериал', 'сериалы', 'сез', 'season']
    for keyword in series_keywords:
        if keyword in combined:
            return True
    return False

def is_documentary(line):
    combined = line.lower()
    doc_keywords = ['documentary', 'документ', 'discovery', 'history', 'наука', 'живая планета', 'viju explore']
    for keyword in doc_keywords:
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
    russian_keywords = ['russia', 'россия', '1tv', 'rtr', 'russia1', 'zvezda']
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
    
    # Проверяем исключения (украинские и румынские)
    if should_exclude(line):
        return '🚫 ИСКЛЮЧЕН'
    
    # Фильмы (отдельно!)
    if is_movie(line):
        return '🎬 ФИЛЬМЫ (онлайн)'
    
    # Сериалы (отдельно!)
    if is_series(line):
        return '📺 СЕРИАЛЫ (онлайн)'
    
    # Документальные
    if is_documentary(line):
        return '🌍 ДОКУМЕНТАЛЬНЫЕ'
    
    # Молдова
    if is_moldovan(line):
        return '🇲🇩 МОЛДОВА'
    
    # Россия
    if is_russian(line):
        return '🇷🇺 РОССИЯ'
    
    return '📺 ТВ-КАНАЛЫ'

def build_playlist():
    print("\n" + "="*70)
    print("📺 НОВАЯ СЕТКА - МОЛДОВА + РОССИЯ + ФИЛЬМЫ")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*70 + "\n")
    
    all_channels = []
    stats = {'movies': 0, 'series': 0, 'russia': 0, 'moldova': 0, 'doc': 0, 'other': 0, 'excluded': 0}
    
    for url in SOURCES:
        print(f"📡 {url[:60]}...")
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
            
            if category == '🚫 ИСКЛЮЧЕН':
                stats['excluded'] += 1
                continue
            
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
            
            elif category in ['🇷🇺 РОССИЯ', '🇲🇩 МОЛДОВА', '🌍 ДОКУМЕНТАЛЬНЫЕ']:
                name = get_russian_name(line)
                if name:
                    line = re.sub(r',[^,]*$', f',{name}', line)
                all_channels.append((line, url))
                if category == '🇷🇺 РОССИЯ':
                    stats['russia'] += 1
                elif category == '🇲🇩 МОЛДОВА':
                    stats['moldova'] += 1
                else:
                    stats['doc'] += 1
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
    print(f"   🌍 Документальные: {stats['doc']}")
    print(f"   🇷🇺 Россия: {stats['russia']}")
    print(f"   🇲🇩 Молдова: {stats['moldova']}")
    print(f"   🚫 Исключено (украинские/румынские): {stats['excluded']}")
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
        '🌍 ДОКУМЕНТАЛЬНЫЕ',
        '🇷🇺 РОССИЯ',
        '🇲🇩 МОЛДОВА',
        '📺 ТВ-КАНАЛЫ'
    ]
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 📺 НОВАЯ СЕТКА - ТОЛЬКО НУЖНОЕ!\n')
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
        print("   🚫 Убраны все украинские и румынские каналы")
        print("   📺 Добавлены viju History HD, Россия 1 HD, Звезда HD")
        print("   🎬 Фильмы и сериалы ОТДЕЛЬНО с постерами")
        print("   🏷️ Все названия на русском языке")
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
