import pandas as pd
from langchain_community.llms import Ollama
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from src.utils.config import settings
from src.services.data_loader import data_loader

class LLMService:
    def __init__(self):
        self.llm = Ollama(model=settings.LLM_MODEL, base_url=settings.LLM_BASE_URL, temperature=0)
        self.agent = self._create_agent()
        
    def _create_agent(self):
        df = data_loader.get_dataframe()
        return create_pandas_dataframe_agent(
            self.llm, 
            df, 
            verbose=True, 
            allow_dangerous_code=True,
            handle_parsing_errors=True
        )

    def query(self, question: str) -> str:
        try:
            response = self.agent.invoke(question)
            return str(response.get("output", response))
        except Exception as e:
            return f"Error executing query: {str(e)}"

llm_service = LLMService()
