from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.workflow import Workflow, RunResponse, RunEvent
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


class CodeAIWorkflow(Workflow):
    user_interface: Agent = Field(default_factory=lambda: userInterfaceCommunicator)
    task_splitter: Agent = Field(default_factory=lambda: taskSpliter)
    tools_team: Agent = Field(default_factory=lambda: toolsTeam)
    output_checker: Agent = Field(default_factory=lambda: outputChecker)

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
            if task_splitter_response and task_splitter_response.content:
                task_splitter_output = TaskSpliterAIOutput.parse_obj(task_splitter_response.content)
                tasks = task_splitter_output.tasks
                logger.info(f"Task split into {len(tasks)} subtasks.")
            else:
                logger.warning("taskSpliter response invalid")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="taskSpliter response invalid",
                )
                return
        except Exception as e:
            logger.warning(f"Error running taskSpliter: {e}")
            yield RunResponse(
                run_id=self.run_id,
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
                tools_team_response: RunResponse = self.tools_team.run(
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
            output_checker_response: RunResponse = self.output_checker.run(
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
            else:
                logger.warning("outputChecker response invalid")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="outputChecker response invalid",
                )
        except Exception as e:
            logger.warning(f"Error running outputChecker: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Error running outputChecker: {e}",
            )


# Create a new directory for the session
os.makedirs('./app/ProcessingSpace/' + session_id, exist_ok=True)
os.chdir('./app/ProcessingSpace/' + session_id)

filePath = input("Your input file path here:")
destination_file_path = os.path.join(os.getcwd(), os.path.basename(filePath))
shutil.copy(filePath, destination_file_path)

# Get the user input text
user_input = input("Your input text here:")

# Create the new workflow
task_execution_workflow = CodeAIWorkflow(
    session_id=session_id,
    storage=SqlWorkflowStorage(
        table_name="task_execution_workflows",
        db_file="./../Database/CodeWorkflows.db",
    ),
)

# Run the workflow
task_execution_results: Iterator[RunResponse] = task_execution_workflow.run(user_input=user_input)


pprint_run_response(task_execution_results, markdown=True)