from agno.agent import Agent
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.pubmed import PubmedTools
from config import API_KEY
from agno.models.deepseek import DeepSeek
import os

API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

paperai_agent = Agent(
    model=DeepSeek(api_key=API),
    tools=[ArxivTools(), PubmedTools(), DuckDuckGoTools()],
    instructions=[
        "You are an expert research assistant.",
        "Given a topic, your goal is to find relevant academic papers and articles using the available tools (Arxiv, PubMed, DuckDuckGo Search).",
        "First, use the tools to search for information on the topic. Prioritize Arxiv and PubMed for academic content.",
        "Synthesize the findings from the search results.",
        "Provide a concise summary of the most relevant information and papers found.",
        "Include links (URLs) to the papers or articles in your summary.",
        "Format your response in clear markdown.",
        "If no relevant information is found after searching, state that clearly.",
    ],
    markdown=True,
    add_history_to_messages=True,
)

