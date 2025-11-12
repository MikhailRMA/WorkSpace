import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from datetime import datetime
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def get_db_connection():
    """Создание подключения к PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'series_tracker'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
        raise

def init_database():
    """Инициализация базы данных PostgreSQL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Создание таблицы сериалов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT,
                country TEXT,
                year INTEGER,
                release_date DATE,
                season INTEGER,
                rating_kino_mail REAL DEFAULT 0,
                rating_imdb REAL DEFAULT 0,
                genre TEXT,
                duration TEXT,
                age_limit TEXT,
                parsed_at TIMESTAMP,
                target_month TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, release_date, target_month)  -- Защита от дубликатов
            )
        ''')
        
        # Создание индексов для ускорения запросов
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_series_target_month 
            ON series(target_month)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_series_release_date 
            ON series(release_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_series_year 
            ON series(year)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_series_rating_kino 
            ON series(rating_kino_mail DESC)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_series_created_at 
            ON series(created_at DESC)
        ''')
        
        conn.commit()
        print("✅ База данных PostgreSQL инициализирована успешно")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def save_to_database(series_data):
    """Сохранение данных в PostgreSQL"""
    if not series_data:
        print("❌ Нет данных для сохранения")
        return False
    
    init_database()  # Убедимся, что база создана
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Подготовка данных для вставки
        columns = [
            'title', 'link', 'country', 'year', 'release_date', 
            'season', 'rating_kino_mail', 'rating_imdb', 'genre', 
            'duration', 'age_limit', 'parsed_at', 'target_month'
        ]
        
        # Преобразование данных
        values = []
        for series in series_data:
            row = [
                series.get('title'),
                series.get('link', ''),
                series.get('country', 'Неизвестно'),
                int(series.get('year', 2025)) if str(series.get('year', '2025')).isdigit() else 2025,
                series.get('release_date'),
                int(series.get('season', 1)) if str(series.get('season', '1')).isdigit() else 1,
                float(series.get('rating_kino_mail', 0)),
                float(series.get('rating_imdb', 0)),
                series.get('genre', 'Неизвестно'),
                series.get('duration', 'Неизвестно'),
                series.get('age_limit', 'Неизвестно'),
                series.get('parsed_at'),
                series.get('target_month')
            ]
            values.append(row)
        
        # Вставка данных с обработкой конфликтов (ON CONFLICT DO NOTHING)
        insert_query = '''
            INSERT INTO series 
            (title, link, country, year, release_date, season, rating_kino_mail, 
             rating_imdb, genre, duration, age_limit, parsed_at, target_month)
            VALUES %s
            ON CONFLICT (title, release_date, target_month) DO NOTHING
        '''
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"✅ Успешно сохранено {len(series_data)} сериалов в PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения в PostgreSQL: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_series_stats(year, month):
    """Получение статистики по сериалам за конкретный месяц"""
    try:
        conn = get_db_connection()
        
        # Получаем все сериалы за указанный месяц для PostgreSQL
        query = """
        SELECT title, rating_kino_mail, rating_imdb, country, genre, release_date 
        FROM series 
        WHERE TO_CHAR(release_date, 'YYYY-MM') = %s OR target_month = %s
        ORDER BY 
            CASE WHEN rating_kino_mail > 0 THEN rating_kino_mail ELSE 0 END DESC,
            CASE WHEN rating_imdb > 0 THEN rating_imdb ELSE 0 END DESC
        """
        df = pd.read_sql_query(query, conn, params=[f"{year}-{month:02d}", f"{year}-{month:02d}"])
        conn.close()
        
        if df.empty:
            print(f"❌ Нет данных за {year}-{month:02d}")
            return {}
        
        print(f"📊 Найдено {len(df)} сериалов за {year}-{month:02d}")
        
        # Переименуем колонки для удобства
        df = df.rename(columns={
            'rating_kino_mail': 'rating_kino',
            'genre': 'genres'
        })
        
        # Считаем средние рейтинги ИГНОРИРЯ нулевые значения
        kino_ratings = df[df['rating_kino'] > 0]['rating_kino']
        imdb_ratings = df[df['rating_imdb'] > 0]['rating_imdb']
        
        avg_rating_kino = kino_ratings.mean() if not kino_ratings.empty else None
        avg_rating_imdb = imdb_ratings.mean() if not imdb_ratings.empty else None
        
        print(f"⭐ Средние рейтинги: KinoMail={avg_rating_kino}, IMDb={avg_rating_imdb}")
        
        # Количество уникальных стран
        countries_count = df['country'].nunique()
        
        # Топ жанров
        all_genres = []
        for genres_str in df['genres'].dropna():
            if genres_str and genres_str != 'Неизвестно':
                genres = [genre.strip() for genre in genres_str.split(',')]
                all_genres.extend(genres)
        
        from collections import Counter
        top_genres = dict(Counter(all_genres).most_common(10))
        
        # Полный список сериалов (отсортированный по рейтингу)
        all_series = []
        for _, row in df.iterrows():
            series_data = {
                'title': row['title'],
                'rating_kino': float(row['rating_kino']) if row['rating_kino'] else 0,
                'rating_imdb': float(row['rating_imdb']) if row['rating_imdb'] else 0,
                'country': row['country'],
                'genres': row['genres'],
                'release_date': row['release_date']
            }
            all_series.append(series_data)
        
        result = {
            'total_series': len(df),
            'avg_rating_kino': round(avg_rating_kino, 2) if avg_rating_kino else None,
            'avg_rating_imdb': round(avg_rating_imdb, 2) if avg_rating_imdb else None,
            'countries_count': countries_count,
            'top_genres': top_genres,
            'all_series': all_series,
            'year': year,
            'month': month
        }
        
        print(f"✅ Статистика сформирована: {len(all_series)} сериалов")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        import traceback
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")
        return {}
   
