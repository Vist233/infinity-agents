import os
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from config import API_KEY

# Get the API key from environment variables OR use the one from config.py
API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

# Define the Chater Agent using the specified DeepSeek model
chater_agent = Agent(
    model=DeepSeek(api_key=API, id="deepseek-reasoner"), # Use deepseek-chat as specified
    markdown=True,
    description="A general conversational AI assistant.",
    add_history_to_messages=True, # Maintain conversation history
)

# Example usage (for testing)
if __name__ == "__main__":
    from agno.utils.log import logger
    logger.info("Testing Chater Agent...")
    # Streaming example
    for chunk in chater_agent.run("Hello, how are you today?", stream=True):
        print(chunk, end="", flush=True)
    print("\n---")
    # Second message to test history
    for chunk in chater_agent.run("Tell me a joke.", stream=True):
        print(chunk, end="", flush=True)
