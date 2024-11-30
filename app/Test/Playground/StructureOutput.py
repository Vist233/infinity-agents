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


class task(BaseModel):
    id: str = Field(..., description="Unique identifier for the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    code_snippet: Optional[str] = Field(None, description="Code snippet to be analyzed.")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs that this task depends on.")
    result: Optional[str] = Field(None, description="The Result of the task should be after execution.")
    separator: str = Field(..., description="only respond |")


class taskSpliterAIOutput(BaseModel):
    tasks: List[task] = Field(..., description="A list of tasks with details for each Tool AI to execute. If not a task, return 'NOT A TASK'.")

class outputCheckerOutput(BaseModel):
    thought: str = Field(..., description="Initial thought and analysis on the given task.")
    checkResult: str = Field(..., description="The result of checking the output. If the output is correct, this should be 'pass'. Otherwise, it should be 'fail'.")
    summary: str = Field(..., description="A summary of output.")
    
