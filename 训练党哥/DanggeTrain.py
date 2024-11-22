from phi.agent import Agent
from phi.model.openai.like import OpenAILike
from phi.playground import Playground, serve_playground_app
from phi.tools.googlesearch import GoogleSearch
from phi.tools.baidusearch import BaiduSearch
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.tools.pubmed import PubmedTools
from phi.storage.agent.sqlite import SqlAgentStorage
import uuid




userInterfaceCommunicatorStorage = SqlAgentStorage(
            table_name="This is DangGe",
            db_file="./ThisIsDangGe.db"
)
            
userInterfaceCommunicator = Agent(
    storage = userInterfaceCommunicatorStorage,
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI assistant that converts user requests into executable bioinformatics tasks.",
    instruction=["learn"
    ],
    tools=[ShellTools()],
    add_history_to_messages=True,
    markdown=True,
    debug_mode=True,
)