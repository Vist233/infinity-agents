import subprocess
from phi.agent import Agent
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.agent import Agent, RunResponse
from phi.model.openai.like import OpenAILike



class BaseAI:
    def __init__(self, model_id: str, description: str, instruction: list, table_name: str, debug_mode=False, add_history_to_messages=True):
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
            add_history_to_messages=add_history_to_messages
        )

class TalkAI(BaseAI):
    def __init__(self, table_name="talk_ai", debug=False):
        super().__init__(
            model_id="yi-lightning",
            description="An AI assistant that receives user input and generates a task execution plan.",
            instruction=[
                "Receive user requests and create a task execution plan.",
                "Provide the task execution plan to TaskSplitterAI."
            ],
            table_name=table_name,
            debug_mode=debug,
            add_history_to_messages=True
        )

    def process_input(self, user_input: str):
        # Generate a task execution plan based on user input
        task_plan = self.agent.run(f"Create a bioinformatics task execution plan for: {user_input}").content.strip()
        return task_plan

class ToolsAI(BaseAI):
    def __init__(self, tools: list, description: str, instruction: list, table_name: str, debug_mode=False, add_history_to_messages=False):
        super().__init__(
            model_id="yi-large-fc",
            description=description,
            instruction=instruction,
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=add_history_to_messages
        )
        self.agent.tools = tools
        self.agent.show_tool_calls = True

    def execute_task(self, task: str):
        # Execute the task by running bioinformatics software
        try:
            # Ensure the task command is safe to execute
            safe_command = self.sanitize_command(task)
            result = subprocess.run(safe_command, shell=True, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"An error occurred while executing the task: {e}"

    def sanitize_command(self, command: str) -> str:
        # Implement command sanitization to prevent unsafe executions
        # ...code to sanitize command...
        return command  # Placeholder

    def is_harmful(self, code: str) -> bool:
        # Code to check if the task is harmful
        return False  # Placeholder implementation

class TaskSplitterAI(BaseAI):
    def __init__(self, table_name="task_splitter"):
        super().__init__(
            model_id="yi-large-fc",
            description="An AI that analyzes tasks and distributes them to the appropriate ToolsAI.",
            instruction=[
                "Analyze the task execution plan from TalkAI.",
                "Determine the appropriate ToolsAI for each task.",
                "Ensure the task is safe before execution."
            ],
            table_name=table_name,
            debug_mode=False,
            add_history_to_messages=False
        )
        self.tools_agents = {
            "script": ToolsAI(
                tools=[PythonTools()],
                description="Specialized in executing data processing scripts.",
                instruction=[
                    "Execute data processing tasks using Python."
                ],
                table_name="script_agent"
            ),
            "system": ToolsAI(
                tools=[ShellTools()],
                description="Specialized in performing system operations and file management.",
                instruction=[
                    "Execute system operations and manage files."
                ],
                table_name="system_agent"
            )
        }

    def process_task(self, task_plan: str) -> str:
        # Analyze the task plan and select the appropriate agent
        analysis = self.agent.run(f"""
            Analyze the following task and determine the appropriate tool ('script' or 'system'):
            Task: {task_plan}
            """).content.strip()
        if analysis in self.tools_agents:
            execution_result = self.tools_agents[analysis].execute_task(task_plan)
            return execution_result
        else:
            return "Could not determine appropriate agent for this task"

class OutputCheckerAI(BaseAI):
    def __init__(self, table_name="output_checker"):
        super().__init__(
            model_id="yi-lightning",
            description="An AI that checks the output of executed tasks.",
            instruction=[
                "Review the output of tasks from ToolsAI.",
                "Ensure the output meets the required standards."
            ],
            table_name=table_name,
            debug_mode=False,
            add_history_to_messages=False
        )

    def check_output(self, output: str) -> str:
        # Check the output files and terminal outputs for correctness
        check_result = self.agent.run(f"Check the following output for correctness:\n{output}").content.strip()
        return check_result