from pydantic import Field
from phi.agent import Agent
from phi.workflow import Workflow, RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.log import logger
from phi.agent import Agent
from phi.model.openai.like import OpenAILike
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.storage.agent.sqlite import SqlAgentStorage
# from phi.tools.file import FileTools
from .tools.fileChanged import FileTools
from .tools.shellChanged import ShellTools
from phi.utils.pprint import pprint_run_response
import os
from typing import Iterator
import uuid
from .StructureOutput import *

# Initialize processing workspace
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Get the API key from environment variables OR set your API key here
API_KEY = os.environ.get("YI_API_KEY", "1352a88fdd3844deaec9d7dbe4b467d5")

# 构建目标目录路径
processing_space_dir = os.path.join(parent_dir, 'ProcessingSpace')
database_dir = os.path.join(parent_dir, 'Database')
print(f"Parent directory: {parent_dir}")

# 创建目录并切换到该目录
if not os.path.exists(processing_space_dir):
    os.makedirs(processing_space_dir)
os.chdir(processing_space_dir)

# Generate a new session ID
user_session_id = str(uuid.uuid4())
os.makedirs(user_session_id, exist_ok=True)
os.chdir(user_session_id)

# Create database directory before initializing storage
os.makedirs(database_dir, exist_ok=True)

def create_storage(session_id: str, name: str) -> SqlAgentStorage:
    """Create SQLite storage for agents with proper session isolation"""
    return SqlAgentStorage(
        table_name=session_id,
        db_file = os.path.join(database_dir, f"{name}.db")
    )

# Initialize shared storage for tool executors
toolsTeamStorage = create_storage(user_session_id, "toolsTeam")

