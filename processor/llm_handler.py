from .llm_factory import LLMFactory
from config import USE_API, API_URL, API_KEY, YANDEX_API, FOLDER_ID


llm = LLMFactory.create_llm(
    use_api=USE_API,
    api_url=API_URL,
    api_key=API_KEY,
    folder_id=FOLDER_ID,
    yandex_api=YANDEX_API
)


def count_compliments(messages, max_retries=3):
    return llm.count_compliments(messages, max_retries)

def calculate_engagement(messages, historical_summary="", previous_engagement=None, max_retries=3):
    return llm.calculate_engagement(messages, historical_summary, previous_engagement, max_retries)

def calculate_attachment(messages, historical_summary="", previous_attachments=None, max_retries=3):
    return llm.calculate_attachment(messages, historical_summary, previous_attachments, max_retries)

def generate_recommendations(messages, historical_summary="", user_id="", max_retries=3):
    return llm.generate_recommendations(messages, historical_summary, user_id, max_retries)

def update_summary(messages, historical_summary=None, max_retries=3):
    return llm.update_summary(messages, historical_summary, max_retries)
def analyze_batch(messages, max_retries=3):
    """
    Устаревший метод, оставлен для обратной совместимости
    """
    return llm.analyze_batch(messages, max_retries)

