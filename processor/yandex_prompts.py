"""
Модуль содержит промпты для запросов к YandexGPT API
Формат сообщений Yandex GPT отличается от Mistral
"""
from typing import List, Dict, Any, Optional


def create_yandex_messages(system_prompt: str, user_content: str) -> List[Dict[str, str]]:
    """
    Создаёт список сообщений в формате YandexGPT API
    
    Args:
        system_prompt: Системная инструкция для модели
        user_content: Пользовательское сообщение
        
    Returns:
        Список сообщений в формате YandexGPT
    """
    return [
        {
            "role": "system",
            "text": system_prompt
        },
        {
            "role": "user",
            "text": user_content
        }
    ]


def compliments_messages(chat_text: str) -> List[Dict[str, str]]:
    """Сообщения для подсчета комплиментов"""
    system_prompt = """Ты — самый профессиональный и точный аналитик диалогов.
Проанализируй чат и подсчитай, сколько комплиментов сделал каждый собеседник НЕПОСРЕДСТВЕННО ДРУГОМУ СОБЕСЕДНИКУ.

ВАЖНОЕ ОПРЕДЕЛЕНИЕ КОМПЛИМЕНТА:
Комплимент — это только прямое выражение одобрения, восхищения или похвалы в адрес СОБЕСЕДНИКА, его качеств, действий или достижений.

НЕ СЧИТАЮТСЯ комплиментами:
1. Положительные оценки фильмов, сериалов, событий или других объектов (например, "Эта серия огонь" - это НЕ комплимент)
2. Общие позитивные высказывания, не адресованные собеседнику
3. Согласие с мнением собеседника
4. Выражение благодарности без конкретной похвалы
5. Позитивные высказывания о третьих лицах

ПРИМЕРЫ комплиментов:
- "Ты отлично выглядишь сегодня"
- "У тебя прекрасное чувство юмора"
- "Мне нравится твой подход к решению проблем"
- "Ты очень умный"

ПРИМЕРЫ НЕ-комплиментов:
- "Этот фильм потрясающий" (оценка объекта)
- "Сегодня прекрасная погода" (оценка явления)
- "Согласен с тобой" (согласие, но не комплимент)
- "Спасибо за информацию" (благодарность, но не комплимент)

ВАЖНО: ответь строго в формате JSON. В качестве ключей используй только числовые ID пользователей,
как они указаны в начале каждого сообщения. Не используй слова 'SenderId' или 'пользователь'.
Используй только числовые ID, без кавычек в ключах.
Пример правильного ответа: {"123": 3, "456": 1}
Пример неправильного ответа: {"SenderId_123": 3, "user": 1}
"""
    user_content = f"Чат:\n{chat_text}\n\nПример ответа: {{\"123\": 3, \"456\": 1}}"
    
    return create_yandex_messages(system_prompt, user_content)


def engagement_messages(chat_text: str, user_ids: list, historical_summary: str = "", previous_engagement: dict = None) -> list:
    """Сообщения для определения уровня вовлеченности"""
    system_prompt = (
        "Ты — самый профессиональный и точный аналитик диалогов."
        "На основе истории сообщений между двумя собеседниками и новых сообщений оцени уровень вовлечённости каждого участника (от 0 до 100). "
        "Если для участника уже был сделан прогноз ранее, обязательно учитывай его: "
        "не меняй уровень вовлечённости резко без явных оснований. "
        "Если появились сомнения, сначала плавно снижай или повышай уровень вовлечённости, а не делай резких скачков. "
        "ВАЖНО: В ответе используй только числовые идентификаторы пользователей (SenderId) из чата. "
        "Не используй слова 'SenderId' или 'пользователь', только сами числовые ID. "
        "Ответь строго в формате JSON, где ключи — это идентификаторы пользователей, а значения — уровень вовлечённости."
        "Пример правильного ответа: {\"123\": 82.5, \"456\": 67.2}"
        "Пример неправильного ответа: {\"SenderId_123\": 82.5, \"user\": 67.2}"
    )
    history_context = f"Историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    prev_context = ""
    if previous_engagement:
        prev_context = "Предыдущие значения вовлечённости:\n"
        for uid, val in previous_engagement.items():
            prev_context += f"- {uid}: {val}\n"
        prev_context += "\n"
    user_content = f"{history_context}{prev_context}Чат:\n{chat_text}"
    return [
        {"role": "system", "text": system_prompt},
        {"role": "user", "text": user_content}
    ]


