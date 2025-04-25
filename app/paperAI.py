from agno.agent import Agent
from agno.utils.log import logger
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.pubmed import PubmedTools
from config import API_KEY
from agno.models.deepseek import DeepSeek
import os

# Get the API key from environment variables OR set your API key here
API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

# Define the PaperAI Agent
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
    markdown=True,  # Ensure markdown output is enabled
    add_history_to_messages=True,
    # Removed response_model as the agent will generate free-form summary
)

# Example usage (for testing, not used by app.py directly this way)
if __name__ == "__main__":
    topic = "Recent advancements in CRISPR gene editing for cancer therapy"
    logger.info(f"Testing PaperAI with topic: {topic}")

    # Non-streaming example
    # result = paperai_agent.run(topic)
    # print(result)

    # Streaming example
    for chunk in paperai_agent.run(topic, stream=True):
        print(chunk, end="", flush=True)

