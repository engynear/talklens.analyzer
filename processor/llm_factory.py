from typing import Optional
from .llm_interface import LLMInterface
from .api_llm import ApiLLM

class LLMFactory:
    @staticmethod
    def create_llm(
        api_key: str,
        folder_id: str
    ) -> LLMInterface:
        """
        Создает экземпляр LLM для работы с YandexGPT API
        
        Args:
            api_key: API ключ для доступа к YandexGPT
            folder_id: Идентификатор каталога Yandex Cloud
            
        Returns:
            Экземпляр LLMInterface
        """
        if not api_key or not folder_id:
            raise ValueError("Для использования YandexGPT API необходимо указать api_key и folder_id")
        return ApiLLM(api_key=api_key, folder_id=folder_id) 