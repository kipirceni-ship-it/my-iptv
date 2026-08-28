#!/usr/bin/env python3
"""
📺 ПЛЕЙЛИСТ ДЛЯ LG TV - С РАСШИРЕННЫМ ПОИСКОМ!
"""

import requests
import hashlib
import os
import re
from datetime import datetime

# ============================================
# 1. ВАШИ КАНАЛЫ + СИНОНИМЫ (ДЛЯ ПОИСКА!)
# ============================================

CHANNELS = {
    # ===== ФИЛЬМЫ =====
    'Amedia Premium HD': ['amedia premium', 'amedia', 'amedia hd'],
    'viju+ Premiere': ['viju+ premiere', 'viju premiere', 'premiere'],
    'viju+ Megahit': ['viju+ meghit', 'viju meghit', 'megahit'],
    'viju+ Serial': ['viju+ serial', 'viju serial', 'serial'],
    'viju History': ['viju history', 'viju history hd', 'history'],
    'TV1000': ['tv1000', 'tv 1000'],
    'TV1000 Русское кино': ['tv1000 русское', 'tv1000 русское кино', 'russian cinema'],
    'TV1000 Action': ['tv1000 action', 'tv1000 action hd'],
    'Кинопремьера': ['кинопремьера', 'kinopremiera'],
    'Киносемья': ['киносемья', 'kinosemya'],
    'Мужское кино': ['мужское кино', 'muzhskoe kino'],
    'Мосфильм. Золотая коллекция': ['мосфильм', 'mosfilm', 'золотая коллекция'],
    
    # ===== РОССИЯ (ВСЕ ВАРИАНТЫ!) =====
    'Россия 1': [
        'россия 1', 'россия-1', 'russia 1', 'russia-1',
        'ртр', 'rtr', 'rtr planeta', 'россия ртр'
    ],
    'Звезда': [
        'звезда', 'zvezda', 'tv zvezda', 'звезда hd',
        'star tv', 'star'
    ],
    'Звезда Плюс': [
        'звезда плюс', 'zvezda plus', 'звезда+', 'star plus'
    ],
    
    # ===== МОЛДОВА (ВСЕ ВАРИАНТЫ!) =====
    'TV7': [
        'tv7', '7tv', 'tv 7', '7 tv',
        'tv7 moldova', '7tv moldova',
        'canal 7', 'canal7', 'tvr 7'
    ],
    'TV9': [
        'tv9', '9tv', 'tv 9', '9 tv',
        'tv9 moldova', '9tv moldova',
        'canal 9', 'canal9', 'tvr 9'
    ],
}

# ============================================
# 2. КАТЕГОРИИ
# ============================================

CATEGORIES = {
    '🎬 ФИЛЬМЫ': list(CHANNELS.keys())[:12],
    '🇷🇺 РОССИЯ': list(CHANNELS.keys())[12:15],
    '🇲🇩 МОЛДОВА': list(CHANNELS.keys())[15:17],
}

# ============================================
# 3. ИСТОЧНИКИ
# ============================================

SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://iptv-org.github.io/iptv/countries/ru.m3u',
    'https://iptv-org.github.io/iptv/countries/md.m3u',
]

# ============================================
# 4. ФУНКЦИИ
# ============================================

def download_m3u(url):
    try:
        r = requests.get(url, timeout=15)
        return r.text if r.status_code == 200 else None
    except:
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
                    key = hashlib.md5(line.lower().encode()).hexdigest()
                    if key not in seen:
                        seen.add(key)
                        channels.append((line, url))
                        i += 1
        i += 1
    return channels

def find_channel(line):
    """Поиск по всем синонимам"""
    line_lower = line.lower()
    
    for channel_name, synonyms in CHANNELS.items():
        for synonym in synonyms:
            if synonym.lower() in line_lower:
                return channel_name
    
    return None

def get_category(channel_name):
    for category, channels in CATEGORIES.items():
        if channel_name in channels:
            return category
    return None

def clean_name(line):
    line = re.sub(r'\([^)]*\)', '', line)
    line = re.sub(r'\[[^\]]*\]', '', line)
    line = re.sub(r'HD|SD|FULL|4K|1080|720', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+', ' ', line)
    return line.strip()

def build_playlist():
    print("\n" + "="*60)
    print("📺 ПОИСК КАНАЛОВ (С РАСШИРЕННЫМИ СИНОНИМАМИ!)")
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
            channel_name = find_channel(line)
            if not channel_name:
                continue
            
            # Исключаем Moldova 1
            if 'moldova 1' in line.lower():
                continue
            
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            category = get_category(channel_name)
            if not category:
                continue
            
            name_match = re.search(r',([^,]+)$', line)
            if name_match:
                name = name_match.group(1).strip()
                clean = clean_name(name)
                line = re.sub(r',[^,]*$', f',{clean}', line)
            
            if channel_name not in found:
                found[channel_name] = []
            found[channel_name].append((line, url, category))
    
    print("\n" + "="*60)
    print(f"📊 НАЙДЕНО: {len(found)} из {len(CHANNELS)}")
    print("="*60)
    
    for channel in CHANNELS.keys():
        if channel in found:
            print(f"   ✅ {channel}")
        else:
            print(f"   ❌ {channel} - НЕ НАЙДЕН")
    
    return found

def save_playlist(found):
    if not found:
        print("\n❌ Каналы не найдены!")
        return False
    
    grouped = {}
    for channel_name, channels in found.items():
        category = get_category(channel_name)
        if category not in grouped:
            grouped[category] = []
        for line, url, _ in channels:
            grouped[category].append(f"{line}\n{url}")
    
    try:
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 📺 ПЛЕЙЛИСТ ДЛЯ LG TV\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего: {sum(len(v) for v in found.values())}\n\n')
            
            priority = ['🎬 ФИЛЬМЫ', '🇷🇺 РОССИЯ', '🇲🇩 МОЛДОВА']
            
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
        print("\n📎 ССЫЛКА ДЛЯ ПЛЕЕРА:")
        print("https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
        print("\n🔄 Обновляется каждые 6 часов")
    else:
        print("\n❌ Каналы не найдены!")

if __name__ == "__main__":
    main()
