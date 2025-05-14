from typing import Optional
from .llm_interface import LLMInterface
from .api_llm import ApiLLM
from .local_llm import LocalLLM

class LLMFactory:
    @staticmethod
    def create_llm(
        llm_type: str,
        api_key: Optional[str] = None,
        folder_id: Optional[str] = None,
        local_model_name: Optional[str] = "models/mistral-instruct"
    ) -> LLMInterface:
        """
        Создает экземпляр LLM.
        
        Args:
            llm_type: Тип LLM для создания ("yandex" или "local").
            api_key: API ключ для доступа к YandexGPT (если llm_type="yandex").
            folder_id: Идентификатор каталога Yandex Cloud (если llm_type="yandex").
            local_model_name: Имя или путь к локальной модели (если llm_type="local").
            
        Returns:
            Экземпляр LLMInterface.
            
        Raises:
            ValueError: Если указан неизвестный тип LLM или отсутствуют необходимые параметры.
        """
        if llm_type == "yandex":
            if not api_key or not folder_id:
                raise ValueError("Для использования YandexGPT API необходимо указать api_key и folder_id")
            print(f"🏭 Создание Yandex LLM (ApiLLM) с folder_id: {folder_id[:5]}...")
            return ApiLLM(api_key=api_key, folder_id=folder_id)
        elif llm_type == "local":
            print(f"🏭 Создание Local LLM (LocalLLM) с моделью: {local_model_name}")
            return LocalLLM(model_name=local_model_name)
        else:
            raise ValueError(f"Неизвестный тип LLM: {llm_type}. Доступные типы: 'yandex', 'local'") 