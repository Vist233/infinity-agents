from flask import Flask, render_template, request
from phi.tools.duckduckgo import DuckDuckGo
import json
from typing import Optional, Iterator
from phi.agent import Agent
from phi.workflow import Workflow, RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.log import logger
from phi.tools.arxiv_toolkit import ArxivToolkit
from phi.model.openai.like import OpenAILike
import shutil
import os


class PaperSummaryGenerator(Workflow):

    searcher: Agent = Agent(
        model=OpenAILike(
            id="yi-large-fc",
            api_key="1352a88fdd3844deaec9d7dbe4b467d5",
            base_url="https://api.lingyiwanwu.com/v1",
        ),
        tools=[ArxivToolkit()],
        instructions=["Given a topic, search for 10 research papers and return the 5 most relevant papers in a simple format including title, URL, and abstract for each paper."],
    )

    summarizer: Agent = Agent(
        instructions=[
            "You will be provided with a topic and a list of top research papers on that topic.",
            "Carefully read each paper and generate a concise summary of the research findings.",
            "Break the summary into sections and provide key takeaways at the end.",
            "Make sure the title is informative and clear.",
            "Always provide sources, do not make up information or sources.",
        ],
        model=OpenAILike(
            id="yi-medium-200k",
            api_key="1352a88fdd3844deaec9d7dbe4b467d5",
            base_url="https://api.lingyiwanwu.com/v1",
        ),
    )

    def run(self, topic: str, use_cache: bool = True) -> Iterator[RunResponse]:
        logger.info(f"Generating a summary on: {topic}")

        # Use the cached summary if use_cache is True
        if use_cache and "summaries" in self.session_state:
            logger.info("Checking if cached summary exists")
            for cached_summary in self.session_state["summaries"]:
                if cached_summary["topic"] == topic:
                    logger.info("Found cached summary")
                    yield RunResponse(
                        run_id=self.run_id,
                        event=RunEvent.workflow_completed,
                        content=cached_summary["summary"],
                    )
                    return

        # Step 1: Search the web for research papers on the topic
        num_tries = 0
        search_results = None
        # Run until we get valid search results
        while search_results is None and num_tries < 3:
            try:
                num_tries += 1
                searcher_response: RunResponse = self.searcher.run(topic)
                if (
                    searcher_response
                    and searcher_response.content
                ):
                    logger.info("Successfully retrieved papers.")
                    search_results = searcher_response.content
                else:
                    logger.warning("Searcher response invalid, trying again...")
            except Exception as e:
                logger.warning(f"Error running searcher: {e}")

        # If no search_results are found for the topic, end the workflow
        if not search_results:
            yield RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_completed,
                content=f"Sorry, could not find any research papers on the topic: {topic}",
            )
            return

        # Step 2: Summarize the research papers
        logger.info("Summarizing research papers")
        # Prepare the input for the summarizer
        summarizer_input = {
            "topic": topic,
            "papers": search_results,
        }
        # Run the summarizer and yield the response
        yield from self.summarizer.run(json.dumps(summarizer_input, indent=4), stream=True)

        # Save the summary in the session state for future runs
        if "summaries" not in self.session_state:
            self.session_state["summaries"] = []
        self.session_state["summaries"].append({"topic": topic, "summary": self.summarizer.run_response.content})


class AssistantT:

    def __init__(self):
        self.assistantT = Agent(
            name="Web Searcher",
            role="Search from and summary web.",
            tools=[DuckDuckGo()],
            model=OpenAILike(
                id="yi-large-fc",
                api_key="1352a88fdd3844deaec9d7dbe4b467d5",
                base_url="https://api.lingyiwanwu.com/v1",
            )
        )

    def workflow(self, user_input: str):
        return self.assistantT.run(user_input).content

app = Flask(__name__)
#assistant = AssistantT()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    messages = []
    logs = ["系统初始化完成\n"]
    uploaded_files = []  # 用于存储成功上传的文件名

    if request.method == "POST":
        if "file" in request.files:
            uploaded_files_list = request.files.getlist("file")
            for file in uploaded_files_list:
                if file :
                    filename = file.filename
                    file_save_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_save_path)
                    uploaded_files.append(filename)
                    logs.append(f"文件 '{filename}' 已成功上传至 {file_save_path}")

        user_input = request.form.get("userInput")
        if user_input:
            assistant = PaperSummaryGenerator(
                session_id=f"generate-summary-on-{user_input}",
                storage=SqlWorkflowStorage(
                    table_name="generate_summary_workflows",
                    db_file="tmp/workflows.db",
                ),
            )

            try:
                logs.append(f"用户发送: {user_input}\n")
                response = ""
                for res in assistant.run(user_input):
                    if res.event == RunEvent.workflow_completed:
                        logs.append("Workflow completed.\n")
                        response = res.content

                messages.append({"type": "user", "text": user_input})
                messages.append({"type": "ai", "text": response})
                logs.append(f"AI 回复: {response}\n")

            except Exception as e:
                error_message = f"处理过程中出错: {e}"
                logs.append(f"{error_message}\n")
                messages.append({"type": "ai", "text": error_message})

    return render_template("main.html",
                           messages=messages,
                           logs=logs,
                           uploaded_files=uploaded_files)


@app.route("/upload", methods=["POST"])
def upload():
    logs = []
    uploaded_files = []

    if "files" in request.files:
        uploaded_files_list = request.files.getlist("files")
        for file in uploaded_files_list:
            if file and file.filename:
                filename = file.filename
                file_save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_save_path)
                uploaded_files.append(filename)
                logs.append(f"文件 '{filename}' 已成功上传至 {file_save_path}")

    return {"logs": logs, "uploaded_files": uploaded_files}, 200


if __name__ == "__main__":
    #user_input = input("Please enter your query: ")
    #print(assistant.workflow(user_input))
    app.run(debug=True)
