from typing import List, Optional

def _create_local_prompt(instruction: str) -> str:
    """
    Создает промпт в формате для локальной instruct-модели.
    """
    return f"<s>[INST] {instruction} [/INST]"

def compliments_prompt(chat_text: str) -> str:
    instruction = (
        "Ты — самый профессиональный и точный аналитик диалогов. "
        "Проанализируй чат и подсчитай, сколько комплиментов сделал каждый собеседник. "
        "ВАЖНО: ответь строго в формате JSON. В качестве ключей используй только числовые ID пользователей, "
        "как они указаны в начале каждого сообщения. Не используй слова 'SenderId' или 'пользователь'. "
        "Используй только числовые ID, без кавычек в ключах."
        "Пример правильного ответа: {\"123\": 3, \"456\": 1}"
        "Пример неправильного ответа: {\"SenderId_123\": 3, \"user\": 1}"
        f"\n\nЧат для анализа:\n{chat_text}\n\nПример ответа: {{\"123\": 3, \"456\": 1}}"
    )
    return _create_local_prompt(instruction)

def engagement_prompt(chat_text: str, user_ids: List[str], historical_summary: Optional[str] = None) -> str:
    history_context = f"Историческое саммери диалога:\n{historical_summary}\n\n" if historical_summary else ""
    instruction = (
        "Ты — самый профессиональный и точный аналитик диалогов. "
        "На основе истории сообщений между двумя собеседниками и новых сообщений оцени уровень вовлечённости каждого участника (от 0 до 100). "
        "Если для участника уже был сделан прогноз ранее, обязательно учитывай его: "
        "не меняй уровень вовлечённости резко без явных оснований. "
        "Если появились сомнения, сначала плавно снижай или повышай уровень вовлечённости, а не делай резких скачков. "
        "ВАЖНО: В ответе используй только числовые идентификаторы пользователей (SenderId) из чата. "
        "Не используй слова 'SenderId' или 'пользователь', только сами числовые ID. "
        "Ответь строго в формате JSON, где ключи — это идентификаторы пользователей, а значения — уровень вовлечённости."
        "Пример правильного ответа: {\"123\": 82.5, \"456\": 67.2}"
        "Пример неправильного ответа: {\"SenderId_123\": 82.5, \"user\": 67.2}"
        f"\n\n{history_context}Чат для анализа:\n{chat_text}"
    )
    return _create_local_prompt(instruction)

def attachment_prompt(chat_text: str, user_ids: List[str], historical_summary: Optional[str] = None) -> str:
    history_context = f"History summary:\n{historical_summary}\n\n" if historical_summary else ""
    instruction = (
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
        "\n  * Example: 'Are you sure you\'re not upset with me? You haven\'t replied in 5 minutes'"
        "\n- AVOIDANT:"
        "\n  * Maintains emotional distance"
        "\n  * Avoids deep conversations"
        "\n  * Prefers independence over closeness"
        "\n  * Example: 'I don\'t like to discuss feelings. Let\'s keep things casual'"
        "\n\nVERY IMPORTANT: Return a JSON object where keys are ONLY numeric user IDs from SenderId."
        "\nDO NOT use 'SenderId' or 'user' in the keys, use only the numbers. Each value should be an object with keys 'type' and 'confidence'."
        "\nCorrect example: {\"123\": {\"type\": \"secure\", \"confidence\": 75}, \"456\": {\"type\": \"anxious\", \"confidence\": 60}}"
        "\nIncorrect example: {\"SenderId_123\": {\"type\": \"secure\", \"confidence\": 75}, \"user\": {\"type\": \"anxious\", \"confidence\": 60}}"
        "\nUse only English for all keys and values."
        f"\n\n{history_context}Chat for analysis:\n{chat_text}"
    )
    return _create_local_prompt(instruction)

def recommendations_prompt(chat_text: str, historical_summary: Optional[str], user_id: str) -> str:
    history_context = f"Историческое саммери диалога:\n{historical_summary}\n\n" if historical_summary else ""
    instruction = (
        "Ты — коммуникационный коуч."
        f"Твоя задача дать пользователю {user_id} одну короткую, практичную рекомендацию, как улучшить или углубить общение с другим человеком на основе:"
        "Обобщения истории диалога,"
        "Анализа эмоциональных сигналов,"
        "Шаблонов вовлеченности,"
        "Новых сообщений"
        "Формулируй один конкретный и понятный совет, который легко применить:"
        "это может быть поведенческое действие (например, задать вопрос, проявить эмоцию, проявить инициативу) или рекомендация по переосмыслению своей роли в общении (например, быть внимательнее к тону, снизить давление и т.д.)."
        "Не добавляй пояснений, не давай длинных размышлений — только совет."
        "Совет должен быть в указательной форме."
        "Совет должен относиться не только к последним сообщениям, но и к истории диалога, учитывать контекст."
        "Примеры совета:"
        "Попробуй в ответ задать уточняющий вопрос — это покажет твою вовлеченность"
        "Предложи конкретное время или фильм — это поможет перевести идею в действие."
        "Добавь немного личного — небольшая деталь о себе сделает разговор теплее."
        f"\n\n{history_context}Дай рекомендацию пользователю {user_id}, последние сообщения:\n{chat_text}"
    )
    return _create_local_prompt(instruction)

def summary_prompt(chat_text: str, historical_summary: Optional[str] = None) -> str:
    history_context = f"Предыдущее историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    instruction = (
        "Ты — аналитик диалогов. Твоя задача - точно и объективно резюмировать содержание сообщений."
        "\n\nВАЖНЫЕ ПРАВИЛА:"
        "\n1. Анализируй ТОЛЬКО предоставленные сообщения. Не выдумывай диалоги или детали, которых нет."
        "\n2. Если есть сообщения только от одного участника, отметь это явно."
        "\n3. Если сообщений мало, сделай краткое резюме только по фактам."
        "\n4. НЕ ВКЛЮЧАЙ ссылки, поисковые подсказки или фразы о том, что \"в интернете есть информация\"."
        "\n5. НЕ ССЫЛАЙСЯ на посторонние источники информации."
        "\n6. Будь объективным и нейтральным."
        "\n\nЕсли ты видишь только одно сообщение, просто резюмируй его содержание. "
        "Не выдумывай ответы или реакции, которых нет в данных."
        "\n\nСосредоточься ТОЛЬКО на содержании сообщений, без дополнительных предположений."
        f"\n\n{history_context}Обнови саммери, учитывая следующий новый фрагмент чата:\n{chat_text}"
    )
    return _create_local_prompt(instruction) 