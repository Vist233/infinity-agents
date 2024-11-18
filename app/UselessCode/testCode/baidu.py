from phi.agent import Agent
from baidu_search_tool import baidusearch
from phi.model.openai.like import OpenAILike

agent = Agent(
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    tools=[baidusearch()],
    show_tool_calls=True
    )

agent.print_response("What's happening in France?", markdown=True)
