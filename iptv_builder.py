#!/usr/bin/env python3
"""
🎯 ПРОСТОЙ ПЛЕЙЛИСТ - ТОЛЬКО РАБОЧИЕ КАНАЛЫ!
"""

import requests
import hashlib
import os
import re
from datetime import datetime

# ============================================
# 1. ВАШИ КАНАЛЫ (ТОЧНЫЕ НАЗВАНИЯ)
# ============================================

YOUR_CHANNELS = [
    # Фильмы
    'Amedia Premium HD',
    'viju+ Premiere',
    'viju+ Megahit',
    'viju+ Serial',
    'viju History',
    'TV1000',
    'TV1000 Русское кино',
    'TV1000 Action',
    'Кинопремьера',
    'Киносемья',
    'Мужское кино',
    'Мосфильм. Золотая коллекция',
    # Россия
    'Россия 1',
    'Звезда',
    'Звезда Плюс',
    # Молдова
    'TV7',
    'TV9',
]

# ============================================
# 2. КАТЕГОРИИ
# ============================================

CATEGORIES = {
    '🎬 ФИЛЬМЫ': YOUR_CHANNELS[:12],
    '🇷🇺 РОССИЯ': YOUR_CHANNELS[12:15],
    '🇲🇩 МОЛДОВА': YOUR_CHANNELS[15:17],
}

# ============================================
# 3. ИСТОЧНИКИ (ПРОВЕРЕННЫЕ)
# ============================================

SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
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
    """Поиск канала по точному совпадению"""
    line_lower = line.lower()
    
    for channel in YOUR_CHANNELS:
        if channel.lower() in line_lower:
            return channel
    
    return None

def get_category(channel_name):
    for category, channels in CATEGORIES.items():
        if channel_name in channels:
            return category
    return None

def clean_name(line):
    """Очистить название"""
    line = re.sub(r'\([^)]*\)', '', line)
    line = re.sub(r'\[[^\]]*\]', '', line)
    line = re.sub(r'HD|SD|FULL|4K|1080|720', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+', ' ', line)
    return line.strip()

def build_playlist():
    print("\n" + "="*60)
    print("🎯 СБОРКА ПРОСТОГО ПЛЕЙЛИСТА")
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
        
        found_count = 0
        for line, url in channels:
            channel_name = find_channel(line)
            if not channel_name:
                continue
            
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            category = get_category(channel_name)
            if not category:
                continue
            
            # Чистое название
            name_match = re.search(r',([^,]+)$', line)
            if name_match:
                name = name_match.group(1).strip()
                clean = clean_name(name)
                line = re.sub(r',[^,]*$', f',{clean}', line)
            
            if channel_name not in found:
                found[channel_name] = []
            found[channel_name].append((line, url, category))
            found_count += 1
        
        if found_count > 0:
            print(f"    ✅ +{found_count} каналов")
    
    print("\n" + "="*60)
    print(f"📊 НАЙДЕНО: {len(found)} из {len(YOUR_CHANNELS)}")
    print("="*60)
    
    # Отчёт
    for channel in YOUR_CHANNELS:
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
            f.write(f'# 🎯 ПРОСТОЙ ПЛЕЙЛИСТ\n')
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
