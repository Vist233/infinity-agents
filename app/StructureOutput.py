import asyncio
from typing import List, Optional

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.spinner import Spinner
from rich.text import Text
from pydantic import BaseModel, Field

from phi.agent import Agent, RunResponse
from phi.model.openai import OpenAIChat





class TaskSpliterAIOutput(BaseModel):
    thought: str = Field(..., description="Initial thought and analysis on the given task.")
    tasks: List[Dict[str, Any]] = Field(..., description="A list of tasks with details for each Tool AI to execute.")
   