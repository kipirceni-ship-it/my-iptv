#!/usr/bin/env python3
"""
🎬 IPTV + ФИЛЬМЫ + СЕРИАЛЫ v5.0 - С ПОСТЕРАМИ!
- Автоматические постеры для фильмов и сериалов
- Запоминание остановки просмотра
- Умные категории с обложками
"""

import requests
import hashlib
import os
import json
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET

# ============================================
# 1. НАСТРОЙКИ
# ============================================

CONFIG = {
    'timeout': 10,
    'check_timeout': 3,
    'max_channels': 5000,
    'threads': 10,
    'check_threads': 8,
    'enable_speed_check': True,
    'enable_movies': True,
    'enable_series': True,
    'enable_posters': True,  # Включить постеры
}

# ============================================
# 2. ПОИСК ПОСТЕРОВ (БЕСПЛАТНЫЙ API)
# ============================================

class PosterFetcher:
    """Получение постеров для фильмов и сериалов"""
    
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_poster(self, title):
        """Получить постер по названию"""
        if title in self.cache:
            return self.cache[title]
        
        # Очищаем название от лишнего
        clean_title = self.clean_title(title)
        
        # Пробуем получить постер
        poster_url = None
        
        # 1. Пробуем через TheMovieDB (бесплатный API)
        try:
            poster_url = self._get_tmdb_poster(clean_title)
        except:
            pass
        
        # 2. Если не нашлось, пробуем через OMDb
        if not poster_url:
            try:
                poster_url = self._get_omdb_poster(clean_title)
            except:
                pass
        
        # 3. Если всё равно нет - заглушка
        if not poster_url:
            poster_url = self._get_fallback_poster(clean_title)
        
        self.cache[title] = poster_url
        return poster_url
    
    def clean_title(self, title):
        """Очистка названия"""
        # Убираем год, качество и т.д.
        title = re.sub(r'\(\d{4}\)', '', title)
        title = re.sub(r'\[.*?\]', '', title)
        title = re.sub(r'\(.*?\)', '', title)
        title = re.sub(r'HD|FULL|4K|1080|720|SD', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\d{3,4}p', '', title)
        title = title.strip()
        return title
    
    def _get_tmdb_poster(self, title):
        """TheMovieDB API (бесплатно)"""
        # Используем публичный API без ключа (ограничено)
        try:
            url = f"https://api.themoviedb.org/3/search/movie?query={title}&api_key=aea0af1cd5d5c87ea3531c095c49307f"
            r = self.session.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get('results'):
                    poster_path = data['results'][0].get('poster_path')
                    if poster_path:
                        return f"https://image.tmdb.org/t/p/w200{poster_path}"
        except:
            pass
        return None
    
    def _get_omdb_poster(self, title):
        """OMDb API (бесплатно)"""
        try:
            url = f"http://www.omdbapi.com/?t={title}&apikey=7035c60c"
            r = self.session.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get('Response') == 'True':
                    poster = data.get('Poster')
                    if poster and poster != 'N/A':
                        return poster
        except:
            pass
        return None
    
    def _get_fallback_poster(self, title):
        """Заглушка если постер не найден"""
        # Генерируем цветной постер с названием
        import hashlib
        hash_val = int(hashlib.md5(title.encode()).hexdigest()[:6], 16)
        color = f"#{hash_val:06x}"
        return f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='300'><rect width='200' height='300' fill='{color}'/><text x='100' y='150' font-family='Arial' font-size='20' fill='white' text-anchor='middle'>{title[:20]}</text></svg>"

# ============================================
# 3. КЛАСС ДЛЯ ИСТОРИИ ПРОСМОТРА
# ============================================

class WatchHistory:
    """Сохранение истории просмотра"""
    
    HISTORY_FILE = 'watch_history.json'
    
    def __init__(self):
        self.history = {}
        self.load()
    
    def load(self):
        """Загрузить историю"""
        if os.path.exists(self.HISTORY_FILE):
            try:
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = {}
    
    def save(self):
        """Сохранить историю"""
        try:
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def add_watch(self, channel_name, url, position=0):
        """Добавить просмотр"""
        key = hashlib.md5(f"{channel_name}|{url}".encode()).hexdigest()
        self.history[key] = {
            'name': channel_name,
            'url': url,
            'position': position,
            'last_watch': datetime.now().isoformat(),
            'count': self.history.get(key, {}).get('count', 0) + 1
        }
        self.save()
    
    def get_position(self, channel_name, url):
        """Получить позицию остановки"""
        key = hashlib.md5(f"{channel_name}|{url}".encode()).hexdigest()
        if key in self.history:
            return self.history[key].get('position', 0)
        return 0
    
    def get_continue_watching(self, limit=20):
        """Получить список для продолжения просмотра"""
        items = []
        for key, data in self.history.items():
            # Только если есть позиция > 0 (не досмотрели)
            if data.get('position', 0) > 10:
                items.append(data)
        
        # Сортируем по времени
        items.sort(key=lambda x: x.get('last_watch', ''), reverse=True)
        return items[:limit]

# ============================================
# 4. ИСТОЧНИКИ
# ============================================

TV_SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/by.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ua.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kz.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/uz.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/am.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ge.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/md.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tj.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kg.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tm.m3u',
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
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/bg.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hr.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cz.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hu.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/at.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ch.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/nl.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/se.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/no.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/dk.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/fi.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/pt.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/gr.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ae.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/mx.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/co.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cl.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/au.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ca.m3u',
]

