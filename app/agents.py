import os
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.pubmed import PubmedTools

API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'your API key here')

paperai_agent = Agent(
    model=DeepSeek(api_key=API_KEY),
    tools=[PubmedTools()],
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
    add_history_to_messages=False,
    description="PaperAI: Searches PubMed for academic papers and summarizes them.",
)

chater_agent = Agent(
    model=DeepSeek(api_key=API_KEY, id="deepseek-reasoner"),
    markdown=True,
    description="Chater: A general conversational AI assistant.",
    add_history_to_messages=True,
)

if __name__ == "__main__":
    paperai_agent.run()
    