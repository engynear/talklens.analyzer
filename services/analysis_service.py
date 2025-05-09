import asyncio
from typing import Dict, Any, List, Optional, Tuple
from processor import llm_handler
from services.db_service import db_service
import concurrent.futures
import math
import time


MAX_CHUNK_SIZE = 30

class AnalysisService:
    def __init__(self):
        self.metrics_cache = {}
    
    async def process_batch(self, session_id: str, telegram_user_id: int, interlocutor_id: int, messages: List[Dict[str, Any]]):
        """
        Асинхронно обрабатывает новый батч сообщений, выполняя все необходимые задачи анализа
        
        Args:
            session_id: ID сессии
            telegram_user_id: ID пользователя телеграм
            interlocutor_id: ID собеседника
            messages: Список сообщений для анализа
        """
        try:
            print(f"📝 Начинаем обработку батча сессии {session_id}, чата {interlocutor_id}, размер батча: {len(messages)}")
            

            if len(messages) > MAX_CHUNK_SIZE:
                chunks = self._split_messages_into_chunks(messages, MAX_CHUNK_SIZE)
                print(f"🔄 Большой батч разбит на {len(chunks)} частей по ~{MAX_CHUNK_SIZE} сообщений")
                

                compliments_results = {}
                engagement_results = {}
                attachment_results = {}
                

                historical_summary = await db_service.get_historical_summary(session_id, interlocutor_id)
                print(f"📚 Получено историческое саммери, длина: {len(historical_summary) if historical_summary else 0} символов")
                

                for i, chunk in enumerate(chunks):
                    print(f"🧩 Обрабатываем часть {i+1}/{len(chunks)}, размер: {len(chunk)} сообщений")
                    

                    if i % 3 == 0 and i > 0:
                        pass
                    

                    try:

                        if i > 0:
                            delay = 2.0
                            print(f"⏱️ Ждем {delay} секунд перед обработкой следующего чанка...")
                            await asyncio.sleep(delay)
                        
                        compliments, engagement, attachment = await self._get_metrics_for_chunk(chunk, historical_summary)
                        

                        if compliments:
                            for sender, count in compliments.items():
                                if sender in compliments_results:
                                    compliments_results[sender] += count
                                else:
                                    compliments_results[sender] = count
                        
                        if engagement:
                            for sender, score in engagement.items():
                                if sender in engagement_results:

                                    engagement_results[sender] = (engagement_results[sender] + score) / 2
                                else:
                                    engagement_results[sender] = score
                        
                        if attachment:
                            for sender, data in attachment.items():
                                if sender not in attachment_results:
                                    attachment_results[sender] = data
                                elif data.get("confidence", 0) > attachment_results[sender].get("confidence", 0):

                                    attachment_results[sender] = data
                                    
                        print(f"✅ Часть {i+1} успешно обработана")
                    except Exception as e:
                        print(f"❌ Ошибка при обработке части {i+1}: {e}")
                        import traceback
                        print(f"Стек ошибки:\n{traceback.format_exc()}")
                

                print(f"🔄 Генерируем рекомендации на основе всего батча")
                await self._generate_user_recommendations(session_id, telegram_user_id, interlocutor_id, messages, historical_summary or "")
                


                last_chunk_size = min(MAX_CHUNK_SIZE, len(messages))
                last_messages = messages[-last_chunk_size:]
                print(f"🔄 Обновляем саммери на основе последних {len(last_messages)} сообщений")
                await self._update_summary(session_id, interlocutor_id, last_messages, historical_summary)
                
            else:


                historical_summary = await db_service.get_historical_summary(session_id, interlocutor_id)
                print(f"📚 Получено историческое саммери, длина: {len(historical_summary) if historical_summary else 0} символов")
                

                print(f"🔄 Анализируем метрики для батча из {len(messages)} сообщений")
                


                print(f"🔄 Анализируем метрики...")
                await self._analyze_metrics(session_id, telegram_user_id, interlocutor_id, messages, historical_summary)
                
                print(f"🔄 Генерируем рекомендации для пользователя {telegram_user_id}")
                await self._generate_user_recommendations(session_id, telegram_user_id, interlocutor_id, messages, historical_summary or "")
                

                print(f"🔄 Обновляем саммери диалога")
                await self._update_summary(session_id, interlocutor_id, messages, historical_summary)
            

            print(f"🔄 Принудительно сохраняем метрики в БД")
            await self.flush_metrics()
            
            print(f"✅ Обработка батча сессии {session_id}, чата {interlocutor_id} завершена")
            
        except Exception as e:
            print(f"❌ Ошибка при обработке батча: {e}")

            import traceback
            print(f"Стек ошибки:\n{traceback.format_exc()}")
    
    async def _check_network_connection(self):
        """Проверяет сетевое соединение"""
        try:
            print(f"🔍 Проверка сети выполнена без DNS-проверок")
            
        except Exception as e:
            print(f"❌ Ошибка при проверке сети: {e}")
            import traceback
            print(f"Стек ошибки проверки сети:\n{traceback.format_exc()}")
    
    def _split_messages_into_chunks(self, messages: List[Dict[str, Any]], chunk_size: int) -> List[List[Dict[str, Any]]]:
        """
        Разбивает большой список сообщений на более мелкие части
        
        Args:
            messages: Список сообщений для разбиения
            chunk_size: Максимальный размер одной части
            
        Returns:
            Список частей с сообщениями
        """
        total_chunks = math.ceil(len(messages) / chunk_size)
        return [messages[i*chunk_size:(i+1)*chunk_size] for i in range(total_chunks)]
    
    async def _get_metrics_for_chunk(self, messages: List[Dict[str, Any]], historical_summary: Optional[str]):
        """
        Получает метрики для части сообщений
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Историческое саммери
            
        Returns:
            Tuple из (compliments, engagement, attachment)
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:

            start_time = time.time()
            

            current_loop = asyncio.get_running_loop()
            
            print(f"🔄 Запрашиваем комплименты для {len(messages)} сообщений")
            compliments_future = current_loop.run_in_executor(
                pool, 
                lambda: llm_handler.count_compliments(messages)
            )
            
            print(f"🔄 Запрашиваем уровень вовлеченности для {len(messages)} сообщений")
            engagement_future = current_loop.run_in_executor(
                pool, 
                lambda: llm_handler.calculate_engagement(messages, historical_summary or "", max_retries=3)
            )
            
            print(f"🔄 Запрашиваем тип привязанности для {len(messages)} сообщений")
            attachment_future = current_loop.run_in_executor(
                pool, 
                lambda: llm_handler.calculate_attachment(messages, historical_summary or "", max_retries=3)
            )
            

            compliments, engagement, attachment = await asyncio.gather(
                compliments_future, engagement_future, attachment_future
            )
            

            compliments = compliments or {}
            engagement = engagement or {}
            attachment = attachment or {}
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ Получение метрик заняло {elapsed_time:.2f} секунд")
            
            return compliments, engagement, attachment
    
    async def _update_summary(self, session_id: str, interlocutor_id: int, messages: List[Dict[str, Any]], historical_summary: Optional[str]) -> str:
        """Асинхронно обновляет и сохраняет историческое саммери"""
        try:

            current_loop = asyncio.get_running_loop()
            
            print(f"🔄 Обновляем саммери на основе {len(messages)} сообщений")
            new_summary = await current_loop.run_in_executor(
                None,
                lambda: llm_handler.update_summary(messages, historical_summary)
            )
            
            if new_summary:
                await db_service.save_historical_summary(session_id, interlocutor_id, new_summary)
                print(f"✅ Саммери для сессии {session_id}, чата {interlocutor_id} обновлено")
                return new_summary
        except Exception as e:
            print(f"❌ Ошибка при обновлении саммери: {e}")
            import traceback
            print(f"Стек ошибки саммери:\n{traceback.format_exc()}")
        return historical_summary or ""
    
    async def _analyze_metrics(self, session_id: str, telegram_user_id: int, interlocutor_id: int, 
                         messages: List[Dict[str, Any]], historical_summary: Optional[str]):
        """Асинхронно анализирует и сохраняет метрики диалога"""
        try:

            user_messages = [m for m in messages if str(m['SenderId']) == str(telegram_user_id)]
            interlocutor_messages = [m for m in messages if str(m['SenderId']) == str(interlocutor_id)]
            
            print(f"📊 Статистика сообщений:")
            print(f"  - От пользователя {telegram_user_id}: {len(user_messages)} сообщений")
            print(f"  - От собеседника {interlocutor_id}: {len(interlocutor_messages)} сообщений")
            

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:

                current_loop = asyncio.get_running_loop()
                
                print(f"🔄 Запрашиваем комплименты для {len(messages)} сообщений")
                compliments_future = current_loop.run_in_executor(
                    pool, 
                    lambda: llm_handler.count_compliments(messages)
                )
                
                print(f"🔄 Запрашиваем уровень вовлеченности для {len(messages)} сообщений")
                engagement_future = current_loop.run_in_executor(
                    pool, 
                    lambda: llm_handler.calculate_engagement(messages, historical_summary or "", max_retries=3)
                )
                
                print(f"🔄 Запрашиваем тип привязанности для {len(messages)} сообщений")
                attachment_future = current_loop.run_in_executor(
                    pool, 
                    lambda: llm_handler.calculate_attachment(messages, historical_summary or "", max_retries=3)
                )
                

                compliments, engagement, attachment = await asyncio.gather(
                    compliments_future, engagement_future, attachment_future
                )
            

            compliments = compliments or {}
            engagement = engagement or {}
            attachment = attachment or {}
            
            if not compliments and not engagement and not attachment:
                print("⚠️ Не удалось получить ни одной метрики")
                return
            

            print(f"📊 Получены метрики: комплименты={compliments}, вовлеченность={engagement}")
            

            previous_engagement = {}
            for sender_id in [telegram_user_id, interlocutor_id]:
                role = "user" if str(sender_id) == str(telegram_user_id) else "interlocutor"
                prev_metrics = await db_service.get_latest_metrics(session_id, interlocutor_id, role)
                if prev_metrics:
                    previous_engagement[str(sender_id)] = prev_metrics.get("engagement_score", 0)


            engagement = llm_handler.calculate_engagement(messages, historical_summary, previous_engagement, max_retries=3) or {}
            

            previous_attachments = {}
            for sender_id in [telegram_user_id, interlocutor_id]:
                role = "user" if str(sender_id) == str(telegram_user_id) else "interlocutor"
                prev_metrics = await db_service.get_latest_metrics(session_id, interlocutor_id, role)
                if prev_metrics:
                    previous_attachments[str(sender_id)] = {
                        "type": prev_metrics.get("attachment_type", "неизвестно"),
                        "confidence": prev_metrics.get("attachment_confidence", 0) * 100
                    }


            for sender_id in set(list(compliments.keys()) + list(engagement.keys()) + list(attachment.keys())):

                role = "user" if str(sender_id) == str(telegram_user_id) else "interlocutor"
                

                participant_messages = user_messages if role == "user" else interlocutor_messages
                if not participant_messages:
                    print(f"⚠️ Пропускаем сохранение метрик для {role} ({sender_id}): нет сообщений")
                    continue
                

                previous_metrics = await db_service.get_latest_metrics(session_id, interlocutor_id, role)
                previous_total = previous_metrics.get('total_compliments', 0) if previous_metrics else 0
                

                compliment_count = compliments.get(str(sender_id), 0)
                

                compliments_delta = compliment_count
                new_total = previous_total + compliments_delta
                
                print(f"Комплименты для {role} ({sender_id}):")
                print(f"  - Найдено в текущем батче: {compliment_count}")
                print(f"  - Предыдущее total_compliments: {previous_total}")
                print(f"  - Сохраняем delta: {compliments_delta}")
                print(f"  - Новое total: {new_total}")
                

                att = attachment.get(str(sender_id), {})
                att_type = att.get("type") or "unknown"
                att_conf = att.get("confidence") or 0
                if att_type in [None, "", "неизвестно"]:
                    att_type = "unknown"
                

                cache_key = f"{session_id}:{interlocutor_id}:{role}"
                self.metrics_cache[cache_key] = {
                    "session_id": session_id,
                    "telegram_user_id": telegram_user_id,
                    "interlocutor_id": interlocutor_id,
                    "role": role,
                    "compliments_delta": compliments_delta,
                    "total_compliments": new_total,
                    "engagement_score": engagement.get(str(sender_id), 0),
                    "attachment_type": att_type if att_type != "unknown" else "",
                    "attachment_confidence": att_conf / 100
                }
                print(f"✅ Метрики для {role} ({sender_id}) добавлены в кэш")
        
        except Exception as e:
            print(f"❌ Ошибка при анализе метрик: {e}")
            import traceback
            print(f"Стек ошибки метрик:\n{traceback.format_exc()}")
    
    async def _generate_user_recommendations(self, session_id: str, telegram_user_id: int, 
                                     interlocutor_id: int, messages: List[Dict[str, Any]], 
                                     historical_summary: str):
        """Асинхронно генерирует рекомендации для пользователя"""
        try:

            current_loop = asyncio.get_running_loop()
            

            if len(messages) > MAX_CHUNK_SIZE:
                print(f"🔄 Используем только последние {MAX_CHUNK_SIZE} сообщений для генерации рекомендаций")
                messages_for_recommendations = messages[-MAX_CHUNK_SIZE:]
            else:
                messages_for_recommendations = messages
                
            print(f"🔄 Генерируем рекомендации на основе {len(messages_for_recommendations)} сообщений")
            recommendations = await current_loop.run_in_executor(
                None,
                lambda: llm_handler.generate_recommendations(messages_for_recommendations, historical_summary, str(telegram_user_id))
            )
            
            if recommendations:

                print(f"🔄 Сохраняем рекомендации для пользователя {telegram_user_id} в БД")
                save_result = await db_service.save_user_recommendation(
                    session_id, 
                    telegram_user_id, 
                    interlocutor_id, 
                    recommendations
                )
                if save_result:
                    print(f"✅ Рекомендации для пользователя {telegram_user_id} успешно сохранены в БД")
                else:
                    print(f"⚠️ Не удалось сохранить рекомендации для пользователя {telegram_user_id} в БД")
            else:
                print(f"⚠️ Не удалось сгенерировать рекомендации для пользователя {telegram_user_id}")
        except Exception as e:
            print(f"❌ Ошибка при генерации рекомендаций: {e}")
            import traceback
            print(f"Стек ошибки рекомендаций:\n{traceback.format_exc()}")
    
    async def flush_metrics(self):
        """
        Асинхронно сохраняет накопленные метрики в базу данных
        Этот метод можно вызывать периодически
        """
        metrics_to_save = self.metrics_cache.copy()
        print(f"🔄 Начинаем сохранение метрик в БД, количество метрик в кэше: {len(metrics_to_save)}")
        self.metrics_cache.clear()
        
        for cache_key, metrics in metrics_to_save.items():
            try:
                print(f"🔄 Сохраняем метрики для {cache_key}:")
                print(f"  - session_id: {metrics['session_id']}")
                print(f"  - role: {metrics['role']}")
                print(f"  - compliments_delta: {metrics['compliments_delta']}")
                print(f"  - total_compliments: {metrics['total_compliments']}")
                print(f"  - engagement_score: {metrics['engagement_score']}")
                print(f"  - attachment_type: {metrics['attachment_type']}")
                print(f"  - attachment_confidence: {metrics['attachment_confidence']}")
                
                await db_service.save_chat_metrics(
                    metrics["session_id"],
                    metrics["telegram_user_id"],
                    metrics["interlocutor_id"],
                    metrics["role"],
                    metrics["compliments_delta"],
                    metrics["total_compliments"],
                    metrics["engagement_score"],
                    metrics["attachment_type"],
                    metrics["attachment_confidence"]
                )
                print(f"✅ Метрики для {cache_key} сохранены в БД")
            except Exception as e:
                print(f"❌ Ошибка при сохранении метрик для {cache_key}: {e}")
                import traceback
                print(f"Стек ошибки:\n{traceback.format_exc()}")

                self.metrics_cache[cache_key] = metrics


analysis_service = AnalysisService() 