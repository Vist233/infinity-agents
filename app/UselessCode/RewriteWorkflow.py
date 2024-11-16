import json
from typing import Optional, Iterator, Dict, List, Any
from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.workflow import Workflow, RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.log import logger
from phi.model.openai.like import OpenAILike
import AI_Classes
from StructureOutput import TaskSpliterAIOutput, outputCheckerOutput
from AI_Classes import (
    userInterfaceCommunicator,
    taskSpliter,
    toolsTeam,
    outputChecker,
    session_id
)

# Define the Workflow
class TaskProcessingWorkflow(Workflow):
    task_splitter: Agent = AI_Classes.userInterfaceCommunicator
    output_checker: Agent = AI_Classes.outputChecker

    def run(self, user_input: str) -> Iterator[RunResponse]:
        logger.info(f"Processing user input: {user_input}")

        # Step 1: Split the task
        logger.info("Splitting the task")
        try:
            task_splitter_response: RunResponse = self.task_splitter.run(user_input)
            if task_splitter_response and task_splitter_response.content:
                task_splitter_output = TaskSpliterAIOutput.parse_obj(task_splitter_response.content)
                logger.info(f"Task split into {len(task_splitter_output.tasks)} subtasks.")
            else:
                logger.warning("Task splitter response invalid")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="Task splitter response invalid",
                )
                return
        except Exception as e:
            logger.warning(f"Error running task splitter: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Error running task splitter: {e}",
            )
            return

        # Step 2: Check the output
        logger.info("Checking the output of task splitter")
        try:
            for task in task_splitter_output.tasks:
                if task != "NOT A TASK":
                    output_checker_response: RunResponse = self.output_checker.run(json.dumps(task, indent=4))
                    if output_checker_response and output_checker_response.content:
                        output_checker_output = outputCheckerOutput.parse_obj(output_checker_response.content)
                        logger.info(f"Output check result: {output_checker_output.checkResult}")
                    else:
                        logger.warning("Output checker response invalid")
                        yield RunResponse(
                            run_id=self.run_id,
                            event=RunEvent.workflow_completed,
                            content="Output checker response invalid",
                        )
                        return
        except Exception as e:
            logger.warning(f"Error running output checker: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Error running output checker: {e}",
            )
            return

        # Save the tasks in the session state for future reference
        if "tasks" not in self.session_state:
            self.session_state["tasks"] = []
        self.session_state["tasks"].extend(task_splitter_output.tasks)

        yield RunResponse(
            run_id=self.run_id,
            event=RunEvent.workflow_completed,
            content=task_splitter_output.tasks,
        )

# Create the workflow
task_processing_workflow = TaskProcessingWorkflow(
    session_id=AI_Classes.session_id,
    storage=SqlWorkflowStorage(
        table_name="task_processing_workflows",
        db_file="tmp/workflows.db",
    ),
)

# Run workflow
user_input = "Your input text here"
task_processing_results: Iterator[RunResponse] = task_processing_workflow.run(user_input=user_input)

# Define the new Workflow
class TaskExecutionWorkflow(Workflow):
    user_interface: Agent = userInterfaceCommunicator
    task_splitter: Agent = taskSpliter
    tools_team: Agent = toolsTeam
    output_checker: Agent = outputChecker

    def run(self, user_input: str) -> Iterator[RunResponse]:
        logger.info(f"User input received: {user_input}")

        # Step 1: Process input with userInterfaceCommunicator
        logger.info("Processing input with userInterfaceCommunicator")
        try:
            ui_response: RunResponse = self.user_interface.run(user_input)
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

        # Step 2: Split the task using taskSpliter
        logger.info("Splitting the task with taskSpliter")
        try:
            task_splitter_response: RunResponse = self.task_splitter.run(ui_content)
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

        # Step 3: Execute tasks with toolsTeam
        execution_results = []
        logger.info("Executing tasks with toolsTeam")
        for task in tasks:
            try:
                tools_team_response: RunResponse = self.tools_team.run(json.dumps(task, indent=4))
                if tools_team_response and tools_team_response.content:
                    execution_results.append(tools_team_response.content)
                    logger.info("Task executed by toolsTeam")
                else:
                    logger.warning("toolsTeam response invalid")
            except Exception as e:
                logger.warning(f"Error running toolsTeam: {e}")
                execution_results.append(f"Error executing task: {e}")

        # Step 4: Check outputs with outputChecker
        logger.info("Checking execution results with outputChecker")
        try:
            combined_results = "\n".join(execution_results)
            output_checker_response: RunResponse = self.output_checker.run(combined_results)
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

# Create the new workflow
task_execution_workflow = TaskExecutionWorkflow(
    session_id=session_id,
    storage=SqlWorkflowStorage(
        table_name=session_id,
        db_file="tmp/workflows.db",
    ),
)

# Run the new workflow
user_input = "Your input text here"
task_execution_results: Iterator[RunResponse] = task_execution_workflow.run(user_input=user_input)

# pprint_run_response(task_processing_results, markdown=True)