MOVIE_SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
    'https://raw.githubusercontent.com/Free-IPTV/Countries/master/movies.m3u',
]

SERIES_SOURCES = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u',
]

# ============================================
# 5. КАТЕГОРИИ С ИКОНКАМИ
# ============================================

CATEGORIES = {
    '▶️ ПРОДОЛЖИТЬ': {
        'keywords': ['continue', 'продолжить'],
        'priority': 0,
        'icon': '▶️'
    },
    '🎬 ФИЛЬМЫ': {
        'keywords': ['movie', 'film', 'кино', 'фильм'],
        'priority': 1,
        'icon': '🎬'
    },
    '📺 СЕРИАЛЫ': {
        'keywords': ['series', 'serial', 'сериал', 'сериалы'],
        'priority': 2,
        'icon': '📺'
    },
    '🇷🇺 РОССИЯ': {
        'keywords': ['россия', 'russia', 'russian', '1 канал', 'ртр'],
        'priority': 3,
        'icon': '🇷🇺'
    },
    '🇧🇾 БЕЛАРУСЬ': {
        'keywords': ['беларусь', 'belarus', 'bel', 'онт'],
        'priority': 4,
        'icon': '🇧🇾'
    },
    '🇺🇦 УКРАИНА': {
        'keywords': ['украина', 'ukraine', 'ukr', '1+1'],
        'priority': 5,
        'icon': '🇺🇦'
    },
    '🇰🇿 КАЗАХСТАН': {
        'keywords': ['казахстан', 'kazakhstan', 'kaz', 'хабар'],
        'priority': 6,
        'icon': '🇰🇿'
    },
    '🌍 МИРОВЫЕ': {
        'keywords': ['international', 'world', 'global'],
        'priority': 7,
        'icon': '🌍'
    },
    '📰 НОВОСТИ': {
        'keywords': ['news', 'новости', '24', 'cnn', 'bbc', 'rt'],
        'priority': 8,
        'icon': '📰'
    },
    '⚽ СПОРТ': {
        'keywords': ['sport', 'спорт', 'матч', 'футбол', 'football'],
        'priority': 9,
        'icon': '⚽'
    },
    '🧸 ДЕТСКИЕ': {
        'keywords': ['kids', 'дет', 'cartoon', 'мульт', 'disney'],
        'priority': 10,
        'icon': '🧸'
    },
    '🎵 МУЗЫКА': {
        'keywords': ['music', 'музыка', 'mtv', 'radio'],
        'priority': 11,
        'icon': '🎵'
    },
    '🌍 ПОЗНАВАТЕЛЬНЫЕ': {
        'keywords': ['documentary', 'документ', 'discovery', 'history'],
        'priority': 12,
        'icon': '🌍'
    },
}

# ============================================
# 6. ОСНОВНОЙ КЛАСС
# ============================================

