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


class talkAI(BaseAI):
    def __init__(self, description: str, instruction: list, table_name: str, debug_mode=False, add_history_to_messages=True):
        super().__init__(
            model_id="yi-lightning",
            description=description,
            instruction=instruction,
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=add_history_to_messages
        )

class figAI(BaseAI):
    def __init__(self, description: str, instruction: str, table_name: str, debug_mode=False, add_history_to_messages=False):
        super().__init__(
            model_id="yi-vision",
            description=description,
            instruction=instruction,
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=add_history_to_messages
        )

    def encode_image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return "data:image/jpeg;base64," + base64.b64encode(image_file.read()).decode('utf-8')

    def image_recognition(self, image_paths: List[str], description: str):
        images = [{"type": "image_url", "image_url": {"url": self.encode_image_to_base64(path)}} for path in image_paths]
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": description},
                    *images
                ]
            }
        ]
        completion = self.agent.model.client.chat.completions.create(
            model=self.agent.model.id,
            messages=messages
        )
        return completion

class searchAI(BaseAI):
    def __init__(self, description: str, instruction: list, table_name: str, debug_mode=False, add_history_to_messages=True):
        super().__init__(
            model_id="yi-large-rag",
            description=description,
            instruction=instruction,
            table_name=table_name,
            debug_mode=debug_mode,
            add_history_to_messages=add_history_to_messages
        )

class ToolsAI(BaseAI):
    def __init__(self, tools: List, description: str, instruction: list, table_name: str, debug_mode=False, add_history_to_messages=False):
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

class TaskSplitterAI(BaseAI):
    def __init__(self):
        super().__init__(
            model_id="yi-large-fc",
            description="Task analyzer that determines which specialized agent should handle a task",
            instruction=[],
            table_name="task_splitter",
            debug_mode=False,
            add_history_to_messages=False
        )
        self.tools_agents = {
            "search": ToolsAI(
                tools=[GoogleSearch(), DuckDuckGo()],
                description="Specialized in web searches and information gathering",
                instruction=[],
                table_name="search_agent"
            ),
            "compute": ToolsAI(
                tools=[PythonTools()],
                description="Specialized in computational tasks and data processing",
                instruction=[],
                table_name="compute_agent"
            ),
            "system": ToolsAI(
                tools=[ShellTools()],
                description="Specialized in system operations and file management",
                instruction=[],
                table_name="system_agent"
            )
        }

    def process_task(self, task: str) -> str:
        analysis = self.agent.run(f"""
        Analyze this task and respond only with one of: 'search', 'compute', or 'system':
        Task: {task}
        """).content.strip()
        if analysis in self.tools_agents:
            return self.tools_agents[analysis].agent.run(task).content
        else:
            return "Could not determine appropriate agent for this task"