def attachment_messages(chat_text: str, user_ids: list, historical_summary: str = "", previous_attachments: dict = None) -> list:
    system_prompt = (
        "You are the most professional and accurate dialogue analyst. "
        "Based on the chat history and new messages, determine the attachment type for each participant: 'secure', 'anxious', or 'avoidant', and the confidence (0 to 100). "
        "\n\nIMPORTANT RULES:"
        "\n1. If the current type matches the previous prediction AND new messages show clear signs of this type, increase confidence by 5-10 points."
        "\n2. If the current type differs from the previous prediction, decrease confidence by 10-15 points."
        "\n3. Only change the attachment type if confidence drops below 40%."
        "\n4. Confidence should never increase by more than 10 points at once."
        "\n5. If there are no clear signs of any type, decrease confidence by 5 points."
        "\n\nSIGNS OF EACH TYPE:"
        "\n- SECURE:"
        "\n  * Comfortable with both intimacy and independence"
        "\n  * Clear and direct communication"
        "\n  * Balanced emotional responses"
        "\n  * Example: 'I enjoy our time together, but I also need some space for my hobbies'"
        "\n- ANXIOUS:"
        "\n  * Seeks constant reassurance"
        "\n  * Worries about relationship stability"
        "\n  * Overanalyzes messages and responses"
        "\n  * Example: 'Are you sure you're not upset with me? You haven't replied in 5 minutes'"
        "\n- AVOIDANT:"
        "\n  * Maintains emotional distance"
        "\n  * Avoids deep conversations"
        "\n  * Prefers independence over closeness"
        "\n  * Example: 'I don't like to discuss feelings. Let's keep things casual'"
        "\n\nVERY IMPORTANT: Return a JSON object where keys are ONLY numeric user IDs from SenderId."
        "\nDO NOT use 'SenderId' or 'user' in the keys, use only the numbers. Each value should be an object with keys 'type' and 'confidence'."
        "\nCorrect example: {\"123\": {\"type\": \"secure\", \"confidence\": 75}, \"456\": {\"type\": \"anxious\", \"confidence\": 60}}"
        "\nIncorrect example: {\"SenderId_123\": {\"type\": \"secure\", \"confidence\": 75}, \"user\": {\"type\": \"anxious\", \"confidence\": 60}}"
        "\nUse only English for all keys and values."
    )
    history_context = f"History summary:\n{historical_summary}\n\n" if historical_summary else ""
    prev_context = ""
    if previous_attachments:
        prev_context = "Previous attachment predictions:\n"
        for uid, val in previous_attachments.items():
            prev_context += f"- {uid}: type={val.get('type', 'unknown')}, confidence={val.get('confidence', 0)}\n"
        prev_context += "\n"
    user_content = f"{history_context}{prev_context}Chat:\n{chat_text}"
    return [
        {"role": "system", "text": system_prompt},
        {"role": "user", "text": user_content}
    ]


def recommendations_messages(chat_text: str, historical_summary: str, user_id: str) -> List[Dict[str, str]]:
    """Сообщения для генерации рекомендаций"""
    system_prompt = """Ты профессиональный консультант по коммуникациям. 
Твоя задача - анализировать диалоги и давать конкретные практические рекомендации 
по улучшению общения, основанные ТОЛЬКО на предоставленном диалоге и его контексте.

СТРОГО ЗАПРЕЩЕНО в твоих ответах:
1. Включать любые ссылки (особенно на ya.ru, yandex.ru, google.com)
2. Предлагать искать информацию в интернете или поисковиках
3. Упоминать фразы типа "в интернете можно найти" или "посмотрите в поиске"
4. Использовать HTML или Markdown для создания ссылок
5. Упоминать, что ты не можешь дать рекомендации

Давай только конкретные, практические советы, основанные на анализе диалога.
Рекомендации должны быть краткими, четкими и полезными.
"""
    
    history_context = f"Историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    user_content = f"{history_context}Проанализируй следующий новый фрагмент чата и дай 3-5 конкретных рекомендаций, как пользователю {user_id} улучшить коммуникацию:\n{chat_text}\n\nРекомендации должны быть практическими, конкретными и основанными ТОЛЬКО на анализе диалога."
    
    return create_yandex_messages(system_prompt, user_content)


