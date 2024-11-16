import json
import os
from typing import Optional, Iterator, Dict, List, Any
from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.workflow import Workflow, RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.log import logger
from AI_Classes import (
    session_id,
    searchSummaryTeam
)


class TaskExecutionWorkflow(Workflow):
    searchSummaryTeam: Agent = searchSummaryTeam

    def run(self, user_input: str) -> Iterator[RunResponse]:
        logger.info(f"User input received: {user_input}")
        try:
            response: RunResponse = self.searchSummaryTeam.run(user_input)
            if response and response.content:
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content=response.content,
                )
            else:
                logger.warning("searchSummaryTeam response invalid")
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content="searchSummaryTeam response invalid",
                )
        except Exception as e:
            logger.warning(f"Error running searchSummaryTeam: {e}")
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Error running searchSummaryTeam: {e}",
            )

# Create the new workflow
task_execution_workflow = TaskExecutionWorkflow(
    session_id=session_id,
    storage=SqlWorkflowStorage(
        table_name=session_id,
        db_file="./../Database/SearchWorkflows.db",
    ),
)

# Run the workflow
task_execution_results: Iterator[RunResponse] = task_execution_workflow.run(user_input=user_input)

