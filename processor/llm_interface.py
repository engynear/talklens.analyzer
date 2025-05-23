from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMInterface(ABC):
    @abstractmethod
    def count_compliments(self, messages: List[Dict[str, Any]], max_retries: int = 3) -> Dict[str, Any]:
        """
        Подсчитывает количество комплиментов в сообщениях
        
        Args:
            messages: Список сообщений для анализа
            max_retries: Максимальное количество попыток анализа
            
        Returns:
            Dict с количеством комплиментов для каждого отправителя или None в случае ошибки
        """
        pass
        
    @abstractmethod
    def calculate_engagement(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Определяет уровень вовлеченности на основе истории и нового батча
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Историческое саммери диалога
            max_retries: Максимальное количество попыток анализа
            
        Returns:
            Dict с уровнем вовлеченности для каждого отправителя или None в случае ошибки
        """
        pass
        
    @abstractmethod
    def calculate_attachment(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Определяет тип привязанности и уверенность на основе истории и нового батча
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Историческое саммери диалога
            max_retries: Максимальное количество попыток анализа
            
        Returns:
            Dict с типом привязанности и уверенностью или None в случае ошибки
        """
        pass
        
    @abstractmethod
    def generate_recommendations(
        self, 
        messages: List[Dict[str, Any]], 
        historical_summary: str,
        user_id: str,
        max_retries: int = 3
    ) -> str:
        """
        Генерирует рекомендации по общению для пользователя
        
        Args:
            messages: Список сообщений для анализа
            historical_summary: Историческое саммери диалога
            user_id: ID пользователя, которому нужны рекомендации
            max_retries: Максимальное количество попыток анализа
            
        Returns:
            Строка с рекомендациями или None в случае ошибки
        """
        pass
        
    @abstractmethod
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
        pass 