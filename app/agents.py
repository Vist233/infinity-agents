import os
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.pubmed import PubmedTools
from agno.tools.arxiv import ArxivTools
from agno.utils.pprint import pprint_run_response

API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'your API key here')

paperai_agent = Agent(
    model=DeepSeek(api_key=API_KEY),
    tools=[PubmedTools(), ArxivTools()],
    instructions=[
        "You are an expert research assistant.",
        "Given a topic, your goal is to find relevant academic papers and articles using the available tools (PubMed).",
        "First, use the tools to search for information on the topic. Prioritize PubMed for academic content.",
        "Synthesize the findings from the search results.",
        "Provide a concise summary of the most relevant information and papers found.",
        "Include links (URLs) to the papers or articles in your summary.",
        "Format your response in clear markdown.",
        "If no relevant information is found after searching, state that clearly.",
    ],
    markdown=True,
    description="PaperAI: Searches PubMed for academic papers and summarizes them.",
    debug_mode=True,
)

chater_agent = Agent(
    model=DeepSeek(api_key=API_KEY, id="deepseek-reasoner"),
    markdown=True,
    description="Chater: An academic AI assistant.",
)

if __name__ == "__main__":
    while True:
        user_input = input("Enter a research topic (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        pprint_run_response(paperai_agent.run(user_input))
    