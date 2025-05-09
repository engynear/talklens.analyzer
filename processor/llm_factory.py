from typing import Optional
from .llm_interface import LLMInterface
from .local_llm import LocalLLM
from .api_llm import ApiLLM

class LLMFactory:
    @staticmethod
    def create_llm(
        use_api: bool = False, 
        api_url: Optional[str] = None, 
        api_key: Optional[str] = None,
        folder_id: Optional[str] = None,
        yandex_api: bool = False
    ) -> LLMInterface:
        """
        Создает экземпляр LLM в зависимости от настроек
        
        Args:
            use_api: Использовать ли API вместо локальной модели
            api_url: URL API для LLM (не требуется для YandexGPT)
            api_key: API ключ для доступа к LLM
            folder_id: Идентификатор каталога Yandex Cloud (только для YandexGPT)
            yandex_api: Использовать ли YandexGPT API
            
        Returns:
            Экземпляр LLMInterface
        """
        if use_api:
            if yandex_api:
                if not api_key or not folder_id:
                    raise ValueError("Для использования YandexGPT API необходимо указать api_key и folder_id")
                return ApiLLM(api_key=api_key, folder_id=folder_id)
            else:
                if not api_url or not api_key:
                    raise ValueError("Для использования API необходимо указать api_url и api_key")
                return ApiLLM(api_url=api_url, api_key=api_key)
        else:
            return LocalLLM() 