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
            db_file="./../DataBase/data.db"
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
                "If a command is not a task skip it and return NOT A TASK.",
                "Focus on data analysis, file operations, and calculations.",
                "If a task cannot be executed, report the reason and suggest alternative approaches.",
                "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, phidata, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libxext6, libsm6, libxi6, python3.10, python3.10-pip, python3.10-dev."
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
                "Split input into two sections: description and executable tasks.",
                "First section should explain the overall process.",
                "Second section should be a numbered list of executable commands.",
                "Ensure tasks are properly formatted for ToolsAI execution.",
                "Filter out any non-executable or invalid tasks."
            ],
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=False
        )

    def split_tasks(self, task_plan: str) -> dict:
        # Process the input to ensure it has two sections
        sections = self._parse_sections(task_plan)
        if not sections:
            return {"description": "", "tasks": []}

        description, tasks_text = sections
        # Convert task text into list of executable tasks
        tasks = self._parse_tasks(tasks_text)
        
        return {
            "description": description.strip(),
            "tasks": tasks
        }

    def _parse_sections(self, task_plan: str) -> tuple:
        # Split by double newline or numbered list marker
        parts = task_plan.split('\n\n')
        if len(parts) < 2:
            # Try to find the boundary between description and tasks
            for i, line in enumerate(task_plan.split('\n')):
                if line.strip().startswith('1.') or line.strip().startswith('1)'):
                    return (
                        '\n'.join(task_plan.split('\n')[:i]),
                        '\n'.join(task_plan.split('\n')[i:])
                    )
            return None
        return (parts[0], '\n'.join(parts[1:]))

    def _parse_tasks(self, tasks_text: str) -> list:
        # Extract numbered tasks, cleaning up formatting
        tasks = []
        for line in tasks_text.split('\n'):
            line = line.strip()
            # Remove numbering and clean up
            if line and (line[0].isdigit() or line[0] in ['•', '-', '*']):
                task = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if task:
                    tasks.append(task)
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