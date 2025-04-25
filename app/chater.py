import os
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from config import API_KEY

API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

chater_agent = Agent(
    model=DeepSeek(api_key=API, id="deepseek-reasoner"),
    markdown=True,
    description="A general conversational AI assistant.",
    add_history_to_messages=True,
)
