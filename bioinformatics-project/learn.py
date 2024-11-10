from os import getenv
from phi.agent import Agent, RunResponse
from phi.model.openai.like import OpenAILike

agent = Agent(
    model=OpenAILike(
        id="yi-lightning",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)



# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story.")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")
