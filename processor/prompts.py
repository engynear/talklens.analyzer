"""
Модуль содержит промпты для запросов к LLM
"""

def compliments_prompt(chat_text: str) -> str:
    """Промпт для подсчета комплиментов"""
    return f"""
Проанализируй следующий чат и подсчитай, сколько комплиментов сделал каждый собеседник.

Чат:
{chat_text}

Ответь строго в формате JSON. Пример:
{{
  "A": 3,
  "B": 1
}}
""".strip()

def engagement_prompt(chat_text: str, historical_summary: str = "") -> str:
    """Промпт для определения уровня вовлеченности"""
    history_context = f"Историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    
    return f"""
{history_context}Проанализируй следующий новый фрагмент чата и определи уровень вовлечённости каждого участника от 0 до 100%.
Учитывай как историческое саммери, так и новые сообщения при расчете.

Новые сообщения чата:
{chat_text}

Ответь строго в формате JSON. Пример:
{{
  "A": 82.5,
  "B": 67.0
}}
""".strip()

def attachment_prompt(chat_text: str, historical_summary: str = "") -> str:
    """Промпт для определения типа привязанности"""
    history_context = f"Историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    
    return f"""
{history_context}Проанализируй следующий новый фрагмент чата и определи тип привязанности каждого участника (безопасный, тревожный, избегающий, дезорганизованный) и уверенность в этом определении от 0 до 100%.
Учитывай как историческое саммери, так и новые сообщения при анализе.

Новые сообщения чата:
{chat_text}

Ответь строго в формате JSON. Пример:
{{
  "A": {{"type": "безопасный", "confidence": 75.0}},
  "B": {{"type": "тревожный", "confidence": 60.0}}
}}
""".strip()

def recommendations_prompt(chat_text: str, historical_summary: str, user_id: str) -> str:
    """Промпт для генерации рекомендаций"""
    history_context = f"Историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    
    return f"""
{history_context}Проанализируй следующий новый фрагмент чата и сгенерируй рекомендации по общению для пользователя {user_id}.
Учитывай как историческое саммери, так и новые сообщения при составлении рекомендаций.

Новые сообщения чата:
{chat_text}

Дай 3-5 конкретных рекомендаций, как пользователю {user_id} улучшить коммуникацию.
""".strip()

def summary_prompt(chat_text: str, historical_summary: str = "") -> str:
    """Промпт для обновления саммери"""
    history_context = f"Предыдущее историческое саммери:\n{historical_summary}\n\n" if historical_summary else ""
    
    return f"""
{history_context}Обнови историческое саммери диалога, учитывая следующий новый фрагмент чата.
Саммери должно содержать основные темы разговора, ключевые моменты, эмоциональный фон и динамику отношений.

Новые сообщения чата:
{chat_text}

Верни только текст обновленного саммери, которое можно будет использовать как контекст для будущего анализа.
""".strip()

def legacy_analysis_prompt(chat_text: str) -> str:
    """Устаревший промпт для анализа батча сообщений (обратная совместимость)"""
    return f"""
Проанализируй следующий чат и оцени:
- Сколько комплиментов сделал каждый собеседник?
- Какой уровень вовлечённости у каждого собеседника (от 0 до 100)?

Чат:
{chat_text}

Ответь строго в формате JSON. Пример:
{{
  "A": {{"compliments": 3, "engagement_score": 82.5}},
  "B": {{"compliments": 1, "engagement_score": 67.0}}
}}
""".strip()

def format_mistral_prompt(instruction: str) -> str:
    """Форматирует промпт для модели Mistral Instruct"""
    return f"<s>[INST] {instruction} [/INST]" 