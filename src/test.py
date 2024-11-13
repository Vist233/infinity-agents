from os import getenv
from phi.agent import Agent, RunResponse
from phi.model.openai.like import OpenAILike

# agent = Agent(
#     model=OpenAILike(
#         id="yi-lightning",
#         api_key="1352a88fdd3844deaec9d7dbe4b467d5",
#         base_url="https://api.lingyiwanwu.com/v1",
#     )
# )

# # Get the response in a variable
# # run: RunResponse = agent.run("Share a 2 sentence horror story.")
# # print(run.content)

# # Print the response in the terminal
# agent.print_response("Share a 2 sentence horror story.")


# from phi.agent import Agent

# agent = Agent(
#     model=OpenAILike(
#         id="yi-lightning",
#         api_key="1352a88fdd3844deaec9d7dbe4b467d5",
#         base_url="https://api.lingyiwanwu.com/v1",
#     ),
#     description="You are a famous short story writer asked to write for a magazine",
#     instructions=["You are a pilot on a plane flying from Hawaii to Japan."],
#     markdown=True,
#     debug_mode=True,
# )
# agent.print_response("Tell me a 2 sentence horror story.", stream=True)


from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.shell import ShellTools
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.python import PythonTools
from phi.tools.googlesearch import GoogleSearch

from datetime import datetime
sessionName = datetime.now()
sessionName = sessionName.strftime("%Y%m%d%H%M%S")

storage = SqlAgentStorage(
    # store sessions in the ai.sessions table
    table_name= sessionName,
    # db_file: Sqlite database file
    db_file="testDB/data.db",
)


agent = Agent(
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    tools=[ShellTools(), PythonTools()], 
    show_tool_calls=True, 
    markdown=True, 
    debug_mode=True, 
    stream=False, 
    add_history_to_messages=True,
    storage=storage)

# agent.print_response("Whats happening in France?", stream=True)

agent.print_response("what happened in Franch today?", markdown=True)

