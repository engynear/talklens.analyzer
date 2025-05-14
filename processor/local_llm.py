from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import re

from .llm_interface import LLMInterface
from . import local_prompts

class LocalLLM(LLMInterface):
    def __init__(self, model_name: str = "models/mistral-instruct"):
        print("🔁 Загружаем локальную модель...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        print("✅ Локальная модель загружена.")

    def _format_chat_history(self, messages: List[Dict[str, Any]]) -> str:
        """
        Форматирует историю чата в строку.
        """
        return "\\n".join([f"{m['SenderId']}: {m['MessageText']}" for m in messages])

    def _make_request(self, prompt_text: str, max_retries: int = 3) -> str:
        """
        Выполняет запрос к локальной модели.
        """
        inputs = self.tokenizer(prompt_text, return_tensors="pt", return_attention_mask=True).to(self.model.device)

        for attempt in range(max_retries):
            try:
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256, # Можно настроить
                    do_sample=False,    # Для более детерминированного вывода
                    temperature=0.0,    # Для более детерминированного вывода
                    eos_token_id=self.tokenizer.eos_token_id
                )
                decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                
                # Удаляем часть промпта из ответа, если модель его повторяет
                # Это характерно для instruct-моделей
                if decoded.startswith(prompt_text):
                    decoded = decoded[len(prompt_text):].strip()
                
                # Ищем закрывающий тег [/INST] и берем текст после него
                inst_match = re.search(r"\[/INST\](.*)", decoded, re.DOTALL | re.IGNORECASE)
                if inst_match:
                    decoded = inst_match.group(1).strip()
                    
                return decoded
            except Exception as e:
                print(f"❌ Ошибка при генерации ответа локальной моделью (попытка {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return ""
        return ""

    def _clean_markdown_and_extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Очищает текст от Markdown и извлекает JSON.
        """
        if not text:
            print("❌ Пустой текст для извлечения JSON")
            return None

        # Удаляем ```json ... ``` и ``` ... ```
        cleaned_text = re.sub(r'```(?:json|)\\n?(.*?)\\n?```', r'\\1', text, flags=re.DOTALL)
        cleaned_text = re.sub(r'`(?!`)(.*?)`', r'\\1', cleaned_text) # Одиночные тики, не двойные

        # Пытаемся найти JSON объект в тексте
        # Сначала ищем самый внешний JSON объект
        match = re.search(r'{\s*".*?":.*?}', cleaned_text, re.DOTALL)
        if not match:
            # Если не нашли, попробуем найти без строгого начала/конца строки, на случай если есть префикс/суффикс
            match = re.search(r'({.*?})', cleaned_text, re.DOTALL)

        if match:
            json_text = match.group(0)
            try:
                # Дополнительная очистка перед парсингом
                # Убираем возможные комментарии в стиле Python/JavaScript, если они попали в строку
                json_text = re.sub(r'//.*?\\n', '\\n', json_text)
                json_text = re.sub(r'#.*?\\n', '\\n', json_text)
                
                # Убираем возможные управляющие символы в начале/конце, которые могут мешать
                json_text = json_text.strip().strip(',').strip()

                # Проверяем наличие и корректность кавычек у ключей и строковых значений
                # Это очень упрощенная проверка, но может помочь в некоторых случаях
                json_text = re.sub(r'(?<![\\])"\s*([a-zA-Z0-9_]+)\s*":', r'"\\1":', json_text) # Ключи
                
                data = json.loads(json_text)
                return data
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка декодирования JSON из текста: {json_text}. Ошибка: {e}")
                # Попытка исправить распространенные ошибки, например, одинарные кавычки вместо двойных
                try:
                    corrected_json_text = json_text.replace("'", '"')
                    # Исправление для случаев, когда числовые ключи без кавычек
                    corrected_json_text = re.sub(r'([{,]\s*)(\d+)(\s*:)', r'\\1"\\2"\\3', corrected_json_text)
                    data = json.loads(corrected_json_text)
                    print("✅ JSON успешно извлечен после исправления кавычек/числовых ключей.")
                    return data
                except json.JSONDecodeError:
                    print(f"❌ Повторная ошибка декодирования JSON после исправления: {corrected_json_text}")
                    return None
        else:
            print(f"❌ JSON не найден в тексте: {cleaned_text[:200]}...")
            return None

    def count_compliments(self, messages: List[Dict[str, Any]], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        chat_text = self._format_chat_history(messages)
        prompt = local_prompts.compliments_prompt(chat_text)
        response_text = self._make_request(prompt, max_retries)
        return self._clean_markdown_and_extract_json(response_text)

    def calculate_engagement(self, messages: List[Dict[str, Any]], historical_summary: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        chat_text = self._format_chat_history(messages)
        user_ids = list(set(m['SenderId'] for m in messages)) # Получаем уникальные ID
        prompt = local_prompts.engagement_prompt(chat_text, user_ids, historical_summary)
        response_text = self._make_request(prompt, max_retries)
        return self._clean_markdown_and_extract_json(response_text)

    def calculate_attachment(self, messages: List[Dict[str, Any]], historical_summary: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        chat_text = self._format_chat_history(messages)
        user_ids = list(set(m['SenderId'] for m in messages))
        prompt = local_prompts.attachment_prompt(chat_text, user_ids, historical_summary)
        response_text = self._make_request(prompt, max_retries)
        return self._clean_markdown_and_extract_json(response_text)

    def generate_recommendations(self, messages: List[Dict[str, Any]], historical_summary: str, user_id: str, max_retries: int = 3) -> Optional[str]:
        chat_text = self._format_chat_history(messages)
        prompt = local_prompts.recommendations_prompt(chat_text, historical_summary, user_id)
        response_text = self._make_request(prompt, max_retries)
        # Рекомендации - это просто текст, не JSON
        return response_text if response_text else None

    def update_summary(self, messages: List[Dict[str, Any]], historical_summary: Optional[str] = None, max_retries: int = 3) -> Optional[str]:
        chat_text = self._format_chat_history(messages)
        prompt = local_prompts.summary_prompt(chat_text, historical_summary)
        response_text = self._make_request(prompt, max_retries)
        # Саммери - это просто текст, не JSON
        return response_text if response_text else None 