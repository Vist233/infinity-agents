from typing import List
from rich.pretty import pprint  # noqa
from pydantic import BaseModel, Field
from phi.agent import Agent, RunResponse  # noqa
from phi.model.openai import OpenAIChat
from phi.agent import Agent
from phi.model.openai.like import OpenAILike
from phi.playground import Playground, serve_playground_app
from phi.tools.googlesearch import GoogleSearch
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.tools.pubmed import PubmedTools
from phi.storage.agent.sqlite import SqlAgentStorage
import uuid

class MovieScript(BaseModel):
    setting: str = Field(..., description="Provide a nice setting for a blockbuster movie.")
    ending: str = Field(..., description="Ending of the movie. If not available, provide a happy ending.")
    genre: str = Field(
        ..., description="Genre of the movie. If not available, select action, thriller or romantic comedy."
    )
    name: str = Field(..., description="Give a name to this movie")
    characters: List[str] = Field(..., description="Name of characters for this movie.")
    storyline: str = Field(..., description="3 sentence storyline for the movie. Make it exciting!")


# Agent that uses JSON mode
json_mode_agent = Agent(
    model=OpenAILike(
        id="yi-medium",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="You write movie scripts.",
    response_model=MovieScript,
    debug_mode=True,
    arbitrary_types_allowed=True,
)

# Agent that uses structured outputs
# structured_output_agent = Agent(
#     model=OpenAILike(
#         id="yi-lightning",
#         api_key="1352a88fdd3844deaec9d7dbe4b467d5",
#         base_url="https://api.lingyiwanwu.com/v1",
#     ),
#     description="You write movie scripts.",
#     response_model=MovieScript,
#     structured_outputs=True, # This is the only difference
#     debug_mode=True
# )


# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)
# structured_output_response: RunResponse = structured_output_agent.run("New York")
# pprint(structured_output_response.content)

json_mode_agent.print_response("New York")
# structured_output_agent.print_response("New York")
