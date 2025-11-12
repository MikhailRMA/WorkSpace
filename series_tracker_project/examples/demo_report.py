#!/usr/bin/env python3
"""
Демо-версия отчета для GitHub
"""

import os
import sys
from datetime import datetime

def create_monthly_report_html(stats):
    """Полная функция создания HTML отчета"""
    
    # Берем данные из stats
    total_series = stats.get('total_series', 0)
    avg_rating_kino = stats.get('avg_rating_kino')
    avg_rating_imdb = stats.get('avg_rating_imdb')
    countries_count = stats.get('countries_count', 0)
    top_genres = stats.get('top_genres', {})
    all_series = stats.get('all_series', [])
    current_year = stats.get('current_year', datetime.now().year)
    current_month = stats.get('current_month', datetime.now().month)
    
    # Форматируем рейтинги для отображения
    rating_kino_display = f"{avg_rating_kino:.1f}" if avg_rating_kino else "Н/Д"
    rating_imdb_display = f"{avg_rating_imdb:.1f}" if avg_rating_imdb else "Н/Д"
    
    # ТОП ЖАНРОВ
    genres_html = ""
    for genre, count in list(top_genres.items())[:5]:
        genres_html += f"<li>{genre}: {count} сериалов</li>"
    
    # ПОЛНЫЙ СПИСОК СЕРИАЛОВ
    series_html = ""
    
    if all_series:
        for i, series in enumerate(all_series, 1):
            title = series.get('title', 'N/A')
            rating_kino = series.get('rating_kino', 0)
            rating_imdb = series.get('rating_imdb', 0)
            country = series.get('country', 'N/A')
            genres = series.get('genres', 'Неизвестно')
            
            # Форматируем жанры
            if isinstance(genres, list):
                genres_display = ', '.join(genres)
            else:
                genres_display = str(genres)
            
            # Определяем цвет рейтинга
            if rating_kino > 0:
                rating_kino_color = "#e74c3c" if rating_kino >= 7 else "#f39c12" if rating_kino >= 5 else "#95a5a6"
                rating_kino_display_item = f"{rating_kino:.1f}"
            else:
                rating_kino_color = "#95a5a6"
                rating_kino_display_item = "Н/Д"
            
            if rating_imdb > 0:
                rating_imdb_color = "#e74c3c" if rating_imdb >= 7 else "#f39c12" if rating_imdb >= 5 else "#95a5a6"
                rating_imdb_display_item = f"{rating_imdb:.1f}"
            else:
                rating_imdb_color = "#95a5a6"
                rating_imdb_display_item = "Н/Д"
            
            series_html += f"""
            <tr>
                <td>{i}</td>
                <td><strong>{title}</strong></td>
                <td style="color: {rating_kino_color}; font-weight: bold;">{rating_kino_display_item}</td>
                <td style="color: {rating_imdb_color}; font-weight: bold;">{rating_imdb_display_item}</td>
                <td>{country}</td>
                <td>{genres_display}</td>
            </tr>
            """
    else:
        series_html = '<tr><td colspan="6" style="text-align: center; padding: 30px; color: #666;">Нет данных о сериалах</td></tr>'
    
    # HTML шаблон для ежемесячного отчета
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
            .stat-value {{ font-size: 1.5em; font-weight: bold; color: #2c3e50; margin: 5px 0; }}
            .table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            .table th, .table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            .table th {{ background: #34495e; color: white; }}
            .scrollable-table {{ max-height: 800px; overflow-y: auto; border: 1px solid #ddd; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎬 Отчет по сериалам за {current_year}-{current_month:02d}</h1>
                <p>Сгенерирован {datetime.now().strftime('%d.%m.%Y в %H:%M')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📊 Всего сериалов</h3>
                    <div class="stat-value">{total_series}</div>
                </div>
                <div class="stat-card">
                    <h3>⭐ KinoMail</h3>
                    <div class="stat-value">{rating_kino_display}</div>
                </div>
                <div class="stat-card">
                    <h3>🎯 IMDb</h3>
                    <div class="stat-value">{rating_imdb_display}</div>
                </div>
                <div class="stat-card">
                    <h3>🌍 Стран</h3>
                    <div class="stat-value">{countries_count}</div>
                </div>
            </div>
            
            <h2>🎭 Популярные жанры</h2>
            <ul>
                {genres_html if genres_html else '<li>Нет данных о жанрах</li>'}
            </ul>
            
            <h2>📺 Все сериалы ({total_series} шт)</h2>
            <p><em>Отсортировано по рейтингу KinoMail</em></p>
            <div class="scrollable-table">
                <table class="table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Название</th>
                            <th>KinoMail</th>
                            <th>IMDb</th>
                            <th>Страна</th>
                            <th>Жанры</th>
                        </tr>
                    </thead>
                    <tbody>
                        {series_html}
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center;">
                <p><em>🍿 Что посмотреть в этом месяце? Используйте этот список для выбора сериалов!</em></p>
                <p><small>Рейтинг окрашен: <span style="color: #e74c3c;">высокий (≥7)</span> • <span style="color: #f39c12;">средний (5-7)</span> • <span style="color: #95a5a6;">низкий (<5)</span></small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template

def create_demo_report():
    """Создание демо-отчета с примером данных"""
    
    # Пример данных
    demo_stats = {
        'total_series': 127,
        'avg_rating_kino': 7.2,
        'avg_rating_imdb': 7.5,
        'countries_count': 15,
        'current_year': 2024,
        'current_month': 11,
        'top_genres': {
            'Драма': 45,
            'Комедия': 32,
            'Триллер': 28,
            'Фантастика': 15,
            'Детектив': 7
        },
        'all_series': [
            {
                'title': 'Очень странные дела',
                'rating_kino': 8.9,
                'rating_imdb': 8.7,
                'country': 'США',
                'genres': ['Фантастика', 'Драма', 'Ужасы']
            },
            {
                'title': 'Во все тяжкие',
                'rating_kino': 8.8,
                'rating_imdb': 9.5,
                'country': 'США', 
                'genres': ['Драма', 'Криминал', 'Триллер']
            },
            {
                'title': 'Корона',
                'rating_kino': 8.2,
                'rating_imdb': 8.6,
                'country': 'Великобритания',
                'genres': ['Драма', 'История']
            },
            {
                'title': 'Игра в кальмара',
                'rating_kino': 7.9,
                'rating_imdb': 8.0,
                'country': 'Корея',
                'genres': ['Триллер', 'Драма']
            },
            {
                'title': 'Друзья',
                'rating_kino': 8.5, 
                'rating_imdb': 8.9,
                'country': 'США',
                'genres': ['Комедия', 'Романтика']
            },
            {
                'title': 'Черное зеркало',
                'rating_kino': 8.4,
                'rating_imdb': 8.7,
                'country': 'Великобритания',
                'genres': ['Фантастика', 'Драма', 'Триллер']
            },
            {
                'title': 'Наследники',
                'rating_kino': 8.1,
                'rating_imdb': 8.8,
                'country': 'США',
                'genres': ['Драма']
            },
            {
                'title': 'Бумажный дом',
                'rating_kino': 7.8,
                'rating_imdb': 8.2,
                'country': 'Испания',
                'genres': ['Криминал', 'Драма', 'Триллер']
            },
            {
                'title': 'Клиника',
                'rating_kino': 8.3,
                'rating_imdb': 8.4,
                'country': 'США',
                'genres': ['Комедия', 'Драма']
            },
            {
                'title': 'Темный рыцарь',
                'rating_kino': 9.0,
                'rating_imdb': 9.0,
                'country': 'США',
                'genres': ['Боевик', 'Криминал', 'Драма']
            }
        ],
        'report_type': 'monthly'
    }
    
    # Создаем HTML
    html_content = create_monthly_report_html(demo_stats)
    
    # Определяем абсолютный путь для сохранения
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'demo_report.html')
    
    # Сохраняем в файл
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Демо-отчет создан: {output_path}")
    print("📊 Пример статистики:")
    print(f"   - Сериалов: {demo_stats['total_series']}")
    print(f"   - Рейтинг KinoMail: {demo_stats['avg_rating_kino']}")
    print(f"   - Рейтинг IMDb: {demo_stats['avg_rating_imdb']}")
    print(f"   - Стран: {demo_stats['countries_count']}")
    print(f"   - Топ жанров: {', '.join(list(demo_stats['top_genres'].keys())[:3])}")
    
    # Показываем где искать файл
    print(f"\n📁 Файл сохранен в: {output_path}")
    print("🌐 Откройте его в браузере для просмотра")

if __name__ == "__main__":
    create_demo_report()