import asyncio
from aiokafka import AIOKafkaConsumer
import json
import time
import threading
from utils.batching import SessionBatcher
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, BATCH_SIZE, BATCH_TIMEOUT_SECONDS
from services.analysis_service import analysis_service

async def start_consumer():
    """Асинхронный обработчик сообщений Kafka"""
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id='telegram-metrics-group',
        auto_offset_reset='earliest'
    )
    
    await consumer.start()
    
    batcher = SessionBatcher(max_batch_size=BATCH_SIZE, max_wait=BATCH_TIMEOUT_SECONDS)
    
    metrics_flush_task = asyncio.create_task(metrics_flusher())
    
    print("Kafka consumer started...")
    
    try:
        while True:
            try:

                batch = await consumer.getmany(timeout_ms=1000)
                
                for tp, messages in batch.items():
                    for msg in messages:
                        try:
                            message = json.loads(msg.value.decode('utf-8'))
                            session_id = message["SessionId"]
                            interlocutor_id = message["TelegramInterlocutorId"]
                            telegram_user_id = message["TelegramUserId"]
                            
                            batcher.add_message(session_id, interlocutor_id, message)
                        except Exception as e:
                            print(f"Error parsing message: {e}")
                

                for (session_id, interlocutor_id), batch in batcher.get_ready_batches():
                    print(f"Processing batch for session {session_id}, chat {interlocutor_id}, size={len(batch)}")
                    

                    telegram_user_id = batch[0].get("TelegramUserId", 0)
                    

                    asyncio.create_task(
                        process_batch(session_id, telegram_user_id, interlocutor_id, batch)
                    )
                

                await asyncio.sleep(0.01)
                
            except Exception as e:
                print(f"Error processing Kafka messages: {e}")
                await asyncio.sleep(1)
    
    finally:

        metrics_flush_task.cancel()
        await consumer.stop()

async def process_batch(session_id, telegram_user_id, interlocutor_id, messages):
    """Асинхронно обрабатывает готовый батч сообщений"""
    print(f"🧠 Анализируем чат {interlocutor_id} сессии {session_id} ({len(messages)} сообщений)")
    

    await analysis_service.process_batch(session_id, telegram_user_id, interlocutor_id, messages)

async def metrics_flusher():
    """Периодически сохраняет накопленные метрики в БД"""
    while True:
        try:
            await asyncio.sleep(60)
            await analysis_service.flush_metrics()
        except asyncio.CancelledError:

            break
        except Exception as e:
            print(f"Error in metrics flusher: {e}")
            await asyncio.sleep(10)

def run():
    """Точка входа для запуска асинхронного Kafka consumer"""
    asyncio.run(start_consumer())