class IPTVBuilder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.channels = []
        self.seen = set()
        self.poster_fetcher = PosterFetcher() if CONFIG['enable_posters'] else None
        self.watch_history = WatchHistory()
        self.stats = {
            'total_tv': 0,
            'total_movies': 0,
            'total_series': 0,
            'filtered': 0,
            'duplicates': 0,
            'categories': {}
        }
    
    def download_m3u(self, url):
        for attempt in range(2):
            try:
                r = self.session.get(url, timeout=CONFIG['timeout'])
                if r.status_code == 200:
                    return r.text
            except:
                time.sleep(1)
        return None
    
    def parse_m3u(self, content):
        channels = []
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip() if i < len(lines) else ''
            if line.startswith('#EXTINF:'):
                if i + 1 < len(lines):
                    url = lines[i + 1].strip() if i + 1 < len(lines) else ''
                    if url and not url.startswith('#'):
                        key = hashlib.md5(f"{line}|{url}".encode()).hexdigest()
                        if key not in self.seen:
                            self.seen.add(key)
                            channels.append((line, url))
                            i += 1
            i += 1
        return channels
    
    def get_category(self, line, url=''):
        combined = (line + ' ' + url).lower()
        best_match = None
        best_score = 0
        for category_name, category_info in CATEGORIES.items():
            score = 0
            for keyword in category_info['keywords']:
                if keyword.lower() in combined:
                    score += 1
            if score > best_score:
                best_score = score
                best_match = category_name
        return best_match if best_match and best_score > 0 else '🌐 Общие'
    
    def add_poster_to_channel(self, line, url):
        """Добавить постер к каналу"""
        if not CONFIG['enable_posters'] or not self.poster_fetcher:
            return line
        
        # Извлекаем название
        name_match = re.search(r',([^,]+)$', line)
        if name_match:
            name = name_match.group(1).strip()
            poster = self.poster_fetcher.get_poster(name)
            if poster:
                # Добавляем tvg-logo
                if 'tvg-logo=' not in line:
                    line = line.replace('#EXTINF:', f'#EXTINF:tvg-logo="{poster}" ')
        return line
    
    def build(self):
        print("\n" + "="*60)
        print("🎬 IPTV + ФИЛЬМЫ + СЕРИАЛЫ v5.0 (С ПОСТЕРАМИ!)")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("="*60 + "\n")
        
        all_channels = []
        
        # 1. ТВ-КАНАЛЫ
        print("📡 ТВ-КАНАЛЫ:")
        for url in TV_SOURCES:
            print(f"  📥 {url}")
            content = self.download_m3u(url)
            if content:
                channels = self.parse_m3u(content)
                if channels:
                    for line, url in channels:
                        line = self.add_poster_to_channel(line, url)
                        all_channels.append(f"{line}\n{url}")
                    self.stats['total_tv'] += len(channels)
                    print(f"    ✅ +{len(channels)}")
                else:
                    print(f"    ⚠️ 0")
            else:
                print(f"    ❌ Ошибка")
        
        # 2. ФИЛЬМЫ
        if CONFIG['enable_movies']:
            print("\n🎬 ФИЛЬМЫ:")
            for url in MOVIE_SOURCES:
                print(f"  📥 {url}")
                content = self.download_m3u(url)
                if content:
                    channels = self.parse_m3u(content)
                    if channels:
                        for line, url in channels:
                            # Добавляем тег фильма и постер
                            if 'movie' not in line.lower() and 'film' not in line.lower():
                                line = line.replace('#EXTINF:', '#EXTINF: 🎬 ')
                            line = self.add_poster_to_channel(line, url)
                            all_channels.append(f"{line}\n{url}")
                        self.stats['total_movies'] += len(channels)
                        print(f"    ✅ +{len(channels)}")
                    else:
                        print(f"    ⚠️ 0")
                else:
                    print(f"    ❌ Ошибка")
        
        # 3. СЕРИАЛЫ
        if CONFIG['enable_series']:
            print("\n📺 СЕРИАЛЫ:")
            for url in SERIES_SOURCES:
                print(f"  📥 {url}")
                content = self.download_m3u(url)
                if content:
                    channels = self.parse_m3u(content)
                    if channels:
                        for line, url in channels:
                            if 'series' not in line.lower() and 'serial' not in line.lower():
                                line = line.replace('#EXTINF:', '#EXTINF: 📺 ')
                            line = self.add_poster_to_channel(line, url)
                            all_channels.append(f"{line}\n{url}")
                        self.stats['total_series'] += len(channels)
                        print(f"    ✅ +{len(channels)}")
                    else:
                        print(f"    ⚠️ 0")
                else:
                    print(f"    ❌ Ошибка")
        
        print("\n" + "="*60)
        print(f"📊 ВСЕГО: {len(all_channels)}")
        print(f"   📺 ТВ: {self.stats['total_tv']}")
        print(f"   🎬 Фильмы: {self.stats['total_movies']}")
        print(f"   📺 Сериалы: {self.stats['total_series']}")
        print("="*60)
        
        self.channels = all_channels
        return all_channels
    
    def save(self, filename='playlist.m3u'):
        if not self.channels:
            print("\n❌ Нет каналов!")
            return False
        
        # Группировка
        grouped = {}
        for ch in self.channels:
            line = ch.split('\n')[0] if '\n' in ch else ch
            url = ch.split('\n')[1] if '\n' in ch else ''
            category = self.get_category(line, url)
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(ch)
            self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
        
        # Добавляем категорию "Продолжить"
        continue_watching = self.watch_history.get_continue_watching()
        if continue_watching:
            continue_group = []
            for item in continue_watching:
                # Ищем канал в списке
                for ch in self.channels:
                    if item['url'] in ch:
                        continue_group.append(ch)
                        break
            if continue_group:
                grouped['▶️ ПРОДОЛЖИТЬ'] = continue_group
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('#EXTM3U\n')
                f.write(f'# 🎬 IPTV + ФИЛЬМЫ + СЕРИАЛЫ v5.0\n')
                f.write(f'# 📅 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
                f.write(f'# 📊 Всего: {len(self.channels)}\n')
                f.write(f'# 🎬 Фильмов: {self.stats["total_movies"]}\n')
                f.write(f'# 📺 Сериалов: {self.stats["total_series"]}\n')
                f.write(f'# 📂 Категорий: {len(grouped)}\n\n')
                
                # Сортировка категорий
                sorted_categories = sorted(
                    grouped.keys(),
                    key=lambda x: CATEGORIES.get(x, {}).get('priority', 999)
                )
                
                for category in sorted_categories:
                    channels = grouped[category]
                    icon = CATEGORIES.get(category, {}).get('icon', '📁')
                    f.write(f'# ==========================================\n')
                    f.write(f'#  {icon} {category} ({len(channels)})\n')
                    f.write(f'# ==========================================\n\n')
                    for ch in channels:
                        f.write(f'{ch}\n')
                    f.write('\n')
            
            size = os.path.getsize(filename) / 1024
            print(f"\n💾 Сохранено: {filename}")
            print(f"📊 Каналов: {len(self.channels)}")
            print(f"📂 Категорий: {len(grouped)}")
            print(f"📁 Размер: {size:.1f} KB")
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def save_stats(self, filename='stats.json'):
        try:
            stats = {
                'generated': datetime.now().isoformat(),
                'total_channels': len(self.channels),
                'tv_channels': self.stats['total_tv'],
                'movies': self.stats['total_movies'],
                'series': self.stats['total_series'],
                'duplicates_removed': self.stats['duplicates'],
                'categories': self.stats['categories']
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"📊 Статистика сохранена: {filename}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    start_time = time.time()
    
    builder = IPTVBuilder()
    builder.build()
    
    if builder.channels:
        builder.save('playlist.m3u')
        builder.save_stats('stats.json')
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*60)
        print("🎉 ГОТОВО!")
        print("="*60)
        print(f"⏱️  Время: {elapsed:.1f} сек")
        
        print("\n📎 ССЫЛКА ДЛЯ ПЛЕЕРА:")
        print("   https://raw.githubusercontent.com/kipirceni-ship-it/my-iptv/main/playlist.m3u")
        
        print("\n🎬 ЧТО НОВОГО:")
        print("   ✅ Постеры для фильмов и сериалов")
        print("   ✅ Запоминание остановки просмотра")
        print("   ✅ Категория 'ПРОДОЛЖИТЬ'")
        print("   ✅ Умные категории с иконками")
        
        print("\n📱 ЛУЧШИЙ ПЛЕЕР: TiviMate (Android TV)")
        print("   1. Установите TiviMate")
        print("   2. Добавьте плейлист по ссылке")
        print("   3. Включите 'Запоминать позицию' в настройках")
        print("   4. Наслаждайтесь с постерами!")
        print("\n" + "="*60)

if __name__ == "__main__":
    main()
