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
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_interface: Agent = Field(default_factory=lambda: userInterfaceCommunicator)
    task_splitter: Agent = Field(default_factory=lambda: taskSpliter)
    pythonExcutor: Agent = Field(default_factory=lambda: pythonExcutor)
    shellExcutor: Agent = Field(default_factory=lambda: shellExcutor)
    
    def get_agent_for_task(self, task_dependency):
        if task_dependency == 'pythonExecutor':
            return self.pythonExcutor
        elif task_dependency == 'shellExecutor':
            return self.shellExcutor
        else:
            return None

    def run(self, user_input: str) -> Iterator[RunResponse]:
        listCurrentDir = os.listdir('.')
        logger.info(f"User input received: {user_input}")

        # Step 1: Process with userInterfaceCommunicator
        try:
            ui_response: RunResponse = self.user_interface.run(
                f"Current directory files:\n{str(listCurrentDir)}\nUser input:\n{user_input}"
            )
            if not ui_response or not ui_response.content:
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="Invalid userInterfaceCommunicator response"
                )
                return
            logger.info("Received response from userInterfaceCommunicator")
        except Exception as e:
            logger.error(f"userInterfaceCommunicator error: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Error: {str(e)}"
            )
            return

        logger.info(f"{ui_response.content}")

        # Step 2: Process with taskSpliter
        try:
            task_splitter_response: RunResponse = self.task_splitter.run(ui_response.content)
            logger.info(f"{task_splitter_response.content}")
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

        logger.info(f"Tasks list: {tasks_list}")

        # Step 3: Execute tasks
        execution_results = []
        for task in tasks_list:
            try:
                # Determine dependencies by searching the string
                if 'pythonExecutor' in task:
                    agent = self.pythonExcutor
                elif 'shellExecutor' in task:
                    agent = self.shellExcutor
                else:
                    logger.info(f"Skipping task due to no valid dependencies: {task}")
                    continue

                agent_response = agent.run(task)
                if agent_response and agent_response.content:
                    execution_results.append(agent_response.content)

            except Exception as e:
                logger.error(f"Task execution error: {e}")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content=f"Task execution error: {str(e)}"
                )
                return

        # Return final results
        yield RunResponse(
            run_id=self.run_id,
            event=RunEvent.workflow_completed,
            content="\n".join(execution_results)
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

