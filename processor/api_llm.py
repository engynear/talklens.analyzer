import json
import re
import time
from typing import List, Dict, Any, Optional
from yandex_cloud_ml_sdk import YCloudML

from .llm_interface import LLMInterface
from .prompts import (
    compliments_prompt,
    engagement_prompt,
    attachment_prompt,
    recommendations_prompt,
    summary_prompt,
    legacy_analysis_prompt
)
from .yandex_prompts import (
    compliments_messages,
    engagement_messages,
    attachment_messages,
    recommendations_messages,
    summary_messages,
    legacy_analysis_messages
)

class ApiLLM(LLMInterface):
    def __init__(self, api_url: str = None, api_key: str = None, folder_id: str = None):
        """
        Инициализирует клиент для работы с YandexGPT API
        
        Args:
            api_url: Не используется для YandexGPT, оставлен для совместимости
            api_key: API ключ для YandexGPT
            folder_id: Идентификатор каталога Yandex Cloud
        """
        self.api_url = api_url
        self.api_key = api_key
        self.folder_id = folder_id
        self.sdk = None
        
        print("🔄 Инициализация API-клиента без проверки сети")
        
        if folder_id and api_key:
            try:
                print(f"🔄 Инициализация YCloudML SDK с folder_id={folder_id[:5]}...")
                self.sdk = YCloudML(
                    folder_id=folder_id,
                    auth=api_key
                )
                print(f"✅ YCloudML SDK инициализирован успешно")
            except Exception as e:
                print(f"❌ Ошибка инициализации YCloudML SDK: {e}")
                import traceback
                print(f"Стек ошибки:\n{traceback.format_exc()}")
        elif api_url:
            print(f"🔄 Используется обычный API URL: {api_url}")
        else:
            print("⚠️ Предупреждение: API не сконфигурирован должным образом")

    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        """
        Форматирует список сообщений в текст для чата
        
        Args:
            messages: Список сообщений для форматирования
            
        Returns:
            Отформатированный текст чата
        """
        print(f"🔄 Форматирование {len(messages)} сообщений в текст")
        return "\n".join([f"{m['SenderId']}: {m['MessageText']}" for m in messages])

    def _make_request(self, messages: List[Dict[str, str]], max_retries: int = 3) -> str:
        """
        Выполняет запрос к YandexGPT API
        
        Args:
            messages: Список сообщений в формате YandexGPT
            max_retries: Максимальное количество попыток
            
        Returns:
            Текст ответа от API
        """
        if not self.sdk and not self.api_url:
            print("❌ SDK не инициализирован и API URL не указан")
            return ""
        
        print(f"📝 Запрос содержит {len(messages)} сообщений")
        if len(messages) > 0:
            print(f"📝 Роль первого сообщения: {messages[0].get('role', 'неизвестно')}")
            print(f"📝 Первые 50 символов: {messages[0].get('text', '')[:50]}...")
            
        for attempt in range(max_retries):
            try:
                print(f"🔄 Попытка #{attempt + 1} отправки запроса к API")
                start_time = time.time()
                
                if self.sdk:
                    print("🔄 Отправка запроса через YCloudML SDK...")
                    result = self.sdk.models.completions("yandexgpt").configure(temperature=0.0).run(messages)
                    
                    if hasattr(result, '__iter__'):
                        print(f"✅ Получен итерируемый результат, тип: {type(result)}")
                        for alternative in result:
                            if hasattr(alternative, 'text'):
                                elapsed_time = time.time() - start_time
                                text = alternative.text.strip()
                                print(f"🧠 Yandex GPT ответ получен за {elapsed_time:.2f} сек., длина: {len(text)} символов")
                                if text:
                                    print(f"🧠 Первые 200 символов ответа: {text[:200]}...")
                                return text
                            else:
                                print(f"⚠️ Объект Alternative не имеет атрибута text: {alternative}")
                    else:
                        print(f"⚠️ Неожиданный тип результата: {type(result)}")
                    
                    print(f"⚠️ Не удалось извлечь текст из ответа")
                    return ""
                
                else:
                    try:
                        import requests
                        print("🔄 Отправка запроса через HTTP API...")
                        headers = {
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        }
                        
                        data = {
                            "messages": messages,
                            "temperature": 0.0
                        }
                        
                        response = requests.post(self.api_url, headers=headers, json=data)
                        response.raise_for_status()
                        
                        result = response.json()
                        elapsed_time = time.time() - start_time
                        print(f"✅ Ответ от HTTP API получен за {elapsed_time:.2f} сек.")
                        
                        if "choices" in result and len(result["choices"]) > 0:
                            text = result["choices"][0].get("message", {}).get("content", "").strip()
                            print(f"🧠 API ответ, длина: {len(text)} символов")
                            if text:
                                print(f"🧠 Первые 100 символов ответа: {text[:100]}...")
                            return text
                        else:
                            print(f"⚠️ Неожиданный формат ответа API: {result}")
                            return ""
                    except requests.exceptions.ConnectionError as e:
                        print(f"❌ Ошибка подключения к API: {e}")
                        import traceback
                        print(f"Стек ошибки подключения:\n{traceback.format_exc()}")
                        time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Ошибка API запроса (попытка {attempt + 1}/{max_retries}): {e}")
                import traceback
                print(f"Стек ошибки:\n{traceback.format_exc()}")
                if attempt == max_retries - 1:
                    return ""
                time.sleep(1 + attempt)
                
        return ""

    def _clean_markdown(self, text: str) -> str:
        """
        Очищает текст от Markdown-разметки кода
        
        Args:
            text: Исходный текст с Markdown
            
        Returns:
            Очищенный текст
        """

        cleaned_text = re.sub(r'```(?:json|)\n?(.*?)\n?```', r'\1', text, flags=re.DOTALL)
        

        cleaned_text = re.sub(r'`(.*?)`', r'\1', cleaned_text)
        
        print(f"🧹 Текст очищен от Markdown: было {len(text)} символов, стало {len(cleaned_text)}")
        
        return cleaned_text
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает JSON из текстового ответа модели с улучшенной валидацией
        
        Args:
            text: Текст ответа
            
        Returns:
            Извлеченный JSON объект или None в случае ошибки
        """
        if not text:
            print("❌ Пустой текст для извлечения JSON")
            return None
            

        max_fix_attempts = 3
            
        try:

            cleaned_text = self._clean_markdown(text)
            print(f"🔍 Ищем JSON в тексте: {cleaned_text[:100]}...")
            

            try:
                result = json.loads(cleaned_text)
                print(f"✅ Успешно загружен JSON")
                

                fixed_result = {}
                for key, value in result.items():

                    if 'SenderId' in key or 'пользователь' in key or 'user' in key:
                        print(f"⚠️ Пропускаем неверный формат ID: {key}")
                        continue
                    

                    new_key = str(key) if key is not None else ""
                    

                    if value is not None:
                        fixed_result[new_key] = value
                
                if fixed_result:
                    print(f"✅ Валидация ключей успешна: {fixed_result}")
                    return fixed_result
                else:
                    print("⚠️ После валидации ключей результат пустой")
            except json.JSONDecodeError as e:
                print(f"ℹ️ Не получилось загрузить весь текст как JSON: {e}")
                

            print("🔄 Ищем JSON в тексте с помощью регулярного выражения...")
            json_matches = re.findall(r'{[\s\S]*?}', cleaned_text)
            if json_matches:
                for json_text in json_matches:
                    for attempt in range(max_fix_attempts):
                        try:
                            result = json.loads(json_text)
                            print(f"✅ Найден валидный JSON: {result}")
                            

                            fixed_result = {}
                            for key, value in result.items():

                                if 'SenderId' in key or 'пользователь' in key or 'user' in key:
                                    print(f"⚠️ Пропускаем неверный формат ID: {key}")
                                    continue
                                

                                new_key = str(key) if key is not None else ""
                                

                                if value is not None:
                                    fixed_result[new_key] = value
                            
                            if fixed_result:
                                print(f"✅ Валидация ключей успешна: {fixed_result}")
                                return fixed_result
                            else:
                                print("⚠️ После валидации ключей результат пустой")
                                break
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ Найденный текст не является валидным JSON: {e}")
                            if attempt < max_fix_attempts - 1:
                                print("🔄 Попытка исправить некорректный JSON...")
                                json_text = self._fix_json(json_text)
                            else:
                                print(f"❌ Не удалось исправить JSON: {e}")
                                break
                

            print("⚠️ Не удалось извлечь JSON, возвращаем пустой словарь")
            return {}
                
        except Exception as e:
            print(f"❌ Ошибка при извлечении JSON: {e}")
            import traceback
            print(f"Стек ошибки JSON-извлечения:\n{traceback.format_exc()}")
            return {}
    
    def _fix_json(self, json_text: str) -> str:
        """
        Пытается исправить некорректный JSON
        
        Args:
            json_text: Некорректный JSON-текст
            
        Returns:
            Исправленный JSON-текст
        """

        fixed = re.sub(r"'([^']*)':", r'"\1":', json_text)
        

        fixed = re.sub(r':\s*"([^"]*)"([^,}])', r':"\1"\2', fixed)
        

        fixed = re.sub(r'([{,])\s*([a-zA-Z0-9_]+):', r'\1"\2":', fixed)
        
        return fixed
    
    def count_compliments(self, messages: List[Dict[str, Any]], max_retries: int = 3) -> Dict[str, Any]:
        """
        Подсчитывает количество комплиментов в диалоге
        
        Args:
            messages: Список сообщений для анализа
            max_retries: Максимальное количество попыток
            
        Returns:
            Dict с количеством комплиментов или пустой словарь в случае ошибки
        """
        print(f"🔄 Запрос на подсчет комплиментов для {len(messages)} сообщений")
        

        if not messages:
            print("⚠️ Пустой список сообщений для анализа комплиментов")
            return {}
            
        chat_text = self._format_messages(messages)
        yandex_messages = compliments_messages(chat_text)
        response = self._make_request(yandex_messages, max_retries)
        result = self._extract_json_with_retries(response, max_retries)
        print(f"✅ Результат подсчета комплиментов: {result}")
        return result

    def calculate_engagement(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        previous_engagement: dict = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Рассчитывает уровень вовлеченности участников
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Историческое саммери
            previous_engagement: Предыдущие значения вовлечённости
            max_retries: Максимальное количество попыток
            
        Returns:
            Dict с уровнем вовлеченности или пустой словарь в случае ошибки
        """
        print(f"🔄 Запрос на расчет уровня вовлеченности для {len(messages)} сообщений")
        

        if not messages:
            print("⚠️ Пустой список сообщений для анализа вовлеченности")
            return {}
            
        chat_text = self._format_messages(messages)
        user_ids = list({str(m['SenderId']) for m in messages})
        yandex_messages = engagement_messages(chat_text, user_ids, historical_summary, previous_engagement)
        response = self._make_request(yandex_messages, max_retries)
        result = self._extract_json_with_retries(response, max_retries)
        print(f"✅ Результат расчета вовлеченности: {result}")
        return result

    def calculate_attachment(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        previous_attachments: dict = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Определяет тип привязанности участников диалога
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Историческое саммери
            previous_attachments: Предыдущие прогнозы привязанности
            max_retries: Максимальное количество попыток
            
        Returns:
            Dict с типом привязанности или пустой словарь в случае ошибки
        """
        print(f"🔄 Запрос на определение типа привязанности для {len(messages)} сообщений")
        

        if not messages:
            print("⚠️ Пустой список сообщений для анализа привязанности")
            return {}
            
        chat_text = self._format_messages(messages)
        user_ids = list({str(m['SenderId']) for m in messages})
        yandex_messages = attachment_messages(chat_text, user_ids, historical_summary, previous_attachments)
        response = self._make_request(yandex_messages, max_retries)
        result = self._extract_json_with_retries(response, max_retries)
        print(f"✅ Результат определения привязанности: {result}")
        return result

    def generate_recommendations(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        user_id: str,
        max_retries: int = 3
    ) -> str:
        """
        Генерирует рекомендации для пользователя
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Историческое саммери
            user_id: ID пользователя
            max_retries: Максимальное количество попыток
            
        Returns:
            Текст с рекомендациями
        """
        print(f"🔄 Запрос на генерацию рекомендаций для пользователя {user_id}, {len(messages)} сообщений")
        

        if not messages:
            print("⚠️ Пустой список сообщений для генерации рекомендаций")
            return ""
            
        chat_text = self._format_messages(messages)
        yandex_messages = recommendations_messages(chat_text, historical_summary, user_id)
        
        for attempt in range(max_retries):
            try:
                response = self._make_request(yandex_messages, max_retries=1)
                

                if not response:
                    print(f"⚠️ Пустой ответ при генерации рекомендаций (попытка {attempt+1}/{max_retries})")
                    time.sleep(1 + attempt)
                    continue
                

                clean_response = self._clean_markdown(response)
                

                if self._contains_prohibited_content(clean_response):
                    print(f"⚠️ Обнаружен запрещенный контент в рекомендациях (попытка {attempt+1}/{max_retries})")
                    

                    if attempt == max_retries - 1:
                        print("⚠️ Не удалось получить рекомендации без запрещенного контента")
                        return "Проанализируйте диалог и подумайте, как можно улучшить коммуникацию."
                    

                    repair_prompt = f"""Дай конкретные рекомендации по общению для пользователя {user_id} на основе анализа диалога.

Диалог:
{chat_text}

Историческое саммери:
{historical_summary}

СТРОГО запрещено в твоем ответе:
1. Любые ссылки, особенно на ya.ru, yandex.ru, google.com и др.
2. Фразы типа "посмотрите в поиске", "в интернете есть информация" и подобные
3. Упоминание поисковых систем или интернета
4. Любые HTML или Markdown ссылки
5. Упоминание, что ты не можешь помочь

Твой предыдущий ответ содержал запрещенный контент (ссылки или упоминания поиска).
Дай 3-5 конкретных, практических рекомендаций, основанных ТОЛЬКО на этом диалоге.
Рекомендации должны быть короткими, понятными и действенными."""
                    
                    yandex_messages = [
                        {"role": "system", "text": "Ты коммуникационный консультант, дающий практические советы."},
                        {"role": "user", "text": repair_prompt}
                    ]
                    time.sleep(1 + attempt)
                    continue
                
                print(f"✅ Сгенерированы рекомендации длиной {len(clean_response)} символов")
                return clean_response
                
            except Exception as e:
                print(f"❌ Ошибка при генерации рекомендаций (попытка {attempt+1}/{max_retries}): {e}")
                import traceback
                print(f"Стек ошибки:\n{traceback.format_exc()}")
                
                if attempt == max_retries - 1:
                    print("⚠️ Не удалось сгенерировать рекомендации после всех попыток")
                    return ""
                
                time.sleep(1 + attempt)
        

        return ""

    def update_summary(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        """
        Обновляет историческое саммери на основе нового батча сообщений
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Предыдущее историческое саммери диалога (если есть)
            max_retries: Максимальное количество попыток анализа
            
        Returns:
            Строка с обновленным саммери или None в случае ошибки
        """
        chat_text = self._format_messages(messages)
        yandex_messages = summary_messages(chat_text, historical_summary)
        response = self._make_request(yandex_messages, max_retries)
        return response

    def get_llm_response(self, prompt: str, max_retries: int = 3) -> str:
        """
        Получает ответ от LLM на основе простого текстового промпта
        
        Args:
            prompt: Текстовый промпт
            max_retries: Максимальное число повторных попыток
            
        Returns:
            Текстовый ответ от LLM
        """
        messages = [
            {"role": "user", "text": prompt}
        ]
        return self._make_request(messages, max_retries)
    
    def _extract_json_with_retries(self, text: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Пытается извлечь JSON с несколькими попытками, включая повторные запросы к LLM
        
        Args:
            text: Текст ответа
            max_retries: Максимальное число повторных попыток
            
        Returns:
            Извлеченный JSON или пустой словарь
        """

        result = self._extract_json(text)
        if result:
            return result
            

        for attempt in range(max_retries):
            try:
                print(f"🔄 Повторная попытка #{attempt + 1} получения JSON")
                

                repair_prompt = f"""Проанализируй следующий текст и верни его как валидный JSON.
                
                    ТЕКСТ:
                    {text}

                    ВАЖНЫЕ ПРАВИЛА:
                    1. Верни ТОЛЬКО валидный JSON, без дополнительного текста
                    2. В качестве ключей используй только числовые ID без кавычек
                    3. НЕ ИСПОЛЬЗУЙ 'SenderId' или 'user' в ключах
                    4. Все текстовые значения должны быть строками в двойных кавычках
                    5. Числовые значения НЕ должны быть в кавычках

                    Пример правильного формата:
                    {{"123": 5, "456": {"type": "secure", "confidence": 70}}}

                    Пример НЕПРАВИЛЬНОГО формата:
                    {{"SenderId_123": 5, "user": {"type": "secure", "confidence": "70"}}}

                    Верни ТОЛЬКО исправленный JSON:
                """
                

                new_response = self.get_llm_response(repair_prompt)
                result = self._extract_json(new_response)
                
                if result:
                    print(f"✅ Успешно получен JSON после повторного запроса (попытка {attempt + 1}/{max_retries})")
                    return result
                    
            except Exception as e:
                print(f"❌ Ошибка при повторной попытке получить JSON: {e}")
                

            time.sleep(1 + attempt)
            
        print("❌ Не удалось получить валидный JSON после всех попыток")
        return {}

    def _contains_prohibited_content(self, text: str) -> bool:
        """
        Проверяет текст на наличие запрещенного контента
        
        Args:
            text: Текст для проверки
            
        Returns:
            True если содержит запрещенный контент, иначе False
        """

        link_patterns = [
            r'\[.*?\]\(.*?\)',
            r'https?://\S+',
            r'www\.\S+',
            r'ya\.ru',
            r'yandex\.ru',
            r'google\.com',
            r'в поиске',
            r'в интернете',
            r'посмотрите'
        ]
        

        for pattern in link_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                print(f"⚠️ Обнаружен запрещенный контент по паттерну: {pattern}")
                return True
                
        return False