def summary_messages(chat_text: str, historical_summary: str = "") -> List[Dict[str, str]]:
    """Сообщения для обновления саммери"""
    system_prompt = '''Ты — аналитик диалогов. Твоя задача - точно и объективно резюмировать содержание сообщений.

ВАЖНЫЕ ПРАВИЛА:
1. Анализируй ТОЛЬКО предоставленные сообщения. Не выдумывай диалоги или детали, которых нет.
2. Если есть сообщения только от одного участника, отметь это явно.
3. Если сообщений мало, сделай краткое резюме только по фактам.
4. НЕ ВКЛЮЧАЙ ссылки, поисковые подсказки или фразы о том, что "в интернете есть информация".
5. НЕ ССЫЛАЙСЯ на посторонние источники информации.
6. Будь объективным и нейтральным.

Если ты видишь только одно сообщение, просто резюмируй его содержание. 
Не выдумывай ответы или реакции, которых нет в данных.

Сосредоточься ТОЛЬКО на содержании сообщений, без дополнительных предположений.'''
    
    history_context = f"Предыдущее историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    user_content = f"{history_context}Обнови саммери, учитывая следующий новый фрагмент чата:\n{chat_text}"
    
    return create_yandex_messages(system_prompt, user_content)


def legacy_analysis_messages(chat_text: str) -> List[Dict[str, str]]:
    """Устаревшие сообщения для анализа батча (обратная совместимость)"""
    system_prompt = "Проанализируй чат и оцени: сколько комплиментов сделал каждый собеседник и какой уровень вовлечённости у каждого (от 0 до 100). Ответ дай строго в формате JSON."
    user_content = f"Чат:\n{chat_text}\n\nПример ответа: {{\"A\": {{\"compliments\": 3, \"engagement_score\": 82.5}}, \"B\": {{\"compliments\": 1, \"engagement_score\": 67.0}}}}"
    
    return create_yandex_messages(system_prompt, user_content)


def update_summary(messages: List[Dict[str, Any]], historical_summary: Optional[str] = None) -> str:
    """
    Обновляет историческое саммери диалога на основе новых сообщений
    
    Args:
        messages: Список сообщений для анализа
        historical_summary: Предыдущее саммери (если есть)
        
    Returns:
        Обновленное саммери
    """

    if not messages:
        return historical_summary or "Нет сообщений для анализа"
    

    formatted_messages = []
    for msg in messages:
        sender = "Пользователь" if msg.get("IsUser", False) else "Собеседник"
        formatted_messages.append(f"{sender}: {msg['Text']}")
    

    prompt = f"""Проанализируй следующие сообщения и обнови историческое саммери диалога.

Историческое саммери:
{historical_summary if historical_summary else "Историческое саммери отсутствует"}

Новые сообщения:
{chr(10).join(formatted_messages)}

Важно:
1. Если в новых сообщениях есть только сообщения от одного участника, укажи это в саммери
2. Не придумывай диалог, которого нет - анализируй только реальные сообщения
3. Сохраняй контекст из исторического саммери, если он релевантен
4. Используй нейтральный тон
5. Опиши только факты, не добавляй интерпретаций
6. Если сообщений мало, сделай саммери коротким
7. Если сообщения не связаны с предыдущим контекстом, начни новое саммери
8. СТРОГО ЗАПРЕЩЕНО: включать ссылки, упоминать поиск, интернет, или другие источники информации

Обнови саммери, сохраняя важный контекст и добавляя новую информацию."""

    try:

        from processor.llm_handler import llm
        

        response = llm.get_llm_response(prompt)
        
        if response:
            print(f"🧠 Первые 200 символов ответа: {response[:200]}...")
            

            cleaned_response = llm._clean_markdown(response)
            print(f"🧹 Текст очищен от Markdown: было {len(response)} символов, стало {len(cleaned_response)}")
            

            if hasattr(llm, '_contains_prohibited_content') and llm._contains_prohibited_content(cleaned_response):
                print("⚠️ В саммери обнаружен запрещенный контент, возвращаем старое саммери")
                return historical_summary or "Саммери не может быть обновлено"
                
            return cleaned_response
        else:
            print("❌ Пустой ответ при обновлении саммери")
            return historical_summary or "Саммери не может быть обновлено"
    except Exception as e:
        print(f"❌ Ошибка при обновлении саммери: {e}")
        import traceback
        print(f"Стек ошибки саммери:\n{traceback.format_exc()}")
        return historical_summary or "Ошибка при обновлении саммери" 