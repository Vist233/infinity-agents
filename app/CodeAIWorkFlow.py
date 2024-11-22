from pydantic import Field
from phi.agent import Agent
from phi.workflow import Workflow, RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.log import logger
from AI_Classes import (
    userInterfaceCommunicator,
    taskSpliter,
    outputCheckerAndSummary,
    paperSearcher,
    webSeacher,
    calculatorai,
    pythonExcutor,
    shellExcutor
)
import shutil
from phi.utils.pprint import pprint_run_response
import os
from typing import Iterator
import uuid


"""
    In TaskExecutionWorkflow, implement the following steps:
    Accept user input.
    Send the input to userInterfaceCommunicator and get the response.
    Send the response to taskSpliter and obtain a structured task list (TaskSpliterAIOutput).
    Iterate over the task list, sending each task to toolsTeam for execution, and collect the results.
    After executing all tasks, send the combined results to outputChecker and obtain a structured output (outputCheckerOutput).
    Based on the outputChecker's decision, output the summary or return the task to Taskspliter to excute the tesks.
"""

class CodeAIWorkflow(Workflow):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_interface: Agent = Field(default_factory=lambda: userInterfaceCommunicator)
    task_splitter: Agent = Field(default_factory=lambda: taskSpliter)
    output_checker: Agent = Field(default_factory=lambda: outputCheckerAndSummary)
    
    paperSearcher: Agent = Field(default_factory=lambda: paperSearcher)
    webSeacher: Agent = Field(default_factory=lambda: webSeacher)
    calculatorai: Agent = Field(default_factory=lambda: calculatorai)
    pythonExcutor: Agent = Field(default_factory=lambda: pythonExcutor)
    shellExcutor: Agent = Field(default_factory=lambda: shellExcutor)
    


    def run(self, user_input: str) -> Iterator[RunResponse]:
        listCurrentDir = os.listdir('.')
        logger.info(f"User input received: {user_input}")

        # Step 1: Process input with userInterfaceCommunicator
        logger.info("Processing input with userInterfaceCommunicator")
        try:
            ui_response: RunResponse = self.user_interface.run(
                "The following is the files under current dir\n" + str(listCurrentDir) + "\nThe following is the user's input\n" + user_input
            )
            if ui_response and ui_response.content:
                ui_content = ui_response.content
                logger.info("Received response from userInterfaceCommunicator")
            else:
                logger.warning("userInterfaceCommunicator response invalid")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="userInterfaceCommunicator response invalid",
                )
                return
        except Exception as e:
            logger.warning(f"Error running userInterfaceCommunicator: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Error running userInterfaceCommunicator: {e}",
            )
            return
        
        
        
        
        listCurrentDir = os.listdir('.')
        # Step 2: Split the task using taskSpliter
        logger.info("Splitting the task with taskSpliter")
        try:
            task_splitter_response: RunResponse = self.task_splitter.run(
                "The following is the files under current dir:\n" +
                "\n".join(listCurrentDir) +
                "\nThe following is the user input:\n" +
                ui_content
            )
            logger.info(f"task_splitter_response.content: {task_splitter_response.content}")
        except Exception as e:
            logger.warning(f"Unexpected error: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Unexpected error: {e}",
            )
            return
        content = str(task_splitter_response.content)
        tasks = content.split('|')


        
        

        listCurrentDir = os.listdir('.')
        # Step 3: Execute tasks with toolsTeam
        execution_results = []
        logger.info("Executing tasks with toolsTeam")
        for task in tasks:
            try:
                tools_team_response: RunResponse = self.tools_team.run(
                    "The following is the files under current dir:\n" + 
                    "\n".join(listCurrentDir) + 
                    "\nThe following is the task:\n" + 
                    task
                )
                if tools_team_response and tools_team_response.content:
                    execution_results.append(tools_team_response.content)
                    logger.info("Task executed by toolsTeam")
                else:
                    logger.warning("toolsTeam response invalid")
            except Exception as e:
                logger.warning(f"Error running toolsTeam: {e}")
                execution_results.append(f"Error executing task: {e}")




        listCurrentDir = os.listdir('.')
        # Step 4: Check outputs with outputChecker
        logger.info("Checking execution results with outputChecker")
        try:
            combined_results = "\n".join(execution_results)
            output_checker_response: RunResponse = self.output_checker.run(
                "The following is the files under current dir:\n" + 
                "\n".join(listCurrentDir) + 
                "\nThe following is the output from the execution:\n" + 
                combined_results
            )
            logger.info(f"Output check result: {output_checker_response.content}")
            
            content = str(output_checker_response.content)
            if content.startswith("```json"):
                content = content[7:-3].strip()            
            
            if(check_result(content)):
                logger.info("Output check passed")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content=combined_results,
                )
            else:
                logger.warning("Output check failed")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="Output check failed",
                )
        except Exception as e:
            logger.warning(f"Error running outputChecker: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Error running outputChecker: {e}",
            )
            return


# Move this block to after user input but before workflow creation
if not os.path.exists('./ProcessingSpace'):
    os.makedirs('./ProcessingSpace')
os.chdir('./ProcessingSpace/')

# Get the user inputs
session_input = input("Session ID (press Enter to generate new): ").strip()

while(1):
    if os.path.isdir(session_input):
        user_session_id = session_input
        break
    elif session_input == "":
        user_session_id = str(uuid.uuid4())
        break
    else:
        user_session_id = input("session ID invalied, Please reenter the session ID (press Enter to generate new): ")

os.makedirs(user_session_id, exist_ok=True)
os.chdir(user_session_id)

filePath = input("Your input file path here:")
if(filePath == ""):
    print("No file path provided")
else:
    destination_file_path = os.path.join(os.getcwd(), os.path.basename(filePath))
    shutil.copy(filePath, destination_file_path)

user_input = input("Your input text here:")

# Create the workflow with the session_id
task_execution_workflow = CodeAIWorkflow(
    session_id=user_session_id,  # Use the user provided or generated session_id
    storage=SqlWorkflowStorage(
        table_name=user_session_id,
        db_file="./../Database/CodeWorkflows.db",
    ),
)

# Run the workflow
task_execution_results: Iterator[RunResponse] = task_execution_workflow.run(user_input=user_input)


pprint_run_response(task_execution_results, markdown=True)