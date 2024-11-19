from phi.agent import Agent
from baidu_search_tool import BaiduSearch
from phi.model.openai.like import OpenAILike

agent = Agent(
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    tools=[BaiduSearch()],
    description="You are a news agent that helps users find the latest news.",
    instructions=[
        "Given a topic by the user, respond with 4 latest news items about that topic.",
        "Search for 10 news items and select the top 4 unique items.",
        "Search in English and in French.",
    ],
    show_tool_calls=True
    )

agent.print_response("请你告诉我最近法国发生了什么事情", markdown=True)
