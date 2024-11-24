from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import re

# class userInterfaceCommunicatorOutput(BaseModel):
#     response: str = Field(..., description="Response from the user interface.")
#     status: str = Field(..., description="Does user provided enough information for its tasks?. Use 'ready' if correct, otherwise 'not'.")

class task(BaseModel):
    id: str = Field(..., description="Unique identifier for the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    code_snippet: Optional[str] = Field(None, description="Code snippet to be analyzed. If no code is needed, it should be 'NO CODE'.")
    dependencies: Optional[str] = Field(default_factory=list, description="The dependencies. Only one tool can be specified:pythonExecutor, shellExecutor. If no dependency is needed it should be 'NO DEPENDENCY'.")
    result: Optional[str] = Field(None, description="Result of the task after execution.")
    separator: str = Field(..., description="only return '|'")

class taskSpliterAIOutput(BaseModel):
    tasks: List[task] = Field(..., description="A list of up to five tasks with details for each Tool AI to execute. If not a task, return 'NOT A TASK'.")

class outputCheckerOutput(BaseModel):
    thought: str = Field(..., description="Initial thought and analysis on the given task.")
    checkResult: str = Field(..., description="Result of checking the output. Use 'pass' if correct, otherwise 'fail'.")
    summary: str = Field(..., description="Summary of the output.")
    

import json
import re


def create_task_splitter_output(tasks):
    if isinstance(tasks, str):
        tasks = tasks.split('separator')
    return tasks

def create_output_checker(thought, check_result, summary):
    return {
        "thought": thought,
        "checkResult": check_result,
        "summary": summary
    }


def parse_output_checker_to_dict(output_str):
    try:
        # First try parsing as JSON
        return json.loads(output_str)
    except json.JSONDecodeError:
        # Fallback to regex parsing for legacy format
        pattern = r"outputCheckerOutput\(thought='(.*?)',\s*checkResult='(.*?)',\s*summary='(.*?)'\)"
        match = re.search(pattern, output_str, re.DOTALL)
        
        if match:
            thought, checkResult, summary = match.groups()
            return create_output_checker(thought, checkResult, summary)
        return {}