def get_top_rated_series(conn, year=None, month=None, limit=5):
    """Получение топовых сериалов по рейтингу"""
    try:
        if year and month:
            target_month = f"{year}-{month:02d}"
            query = """
                SELECT title, rating_kino_mail, rating_imdb, release_date 
                FROM series 
                WHERE target_month = %s AND rating_kino_mail > 0
                ORDER BY rating_kino_mail DESC 
                LIMIT %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (target_month, limit))
        else:
            query = """
                SELECT title, rating_kino_mail, rating_imdb, release_date 
                FROM series 
                WHERE rating_kino_mail > 0
                ORDER BY rating_kino_mail DESC 
                LIMIT %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                'title': row[0],
                'rating_kino': row[1],
                'rating_imdb': row[2],
                'release_date': row[3]
            }
            for row in results
        ]
    except Exception as e:
        print(f"❌ Ошибка получения топовых сериалов: {e}")
        return []

def get_monthly_trend(conn):
    """Получение трендов по месяцам"""
    try:
        query = """
            SELECT 
                target_month,
                COUNT(*) as series_count,
                ROUND(AVG(rating_kino_mail), 2) as avg_rating
            FROM series 
            WHERE target_month IS NOT NULL
            GROUP BY target_month
            ORDER BY target_month DESC
            LIMIT 6
        """
        df = pd.read_sql_query(query, conn)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ Ошибка получения трендов: {e}")
        return []

def check_duplicate_series(title, release_date, target_month):
    """Проверка на дубликаты сериалов"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT COUNT(*) FROM series 
            WHERE title = %s AND release_date = %s AND target_month = %s
        ''', (title, release_date, target_month))
        
        count = cursor.fetchone()[0]
        return count > 0
        
    except Exception as e:
        print(f"❌ Ошибка проверки дубликатов: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def cleanup_old_data(months_to_keep=12):
    """Очистка старых данных (оставляет данные за указанное количество месяцев)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            DELETE FROM series 
            WHERE created_at < CURRENT_DATE - INTERVAL '%s months'
        ''', (months_to_keep,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Удалено {deleted_count} записей старше {months_to_keep} месяцев")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Ошибка очистки данных: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()