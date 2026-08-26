#!/usr/bin/env python3
"""
🌍 IPTV BUILDER - Простая версия
"""

import requests
import re
import os
import json
import time
import hashlib
from datetime import datetime

# Источники каналов
SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/by.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ua.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kz.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/gb.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/de.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/fr.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/es.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/it.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/in.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/pl.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ro.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ae.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/mx.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/news.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/sport.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/music.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kids.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/documentary.m3u',
]

def download_m3u(url):
    """Скачать файл"""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return None

def parse_m3u(content):
    """Разобрать M3U файл"""
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
                        channels.append(f"{line}\n{url}")
                        i += 1
        i += 1
    return channels

def build_playlist():
    """Собрать плейлист"""
    print("\n" + "="*60)
    print("🌍 СБОРКА IPTV ПЛЕЙЛИСТА")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    all_channels = []
    total_sources = len(SOURCES)
    
    for i, url in enumerate(SOURCES, 1):
        print(f"[{i}/{total_sources}] 📡 {url}")
        content = download_m3u(url)
        if content:
            channels = parse_m3u(content)
            if channels:
                all_channels.extend(channels)
                print(f"    ✅ +{len(channels)} каналов")
            else:
                print(f"    ⚠️ 0 каналов")
        else:
            print(f"    ❌ Ошибка загрузки")
    
    print("\n" + "="*60)
    print(f"✅ ВСЕГО КАНАЛОВ: {len(all_channels)}")
    print("="*60)
    
    return all_channels

def save_playlist(channels, filename='playlist.m3u'):
    """Сохранить плейлист"""
    if not channels:
        print("\n❌ Нет каналов!")
        return False
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# 🌍 IPTV Плейлист\n')
            f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
            f.write(f'# 📊 Всего каналов: {len(channels)}\n\n')
            for ch in channels:
                f.write(f'{ch}\n')
        
        size = os.path.getsize(filename) / 1024
        print(f"\n💾 Сохранено: {filename}")
        print(f"📊 Каналов: {len(channels)}")
        print(f"📁 Размер: {size:.1f} KB")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Главная функция"""
    channels = build_playlist()
    if channels:
        save_playlist(channels)
        print("\n" + "="*60)
        print("🎉 ГОТОВО!")
        print("="*60)
        print("\n📎 ССЫЛКА ДЛЯ ПЛЕЕРА:")
        print("   https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
        print("\n📱 КАК ИСПОЛЬЗОВАТЬ:")
        print("   1. Скопируйте ссылку")
        print("   2. Вставьте в любой IPTV плеер")
        print("   3. Смотрите ТВ! 📺")
        print("\n" + "="*60)
    else:
        print("\n❌ Плейлист не создан!")

if __name__ == "__main__":
    main()
