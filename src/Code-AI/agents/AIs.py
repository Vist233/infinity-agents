import subprocess
from phi.agent import Agent
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.agent import Agent, RunResponse
from phi.model.openai.like import OpenAILike



class BaseAI:
    def __init__(self, model_id: str, description: str, instruction: list, table_name: str, debug_mode=False, add_history_to_messages=True, stream=False):
        self.storage = SqlAgentStorage(
            table_name=table_name,
            db_file="db/data.db"
        )
        self.agent = Agent(
            model=OpenAILike(
                id=model_id,
                api_key="1352a88fdd3844deaec9d7dbe4b467d5",
                base_url="https://api.lingyiwanwu.com/v1"
            ),
            description=description,
            instruction=instruction,
            markdown=True,
            debug_mode=debug_mode,
            storage=self.storage,
            add_history_to_messages=add_history_to_messages,
            stream=stream
        )

class TalkAI(BaseAI):
    def __init__(self, table_name="talk_ai", debug_mode=False, stream=False):
        super().__init__(
            model_id="yi-lightning",
            description="An AI assistant that converts user requests into executable bioinformatics tasks using only available system tools and Python packages.",
            instruction=[
                "Create executable task plans using only existing system tools and installed Python packages.",
                "Break down complex tasks into smaller, executable steps.",
                "Avoid generating tasks that require external software installation or system configuration.",
                "Focus on data processing, analysis, and visualization tasks."
            ],
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=True,
            stream=stream
        )

    def process_input(self, user_input: str):
        # Generate a task execution plan based on user input
        task_plan = self.agent.run(f"Create a bioinformatics task execution plan for: {user_input}").content.strip()
        return task_plan

class ToolsAI(BaseAI):
    def __init__(self, table_name: str, debug_mode=False, add_history_to_messages=False, tools=[ShellTools(), PythonTools()]):
        super().__init__(
            model_id="yi-large-fc",
            description="An AI that executes bioinformatics tasks using available Python packages and system tools.",
            instruction=[
                "Execute only tasks that use existing Python packages and system tools.",
                "Do not attempt to install new software or modify system configurations.",
                "Process biological data using available resources.",
                "Report if a task cannot be executed with current tools.",
                "Focus on data analysis, file operations, and calculations."
            ],
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=add_history_to_messages
        )
        self.agent.tools = tools
        self.agent.show_tool_calls = True

    def is_harmful(self, code: str) -> bool:
        # Code to check if the task is harmful
        return False  # Placeholder implementation

    def execute_task(self, task: str) -> str:
        # Execute the given task
        execution_result = self.agent.run(f"Execute the following task:\n{task}").content.strip()
        return execution_result

class TaskSplitterAI(BaseAI):
    def __init__(self, table_name="task_splitter", debug_mode=False):
        super().__init__(
            model_id="yi-lightning",
            description="An AI that validates and distributes executable tasks to ToolsAI.",
            instruction=[
                "Verify that tasks only use available system tools and Python packages.",
                "Reject tasks requiring external software installation or system changes.",
                "Split complex tasks into executable subtasks.",
                "Ensure each subtask can be handled by current ToolsAI capabilities.",
                "Flag and filter out any non-executable tasks."
            ],
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=False
        )

    def split_tasks(self, task_plan: str) -> list:
        # Split the task plan into a list of tasks
        tasks = [task.strip() for task in task_plan.strip().split('\n') if task.strip()]
        return tasks

class OutputCheckerAI(BaseAI):
    def __init__(self, table_name="output_checker", debug_mode=False):
        super().__init__(
            model_id="yi-lightning",
            description="An AI that validates task outputs and execution status.",
            instruction=[
                "Verify that task outputs are complete and valid.",
                "Check for execution errors or tool limitations.",
                "Ensure results meet bioinformatics quality standards.",
                "Report any execution failures or incomplete tasks.",
                "Validate data formats and analysis results."
            ],
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=False
        )

    def check_output(self, output: str) -> str:
        # Check the output files and terminal outputs for correctness
        check_result = self.agent.run(f"Check the following output for correctness:\n{output}").content.strip()
        return check_result