# User Interface Communicator Agent
userInterfaceCommunicator = Agent(
    storage=create_storage(user_session_id, "userInterfaceCommunicator"),
    model=OpenAILike(
        id="yi-medium",
        api_key=API_KEY,
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI assistant that converts user requests into the execute task list.",
    instruction=[
        "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libsm6, libxi6, python3.10.",
        "You just need to provide the task execution sequence and the corresponding command, you could use python or shell command.",
        "Break down complex tasks into smaller, executable steps and avoid generating tasks that require external software installation or system configuration.",
        "Don't check the tools and libraries, all the tools and libraries are available in the environment.",
    ],
    add_history_to_messages=True,
    markdown=True,
    arbitrary_types_allowed=True
)

# Task Splitter Agent
taskSpliter = Agent(
    storage=create_storage(user_session_id, "taskSpliter"),
    model=OpenAILike(
        id="yi-medium",
        api_key=API_KEY,
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI assistant that converts user requests into executable tasks.",
    instruction=[
        "For each task analyze and decide whether it needs Python (data processing, analysis, visualization, save the python file to local) or Shell (command line tools, file operations) execution.",
        "Provide clean, executable code snippets without installation or config steps.",
        "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, phidata, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libxext6, libsm6, libxi6, python3.10.",
        "Don't check the tools and libraries, all the tools and libraries are available in the environment.",
        "if the task is no task, return 'NO TASK' in your reply.",
    ],
    add_history_to_messages=False,
    arbitrary_types_allowed=True,
    response_model=taskSpliterAIOutput
)

# Python Executor Agent
pythonExcutor = Agent(
    storage=toolsTeamStorage,
    tools=[PythonTools(), FileTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key=API_KEY,
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="Executes Python-based tasks with focus on data processing, analysis and visualization",
    instruction=[
        "Focus on generating clean, efficient Python code.",
        "Always include proper error handling and input validation.",
        "Prefer pandas for data manipulation, matplotlib/seaborn for visualization.",
        "Use biopython for sequence analysis tasks.",
        "Return detailed execution results and any generated file paths."
    ],
    add_history_to_messages=False,
)

# Shell Executor Agent
shellExcutor = Agent(
    storage=toolsTeamStorage,
    tools=[ShellTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key=API_KEY,
        base_url="https://api.lingyiwanwu.com/v1"
    ),
    description="Executes shell commands for tools with proper error handling",
    instruction=[
        "You are a shell command execution specialist.",
        "Generate proper command lines for the tools you have.",
        "Always validate input files existence before execution.",
        "Include error handling and status checks.",
        "Use appropriate flags and parameters for each tool.",
        "Return command output and generated file paths.",
        "Commands should be provided as single, complete strings within a list, e.g., [\"command\"], rather than split into separate elements like [\"software\", \"parameters1\"].",
    ],
    add_history_to_messages=False
)

class CodeAIWorkflow(Workflow):
    user_interface: Agent = Field(default_factory=lambda: userInterfaceCommunicator)
    task_splitter: Agent = Field(default_factory=lambda: taskSpliter)
    pythonExcutor: Agent = Field(default_factory=lambda: pythonExcutor)
    shellExcutor: Agent = Field(default_factory=lambda: shellExcutor)

    def run(self, logs: list, user_input: str) -> Iterator[RunResponse]:
        logger.info(f"Processing request: {user_input}")
        logs.append(f"Processing request: {user_input}")
        
        # Get current directory contents
        list_current_dir = os.listdir('.')

        # Step 1: UI Communication with retries
        ui_response = None
        num_tries = 0
        while ui_response is None and num_tries < 3:
            try:
                num_tries += 1
                ui_response = self.user_interface.run(
                    f"Current directory files:\n{str(list_current_dir)}\nUser input:\n{user_input}"
                )
                if not ui_response or not ui_response.content:
                    logger.warning("Invalid UI response, retrying...")
                    logs.append(f"Invalid UI response, retrying...")
                    ui_response = None
            except Exception as e:
                logger.warning(f"UI communication error: {e}")
                logs.append(f"UI communication error: {e}")

        if not ui_response:
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content="Failed to process request through UI communicator"
            )
            return

        # Step 2: Task Splitting
        try:
            task_splitter_response = self.task_splitter.run(ui_response.content)
            if "NO TASK" in task_splitter_response.content:
                logger.info("No tasks to execute as per task splitter response.")
                logs.append(f"No tasks to execute as per task splitter response.")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="No tasks to execute"
                )
                return
            tasks_list = create_task_splitter_output(str(task_splitter_response.content))
            if not tasks_list:
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="No valid tasks found"
                )
                return
        except Exception as e:
            logger.error(f"Task splitting error: {e}")
            logs.append(f"Task splitting error: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Task splitting error: {str(e)}"
            )
            return

        # Step 3: Execute tasks with detailed output
        python_results = []
        shell_results = []
        execution_summary = []

        # Remove the last task if it is a separator
        if tasks_list and '=\'|\'' in tasks_list[-1]:
            tasks_list.pop()

        for idx, task in enumerate(tasks_list, 1):
            task_type = "Python" if 'pythonExecutor' in task else "Shell"
            executor = self.pythonExcutor if 'pythonExecutor' in task else self.shellExcutor
            
            execution_summary.append(f"\n--- Task {idx} ({task_type}) ---")
            execution_summary.append(f"Command: {task}")
            
            try:
                response = executor.run(task)
                if response and response.content:
                    result = f"Output: {response.content}"
                    if task_type == "Python":
                        python_results.append(result)
                    else:
                        shell_results.append(result)
                    execution_summary.append(result)
                    execution_summary.append("Status: Success")
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                execution_summary.append(error_msg)
                execution_summary.append("Status: Failed")

        # Prepare final output
        final_output = [
            "=== Task Execution Summary ===",
            f"Total tasks: {len(tasks_list)}",
            f"Python tasks: {len(python_results)}",
            f"Shell tasks: {len(shell_results)}",
            "\n=== Detailed Execution Log ===",
        ] + execution_summary

        yield RunResponse(
            run_id=self.run_id,
            event=RunEvent.workflow_completed,
            content="\n".join(final_output)
        )

def execute_workflow(session_id: str, input_text: str):
    """Execute the workflow with the given session ID and input text."""
    # Create the workflow with the session_id
    task_execution_workflow = CodeAIWorkflow(
        session_id=session_id,
        storage=SqlWorkflowStorage(
            table_name=session_id,
            db_file = os.path.join(database_dir, "workflow.db")
        ),
    )
    logs=[]
    # Run the workflow
    task_execution_results = task_execution_workflow.run(logs, user_input=input_text)

    # Print the results
    pprint_run_response(task_execution_results, markdown=True)

# Example usage
if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    input_text = "使用命令 cat \"Hello World\" > hello.txt"
    execute_workflow(session_id, input_text)







