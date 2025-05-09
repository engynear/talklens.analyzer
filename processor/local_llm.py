from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
import json
from typing import List, Dict, Any, Optional
from .llm_interface import LLMInterface
from .prompts import (
    compliments_prompt,
    engagement_prompt,
    attachment_prompt,
    recommendations_prompt,
    summary_prompt,
    legacy_analysis_prompt,
    format_mistral_prompt
)

class LocalLLM(LLMInterface):
    def __init__(self, model_name: str = "models/mistral-instruct"):
        print("🔁 Загружаем модель...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        print("✅ Модель загружена.")

    def _generate_response(self, prompt: str, max_retries: int = 3) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=True).to(self.model.device)
        
        for attempt in range(max_retries):
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
                temperature=0.0,
                eos_token_id=self.tokenizer.eos_token_id
            )

            decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            print(f"🧠 Попытка
            return decoded
            
        return ""

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            json_text = re.search(r"\{.*\}", text, re.DOTALL).group()
            return json.loads(json_text)
        except Exception as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            return None

    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        return "\n".join([f"{m['SenderId']}: {m['MessageText']}" for m in messages])

    def count_compliments(self, messages: List[Dict[str, Any]], max_retries: int = 3) -> Dict[str, Any]:
        chat_text = self._format_messages(messages)
        instruction = compliments_prompt(chat_text)
        prompt = format_mistral_prompt(instruction)
        response = self._generate_response(prompt, max_retries)
        return self._extract_json(response)

    def calculate_engagement(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        chat_text = self._format_messages(messages)
        instruction = engagement_prompt(chat_text, historical_summary)
        prompt = format_mistral_prompt(instruction)
        response = self._generate_response(prompt, max_retries)
        return self._extract_json(response)

    def calculate_attachment(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        chat_text = self._format_messages(messages)
        instruction = attachment_prompt(chat_text, historical_summary)
        prompt = format_mistral_prompt(instruction)
        response = self._generate_response(prompt, max_retries)
        return self._extract_json(response)

    def generate_recommendations(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        user_id: str,
        max_retries: int = 3
    ) -> str:
        chat_text = self._format_messages(messages)
        instruction = recommendations_prompt(chat_text, historical_summary, user_id)
        prompt = format_mistral_prompt(instruction)
        response = self._generate_response(prompt, max_retries)
        

        return response

    def update_summary(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        chat_text = self._format_messages(messages)
        instruction = summary_prompt(chat_text, historical_summary)
        prompt = format_mistral_prompt(instruction)
        response = self._generate_response(prompt, max_retries)
        
        return response

    def analyze_batch(self, messages: List[Dict[str, Any]], max_retries: int = 3) -> Dict[str, Any]:

        chat_text = self._format_messages(messages)
        instruction = legacy_analysis_prompt(chat_text)
        prompt_text = format_mistral_prompt(instruction)
        
        inputs = self.tokenizer(prompt_text, return_tensors="pt", return_attention_mask=True).to(self.model.device)

        for attempt in range(max_retries):
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
                temperature=0.0,
                eos_token_id=self.tokenizer.eos_token_id
            )

            decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

            print(f"🧠 Попытка

            try:
                json_text = re.search(r"\{.*\}", decoded, re.DOTALL).group()
                return json.loads(json_text)
            except Exception as e:
                print(f"❌ Ошибка парсинга JSON: {e}")

        return None 