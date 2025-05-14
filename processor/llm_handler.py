from .llm_factory import LLMFactory
from config import API_KEY, FOLDER_ID, LLM_TYPE, LOCAL_MODEL_NAME


llm = LLMFactory.create_llm(
    llm_type=LLM_TYPE,
    api_key=API_KEY,
    folder_id=FOLDER_ID,
    local_model_name=LOCAL_MODEL_NAME
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

