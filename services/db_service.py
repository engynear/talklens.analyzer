import asyncpg
import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
import psycopg2
from psycopg2.extras import RealDictCursor

class DBService:
    def __init__(self):
        self.pool = None
        self.conn_params = {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
            "user": DB_USER,
            "password": DB_PASS
        }
        self.sync_connection = None
        
        print(f"🛢️ Инициализация DBService с параметрами:")
        print(f"🛢️ - Хост: {DB_HOST}, Порт: {DB_PORT}")
        print(f"🛢️ - База данных: {DB_NAME}, Пользователь: {DB_USER}")
        

    async def get_pool(self):
        """Получает или создает пул соединений"""
        if self.pool is None:
            print(f"🔄 Создание пула соединений к PostgreSQL ({DB_HOST}:{DB_PORT})...")
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    start_time = time.time()
                    self.pool = await asyncpg.create_pool(
                        host=DB_HOST,
                        port=DB_PORT,
                        database=DB_NAME,
                        user=DB_USER,
                        password=DB_PASS,
                        timeout=10.0,
                        min_size=2, 
                        max_size=10
                    )
                    elapsed_time = time.time() - start_time
                    print(f"✅ Пул соединений PostgreSQL создан за {elapsed_time:.2f} сек")
                    break
                except asyncpg.exceptions.PostgresError as e:
                    print(f"❌ Ошибка PostgreSQL при создании пула (попытка {attempt+1}/{max_attempts}): {e}")
                    if attempt < max_attempts - 1:
                        delay = 2 * (attempt + 1)
                        print(f"⏱️ Ждем {delay} секунд перед повторной попыткой...")
                        await asyncio.sleep(delay)
                except Exception as e:
                    print(f"❌ Неожиданная ошибка при создании пула (попытка {attempt+1}/{max_attempts}): {e}")
                    import traceback
                    print(f"Стек ошибки:\n{traceback.format_exc()}")
                    if attempt < max_attempts - 1:
                        delay = 2 * (attempt + 1)
                        print(f"⏱️ Ждем {delay} секунд перед повторной попыткой...")
                        await asyncio.sleep(delay)
            
            if self.pool is None:
                print(f"⚠️ Не удалось создать пул соединений к PostgreSQL после {max_attempts} попыток")
                print(f"⚠️ Проверьте настройки подключения в файле .env или config.py")
        
        return self.pool


    def connect(self):
        """Устанавливает синхронное соединение с БД."""
        if self.sync_connection is None or self.sync_connection.closed:
            try:
                print(f"🔄 Установка синхронного соединения к PostgreSQL ({DB_HOST}:{DB_PORT})...")
                start_time = time.time()
                self.sync_connection = psycopg2.connect(**self.conn_params)
                elapsed_time = time.time() - start_time
                print(f"✅ Синхронное соединение с PostgreSQL установлено за {elapsed_time:.2f} сек")
            except psycopg2.OperationalError as e:
                print(f"❌ Ошибка подключения к PostgreSQL: {e}")
                raise
        return self.sync_connection

    def close(self):
        """Закрывает синхронное соединение с БД."""
        if self.sync_connection and not self.sync_connection.closed:
            print(f"🔄 Закрытие синхронного соединения с PostgreSQL...")
            self.sync_connection.close()
            print(f"✅ Соединение закрыто")


    async def get_historical_summary(self, session_id: str, interlocutor_id: int) -> Optional[str]:
        """
        Асинхронно получает последнее историческое саммери для указанного диалога
        """
        print(f"🔄 Получение исторического саммери для сессии {session_id}, собеседника {interlocutor_id}...")
        try:
            pool = await self.get_pool()
            if pool is None:
                print(f"⚠️ Пул соединений не создан, невозможно получить историческое саммери")
                return None
                
            async with pool.acquire() as conn:
                print(f"🔄 Выполнение запроса к БД для получения саммери...")
                row = await conn.fetchrow("""
                    SELECT summary 
                    FROM historical_summaries 
                    WHERE session_id = $1 AND interlocutor_id = $2
                    ORDER BY ts DESC 
                    LIMIT 1
                """, session_id, interlocutor_id)
                
                if row:
                    summary = row['summary']
                    summary_preview = summary[:100] + "..." if len(summary) > 100 else summary
                    print(f"✅ Получено историческое саммери, длина: {len(summary)} символов")
                    print(f"📝 Начало саммери: {summary_preview}")
                    return summary
                else:
                    print(f"ℹ️ Историческое саммери не найдено для сессии {session_id}, собеседника {interlocutor_id}")
                    return None
        except Exception as e:
            print(f"❌ Ошибка при получении исторического саммери: {e}")
            import traceback
            print(f"Стек ошибки:\n{traceback.format_exc()}")
            return None

    async def save_historical_summary(self, session_id: str, interlocutor_id: int, summary: str) -> bool:
        """
        Асинхронно сохраняет новое историческое саммери для указанного диалога
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO historical_summaries (session_id, interlocutor_id, summary) 
                VALUES ($1, $2, $3)
            """, session_id, interlocutor_id, summary)
            return True

    async def save_chat_metrics(self, 
                             session_id: str, 
                             telegram_user_id: int, 
                             interlocutor_id: int,
                             role: str,
                             compliments_delta: int,
                             total_compliments: int, 
                             engagement_score: float,
                             attachment_type: str,
                             attachment_confidence: float) -> bool:
        """
        Асинхронно сохраняет метрики чата в базу данных
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_metrics_history (
                    session_id, 
                    telegram_user_id, 
                    interlocutor_id, 
                    role,
                    compliments_delta, 
                    total_compliments, 
                    engagement_score,
                    attachment_type,
                    attachment_confidence
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                session_id, 
                telegram_user_id, 
                interlocutor_id, 
                role,
                compliments_delta, 
                total_compliments, 
                engagement_score,
                attachment_type,
                attachment_confidence
            )
            return True

    async def get_latest_metrics(self, session_id: str, interlocutor_id: int, role: str) -> Optional[Dict[str, Any]]:
        """
        Асинхронно получает последние метрики для указанного участника диалога
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    total_compliments, 
                    engagement_score,
                    attachment_type,
                    attachment_confidence
                FROM chat_metrics_history 
                WHERE session_id = $1 AND interlocutor_id = $2 AND role = $3
                ORDER BY ts DESC 
                LIMIT 1
            """, session_id, interlocutor_id, role)
            
            if row:
                return {
                    'total_compliments': row['total_compliments'],
                    'engagement_score': row['engagement_score'],
                    'attachment_type': row['attachment_type'],
                    'attachment_confidence': row['attachment_confidence']
                }
            return None
            

    def get_historical_summary_sync(self, session_id: str, interlocutor_id: int) -> Optional[str]:
        conn = self.connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT summary 
                    FROM historical_summaries 
                    WHERE session_id = %s AND interlocutor_id = %s
                    ORDER BY ts DESC 
                    LIMIT 1
                """, (session_id, interlocutor_id))
                
                result = cur.fetchone()
                return result['summary'] if result else None
        except Exception as e:
            print(f"Ошибка при получении исторического саммери: {e}")
            return None

    def save_historical_summary_sync(self, session_id: str, interlocutor_id: int, summary: str) -> bool:
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO historical_summaries (session_id, interlocutor_id, summary) 
                    VALUES (%s, %s, %s)
                """, (session_id, interlocutor_id, summary))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при сохранении исторического саммери: {e}")
            return False

    def save_chat_metrics_sync(self, 
                             session_id: str, 
                             telegram_user_id: int, 
                             interlocutor_id: int,
                             role: str,
                             compliments_delta: int,
                             total_compliments: int, 
                             engagement_score: float,
                             attachment_type: str,
                             attachment_confidence: float) -> bool:
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_metrics_history (
                        session_id, 
                        telegram_user_id, 
                        interlocutor_id, 
                        role,
                        compliments_delta, 
                        total_compliments, 
                        engagement_score,
                        attachment_type,
                        attachment_confidence
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id, 
                    telegram_user_id, 
                    interlocutor_id, 
                    role,
                    compliments_delta, 
                    total_compliments, 
                    engagement_score,
                    attachment_type,
                    attachment_confidence
                ))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при сохранении метрик чата: {e}")
            return False

    def get_latest_metrics_sync(self, session_id: str, interlocutor_id: int, role: str) -> Optional[Dict[str, Any]]:
        conn = self.connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        total_compliments, 
                        engagement_score,
                        attachment_type,
                        attachment_confidence
                    FROM chat_metrics_history 
                    WHERE session_id = %s AND interlocutor_id = %s AND role = %s
                    ORDER BY ts DESC 
                    LIMIT 1
                """, (session_id, interlocutor_id, role))
                
                return cur.fetchone()
        except Exception as e:
            print(f"Ошибка при получении последних метрик: {e}")
            return None

    async def save_user_recommendation(
        self,
        session_id: str,
        telegram_user_id: int,
        interlocutor_id: int,
        recommendation_text: str
    ) -> bool:
        """
        Сохраняет рекомендацию по общению в БД
        
        Args:
            session_id: ID сессии
            telegram_user_id: ID пользователя телеграм
            interlocutor_id: ID собеседника
            recommendation_text: Текст рекомендации
            
        Returns:
            True в случае успеха, False при ошибке
        """
        try:
            conn = await self.get_pool()
            async with conn.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO telegram_user_recommendations
                    (session_id, telegram_user_id, interlocutor_id, recommendation_text)
                    VALUES ($1, $2, $3, $4)
                    """,
                    session_id, telegram_user_id, interlocutor_id, recommendation_text
                )
            print(f"✅ Рекомендация для пользователя {telegram_user_id} с собеседником {interlocutor_id} сохранена в БД")
            return True
        except Exception as e:
            print(f"❌ Ошибка при сохранении рекомендации в БД: {e}")
            import traceback
            print(f"Стек ошибки рекомендации:\n{traceback.format_exc()}")
            return False


db_service = DBService() 