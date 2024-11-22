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
from StructureOutput import parse_tasks_to_list, parse_output_checker_to_dict
import ast


"""
    In TaskExecutionWorkflow, implement the following steps:
    Accept user input.
    Send the input to userInterfaceCommunicator and get the response.
    Send the response to taskSpliter and obtain a structured task list (TaskSpliterAIOutput).
    use function parse_tasks_to_list to get the tasks list
    Iterate over the task list, sending each task to corresponding ai for execution, and collect the results.
    if ERROR happend when function excuted, give the result which was been collected above to outputchecker and then outputchecker summary the result to taskspliterai to excute the same workflow
    if ERROR happend 2 times, report ERROR to the user
    After executing all tasks, send the combined results to outputChecker and obtain a structured output (outputCheckerOutput).
    Based on the parse_output_checker_to_dict worked outputChecker's decision, output the summary or return the task to Taskspliter to excute the tesks.
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
    

    def get_agent_for_task(self, task_dependency):
        if task_dependency == 'paperSearcher':
            return self.paperSearcher
        elif task_dependency == 'webSearcher':
            return self.webSeacher
        elif task_dependency == 'calculatorAI':
            return self.calculatorai
        elif task_dependency == 'pythonExecutor':
            return self.pythonExcutor
        elif task_dependency == 'shellExecutor':
            return self.shellExcutor
        else:
            return None  # Handle tasks with no dependencies or unknown dependencies

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
        # Use parse_tasks_to_list to get tasks list
        tasks_list = parse_tasks_to_list(task_splitter_response.content)
        error_count = 0

        while True:
            execution_results = []
            task_errors = False
            logger.info("Executing tasks with corresponding AIs")
            for task_str in tasks_list:
                task_data = ast.literal_eval(task_str)
                task_dependencies = task_data.get('dependencies', [])
                if not task_dependencies or task_dependencies == ['NO DEPENDENCY']:
                    logger.warning("No dependencies specified for task")
                    continue
                agent = self.get_agent_for_task(task_dependencies[0])
                if agent is None:
                    logger.warning(f"No agent found for dependency: {task_dependencies[0]}")
                    continue
                try:
                    agent_response: RunResponse = agent.run(task_data.get('description', ''))
                    if agent_response and agent_response.content:
                        execution_results.append(agent_response.content)
                        logger.info("Task executed by agent")
                    else:
                        logger.warning("Agent response invalid")
                        task_errors = True
                except Exception as e:
                    logger.warning(f"Error running agent: {e}")
                    execution_results.append(f"Error executing task: {e}")
                    task_errors = True

            if task_errors:
                error_count += 1
                if error_count >= 2:
                    logger.warning("Error occurred twice during task execution")
                    yield RunResponse(
                        run_id=self.run_id,
                        event=RunEvent.workflow_completed,
                        content="Error occurred twice during task execution",
                    )
                    return
                # Send collected results to outputChecker
                combined_results = "\n".join(execution_results)
                output_checker_response: RunResponse = self.output_checker.run(
                    "The following is the output from the execution:\n" + combined_results
                )
                # Parse outputChecker response
                output_dict = parse_output_checker_to_dict(output_checker_response.content)
                # Decide whether to re-execute the tasks based on outputChecker's decision
                if output_dict.get('checkResult', '').lower() == 'pass':
                    logger.info("Output check passed")
                    yield RunResponse(
                        run_id=self.run_id,
                        event=RunEvent.workflow_completed,
                        content=output_dict.get('summary', ''),
                    )
                    return
                else:
                    # Return tasks to taskSpliter to execute the same workflow
                    logger.info("Re-executing tasks based on outputChecker's suggestion")
                    continue
            else:
                # After executing all tasks successfully, send combined results to outputChecker
                combined_results = "\n".join(execution_results)
                output_checker_response: RunResponse = self.output_checker.run(
                    "The following is the output from the execution:\n" + combined_results
                )
                # Parse outputChecker response
                output_dict = parse_output_checker_to_dict(output_checker_response.content)
                if output_dict.get('checkResult', '').lower() == 'pass':
                    logger.info("Output check passed")
                    yield RunResponse(
                        run_id=self.run_id,
                        event=RunEvent.workflow_completed,
                        content=output_dict.get('summary', ''),
                    )
                    return
                else:
                    # Return tasks to taskSpliter to execute the same workflow
                    logger.info("Re-executing tasks based on outputChecker's suggestion")
                    error_count += 1
                    if error_count >= 2:
                        logger.warning("Error occurred twice during task execution")
                        yield RunResponse(
                            run_id=self.run_id,
                            event=RunEvent.workflow_completed,
                            content="Error occurred twice during task execution",
                        )
                        return
                    continue


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