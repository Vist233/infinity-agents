from typing import List, Optional
from pydantic import BaseModel, Field


# Define the task model
class task(BaseModel):
    id: str = Field(..., description="Unique identifier for the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    code_snippet: Optional[str] = Field(None, description="Code snippet to be analyzed. If no code is needed, it should be 'NO CODE'.")
    dependencies: Optional[str] = Field(default_factory=list, description="The dependencies. Only one tool can be specified:pythonExecutor, shellExecutor. If no dependency is needed it should be 'NO DEPENDENCY'.")
    result: Optional[str] = Field(None, description="Result of the task after execution.")
    separator: str = Field(..., description="only return '|'")

# Define the task splitter AI output model
class taskSpliterAIOutput(BaseModel):
    tasks: List[task] = Field(..., description="A list of up to five tasks with details for each Tool AI to execute. If not a task, return 'NOT A TASK'.")

# Function to create task splitter output
def create_task_splitter_output(tasks):
    if isinstance(tasks, str):
        tasks = tasks.split('separator')
    return tasks

