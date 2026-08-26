#!/usr/bin/env python3
"""
🌍 IPTV BUILDER - Простая версия
"""

import requests
import hashlib
import os
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
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/news.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/sport.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/music.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kids.m3u',
]

def download_m3u(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except:
        pass
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
                        channels.append(f"{line}\n{url}")
                        i += 1
        i += 1
    return channels

def build():
    print("="*50)
    print("🌍 СБОРКА IPTV")
    print("="*50)
    all_channels = []
    for url in SOURCES:
        print(f"📡 {url}")
        content = download_m3u(url)
        if content:
            channels = parse_m3u(content)
            if channels:
                all_channels.extend(channels)
                print(f"  ✅ +{len(channels)}")
            else:
                print(f"  ⚠️ 0")
        else:
            print(f"  ❌ Ошибка")
    print("="*50)
    print(f"✅ ВСЕГО: {len(all_channels)}")
    return all_channels

def save(channels):
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        f.write(f'# Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M")}\n')
        f.write(f'# Каналов: {len(channels)}\n\n')
        for ch in channels:
            f.write(f'{ch}\n')
    print(f"💾 Сохранено: playlist.m3u")
    print(f"📊 Каналов: {len(channels)}")

if __name__ == "__main__":
    channels = build()
    if channels:
        save(channels)
        print("\n" + "="*50)
        print("🎉 ГОТОВО!")
        print("="*50)
        print("\n📎 ССЫЛКА:")
        print("https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
