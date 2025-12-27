"""LangChain Google Gemini integration."""
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings

logger = logging.getLogger(__name__)

# Standard LangChain Gemini implementation
gemini_llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.gemini_api_key,
    temperature=settings.agent_temperature,
    max_output_tokens=settings.agent_max_tokens,
)
