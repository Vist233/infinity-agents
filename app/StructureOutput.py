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
    dependencies: Optional[str] = Field(default_factory=list, description="The dependencies. Only one tool can be specified: paperSearcher, webSearcher, calculatorAI, pythonExecutor, shellExecutor. If no dependency is needed it should be 'NO DEPENDENCY'.")
    result: Optional[str] = Field(None, description="Result of the task after execution.")

class taskSpliterAIOutput(BaseModel):
    tasks: List[task] = Field(..., description="A list of up to five tasks with details for each Tool AI to execute. If not a task, return 'NOT A TASK'.")

class outputCheckerOutput(BaseModel):
    thought: str = Field(..., description="Initial thought and analysis on the given task.")
    checkResult: str = Field(..., description="Result of checking the output. Use 'pass' if correct, otherwise 'fail'.")
    summary: str = Field(..., description="Summary of the output.")
    

def parse_tasks_to_list(tasks_str):
    pattern = r"task\(id='(.*?)',\s*description='(.*?)',\s*code_snippet=(.*?),\s*dependencies=\[(.*?)\],\s*result=(.*?),\s*separator='\|'\)"
    matches = re.findall(pattern, tasks_str, re.DOTALL)
    
    tasks_list = []
    for match in matches:
        id, description, code_snippet, dependencies, result = match
        dependencies = [dep.strip().strip("'") for dep in dependencies.split(',') if dep.strip()]
        task_dict = {
            "id": id,
            "description": description,
            "code_snippet": code_snippet.strip("None'\""),
            "dependencies": dependencies,
            "result": result.strip("None'\"")
        }
        tasks_list.append(str(task_dict))
    
    return tasks_list

def parse_output_checker_to_dict(output_str):
    pattern = r"outputCheckerOutput\(thought='(.*?)',\s*checkResult='(.*?)',\s*summary='(.*?)'\)"
    match = re.search(pattern, output_str, re.DOTALL)
    
    if match:
        thought, checkResult, summary = match.groups()
        output_dict = {
            "thought": thought,
            "checkResult": checkResult,
            "summary": summary
        }
        return output_dict
    else:
        return {}