import asyncio
import signal
import platform
from consumer.kafka_consumer import start_consumer

async def main():
    """Главная точка входа в приложение"""
    print("Запуск приложения TalkLens Analyzer...")
    

    if platform.system() != 'Windows':

        loop = asyncio.get_running_loop()
        for s in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                s, lambda: asyncio.create_task(shutdown())
            )
    
    try:

        await start_consumer()
    except KeyboardInterrupt:
        print("Прервано пользователем (Ctrl+C)")
        await shutdown()
    finally:
        print("Приложение завершено")

async def shutdown():
    """Корректное завершение приложения"""
    print("Получен сигнал завершения работы, закрываем соединения...")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    


    if platform.system() != 'Windows':
        asyncio.get_event_loop().stop()

if __name__ == "__main__":
    asyncio.run(main())
