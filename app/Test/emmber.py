# 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

from phi.agent import Agent, AgentKnowledge
from phi.vectordb.pgvector import PgVector
from phi.embedder.openai import OpenAIEmbedder
from phi.agent import Agent
from phi.model.openai.like import OpenAILike

# Create knowledge base
knowledge_base=AgentKnowledge(
    model=OpenAILike(
        id="yi-lightning",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    vector_db=PgVector(
        table_name="embeddings_table",
        embedder=OpenAIEmbedder(api_key="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"),
    ),
    # 2 references are added to the prompt
    num_documents=2,    
),

# Add information to the knowledge base
knowledge_base.load_text("The sky is blue")

# Add the knowledge base to the Agent
agent = Agent(knowledge_base=knowledge_base)
agent.print_response("Whats happening in France?", stream=True)


