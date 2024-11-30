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
from phi.tools.file import FileTools
import shutil
from phi.utils.pprint import pprint_run_response
import os
from typing import Iterator
import uuid
import StructureOutput






# Initialize processing workspace
if not os.path.exists('./ProcessingSpace'):
    os.makedirs('./ProcessingSpace')
os.chdir('./ProcessingSpace/')

# Get the user inputs
# session_input = input("Session ID (press Enter to generate new): ").strip()

# while(1):
#     if os.path.isdir(session_input):
#         user_session_id = session_input
#         break
#     elif session_input == "":
#         user_session_id = str(uuid.uuid4())
#         break
#     else:
#         user_session_id = input("session ID invalied, Please reenter the session ID (press Enter to generate new): ")


user_session_id = str(uuid.uuid4())
os.makedirs(user_session_id, exist_ok=True)
os.chdir(user_session_id)





def create_storage(session_id: str, name: str) -> SqlAgentStorage:
    """Create SQLite storage for agents with proper session isolation"""
    return SqlAgentStorage(
        table_name=session_id,
        db_file=f"./../DataBase/{name}.db"  # Changed to use workflow database
    )

# Initialize shared storage for tool executors
toolsTeamStorage = create_storage(user_session_id, "toolsTeam")

# User Interface Communicator Agent
userInterfaceCommunicator = Agent(
    storage=create_storage(user_session_id, "userInterfaceCommunicator"),
    model=OpenAILike(
        id="yi-medium",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI assistant that converts user requests into the excute task list.",
    instruction=[
        "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libsm6, libxi6, python3.10.",
        "You just need to provide the task Task execution sequence and the corresponding command, you could use python or shell command.",
        "Avoid generating tasks that require external software installation or system configuration.",
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
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="split the task into python and shell tasks",
    instruction=[
        "You are a specialized task analyzer for bioinformatics workflows, python, shell.",
        # "Available tools include: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, and basic Unix tools.",
        "For each task analyze and decide whether it needs Python (data processing, analysis, visualization) or Shell (command line tools, file operations) execution.",
        "Provide clean, executable code snippets without installation or config steps.",
    ],
    add_history_to_messages=True,
    arbitrary_types_allowed=True,
    response_model=StructureOutput.taskSpliterAIOutput
)

pythonExcutor = Agent(
    storage=toolsTeamStorage,
    tools=[PythonTools(), FileTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="Executes Python-based bioinformatics tasks with focus on data processing, analysis and visualization",
    instruction=[
        "Focus on generating clean, efficient Python code.",
        "Always include proper error handling and input validation.",
        "Prefer pandas for data manipulation, matplotlib/seaborn for visualization.",
        "Use biopython for sequence analysis tasks.",
        "Return detailed execution results and any generated file paths."
    ],
    add_history_to_messages=False,
)

shellExcutor = Agent(
    storage=toolsTeamStorage,
    tools=[ShellTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1"
    ),
    description="Executes shell commands for bioinformatics tools with proper error handling",
    instruction=[
        "You are a shell command execution specialist.",
        "Generate proper command lines for bioinformatics tools.",
        "Always validate input files existence before execution.",
        "Include error handling and status checks.",
        "Use appropriate flags and parameters for each tool.",
        "Return command output and generated file paths."
    ],
    add_history_to_messages=False
)

"""
    This should be workflow description
"""

class CodeAIWorkflow(Workflow):
    def __init__(self, session_id: str, storage: SqlWorkflowStorage):
        super().__init__(session_id=session_id, storage=storage)
        self.user_interface = Agent(
            model=OpenAILike(
                id="yi-medium",
                api_key="1352a88fdd3844deaec9d7dbe4b467d5",
                base_url="https://api.lingyiwanwu.com/v1",
            ),
            instructions=[
                "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libsm6, libxi6, python3.10.",
                "You just need to provide the task Task execution sequence and the corresponding command, you could use python or shell command.",
                "Avoid generating tasks that require external software installation or system configuration.",
                "Don't check the tools and libraries, all the tools and libraries are available in the environment.",
            ],
        )

        self.task_splitter = Agent(
            model=OpenAILike(
                id="yi-medium",
                api_key="1352a88fdd3844deaec9d7dbe4b467d5",
                base_url="https://api.lingyiwanwu.com/v1",
            ),
            instructions=[
                "You are a specialized task analyzer for bioinformatics workflows, python, shell.",
                "For each task analyze and decide whether it needs Python or Shell execution.",
                "Provide clean, executable code snippets without installation or config steps.",
            ],
            response_model=StructureOutput.taskSpliterAIOutput
        )

        tools_storage = SqlAgentStorage(
            table_name=session_id,
            db_file=f"./Database/toolsTeam.db"
        )

        self.python_executor = Agent(
            storage=tools_storage,
            tools=[PythonTools(), FileTools()],
            model=OpenAILike(
                id="yi-large-fc",
                api_key="1352a88fdd3844deaec9d7dbe4b467d5",
                base_url="https://api.lingyiwanwu.com/v1",
            ),
            instructions=[
                "Focus on generating clean, efficient Python code.",
                "Always include proper error handling and input validation.",
                "Return detailed execution results and any generated file paths."
            ],
        )

        self.shell_executor = Agent(
            storage=tools_storage,
            tools=[ShellTools()],
            model=OpenAILike(
                id="yi-large-fc",
                api_key="1352a88fdd3844deaec9d7dbe4b467d5",
                base_url="https://api.lingyiwanwu.com/v1"
            ),
            instructions=[
                "Generate proper command lines for bioinformatics tools.",
                "Include error handling and status checks.",
                "Return command output and generated file paths."
            ],
        )

    def run(self, user_input: str) -> Iterator[RunResponse]:
        logger.info(f"Processing request: {user_input}")
        
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
                    ui_response = None
            except Exception as e:
                logger.warning(f"UI communication error: {e}")

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
            tasks_list = StructureOutput.create_task_splitter_output(str(task_splitter_response.content))
            if not tasks_list:
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="No valid tasks found"
                )
                return
        except Exception as e:
            logger.error(f"Task splitting error: {e}")
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

        for idx, task in enumerate(tasks_list, 1):
            task_type = "Python" if 'pythonExecutor' in task else "Shell"
            executor = self.python_executor if 'pythonExecutor' in task else self.shell_executor
            
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

# Get the user inputs
# filePath = input("Your input file path here:")
filePath = ""

if(filePath == ""):
    print("No file path provided")
else:
    destination_file_path = os.path.join(os.getcwd(), os.path.basename(filePath))
    shutil.copy(filePath, destination_file_path)

# user_input = input("Your input text here:")
user_input = "告诉我当前文件夹中有什么文件并创建test.txt文件。我正在windows下使用cmd"

# Create the workflow with the session_id
task_execution_workflow = CodeAIWorkflow(
    session_id=user_session_id,  # Use the user provided or generated session_id
    storage=SqlWorkflowStorage(
        table_name=user_session_id,
        db_file="./../Database/CodeWorkflows.db",
    ),
)

# Run the workflow
task_execution_results = task_execution_workflow.run(user_input=user_input)


pprint_run_response(task_execution_results, markdown=True)

