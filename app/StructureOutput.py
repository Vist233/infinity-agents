import asyncio
from typing import Any, Dict, List, Optional

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
    tasks: List[str] = Field(..., description="A list of tasks with details for each Tool AI to execute. If not a task, return 'NOT A TASK'.")

class outputCheckerOutput(BaseModel):
    thought: str = Field(..., description="Initial thought and analysis on the given task.")
    checkResult: str = Field(..., description="The result of checking the output. If the output is correct, this should be 'pass'. Otherwise, it should be 'fail'.")
    summary: str = Field(..., description="A summary of output.")
    
