from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.workflow import RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.log import logger
from StructureOutput import TaskSpliterAIOutput, outputCheckerOutput
from AI_Classes import (
    userInterfaceCommunicator,
    taskSpliter,
    toolsTeam,
    outputChecker,
    session_id
)
import shutil
from phi.utils.pprint import pprint_run_response
import os
from typing import Iterator
import json
import re

def process_string(input_string):
    # Step 1: Extract the content between the first [ and the first ]
    match = re.search(r'\[(.*?)\]', input_string, re.DOTALL)
    if not match:
        return []

    extracted_string = match.group(1)

    # Step 2: Remove special characters
    cleaned_string = re.sub(r'[\n\t\r]', '', extracted_string)

    # Step 3: Convert the string to a list
    result_list = cleaned_string.split(',')

    # Remove any leading/trailing whitespace from each element
    result_list = [item.strip() for item in result_list]

    return result_list

def run_workflow(user_input: str) -> Iterator[RunResponse]:
    listCurrentDir = os.listdir('.')
    logger.info(f"User input received: {user_input}")

    # Step 1: Process input with userInterfaceCommunicator
    logger.info("Processing input with userInterfaceCommunicator")
    try:
        ui_response: RunResponse = userInterfaceCommunicator.run(
            "The following is the files under current dir\n" + str(listCurrentDir) + "\nThe following is the user's input\n" + user_input
        )
        if ui_response and ui_response.content:
            ui_content = ui_response.content
            logger.info("Received response from userInterfaceCommunicator")
        else:
            logger.warning("userInterfaceCommunicator response invalid")
            yield RunResponse(
                run_id=session_id,
                event=RunEvent.workflow_completed,
                content="userInterfaceCommunicator response invalid",
            )
            return
    except Exception as e:
        logger.warning(f"Error running userInterfaceCommunicator: {e}")
        yield RunResponse(
            run_id=session_id,
            event=RunEvent.workflow_completed,
            content=f"Error running userInterfaceCommunicator: {e}",
        )
        return
    
    listCurrentDir = os.listdir('.')
    # Step 2: Split the task using taskSpliter
    logger.info("Splitting the task with taskSpliter")
    try:
        task_splitter_response: RunResponse = taskSpliter.run(
            "The following is the files under current dir:\n" +
            "\n".join(listCurrentDir) +
            "\nThe following is the user input:\n" +
            ui_content
        )
        if task_splitter_response and task_splitter_response.content:
            tasks = process_string(task_splitter_response.content)
            logger.info(f"Task split into {len(tasks)} subtasks.")
        else:
            logger.warning("taskSpliter response invalid")
            yield RunResponse(
                run_id=session_id,
                event=RunEvent.workflow_completed,
                content="taskSpliter response invalid",
            )
            return
    except Exception as e:
        logger.warning(f"Error running taskSpliter: {e}")
        yield RunResponse(
            run_id=session_id,
            event=RunEvent.workflow_completed,
            content=f"Error running taskSpliter: {e}",
        )
        return

    listCurrentDir = os.listdir('.')
    # Step 3: Execute tasks with toolsTeam
    execution_results = []
    logger.info("Executing tasks with toolsTeam")
    for task in tasks:
        try:
            tools_team_response: RunResponse = toolsTeam.run(
                "The following is the files under current dir:\n" + 
                "\n".join(listCurrentDir) + 
                "\nThe following is the task:\n" + 
                json.dumps(task, indent=4)
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
        output_checker_response: RunResponse = outputChecker.run(
            "The following is the files under current dir:\n" + 
            "\n".join(listCurrentDir) + 
            "\nThe following is the output from the execution:\n" + 
            combined_results
        )
        if output_checker_response and output_checker_response.content:
            output_checker_output = outputCheckerOutput.parse_obj(output_checker_response.content)
            logger.info(f"Output check result: {output_checker_output.checkResult}")
            if output_checker_output.checkResult.lower() == "pass":
                yield RunResponse(
                    run_id=session_id,
                    event=RunEvent.workflow_completed,
                    content=combined_results,
                )
            else:
                logger.warning("Output check failed")
                yield RunResponse(
                    run_id=session_id,
                    event=RunEvent.workflow_completed,
                    content="Output check failed",
                )
        else:
            logger.warning("outputChecker response invalid")
            yield RunResponse(
                run_id=session_id,
                event=RunEvent.workflow_completed,
                content="outputChecker response invalid",
            )
    except Exception as e:
        logger.warning(f"Error running outputChecker: {e}")
        yield RunResponse(
            run_id=session_id,
            event=RunEvent.workflow_completed,
            content=f"Error running outputChecker: {e}",
        )

# Create a new directory for the session
os.makedirs('./app/ProcessingSpace/' + session_id, exist_ok=True)
os.chdir('./app/ProcessingSpace/' + session_id)

filePath = input("Your input file path here:")
if(filePath == ""):
    print("No file path provided")
else:
    destination_file_path = os.path.join(os.getcwd(), os.path.basename(filePath))
    shutil.copy(filePath, destination_file_path)

# Get the user input text
user_input = input("Your input text here:")

# Run the workflow
task_execution_results: Iterator[RunResponse] = run_workflow(user_input=user_input)

pprint_run_response(task_execution_results, markdown=True)