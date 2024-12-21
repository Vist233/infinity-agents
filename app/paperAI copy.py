from typing import Iterator
from phi.agent import Agent
from phi.utils.pprint import pprint_run_response
from phi.workflow import Workflow, RunResponse
from phi.utils.log import logger
from phi.model.openai.like import OpenAILike
from phi.tools.pubmed import PubmedTools
from phi.tools.arxiv_toolkit import ArxivToolkit
from config import API_KEY

# Get the API key from environment variables OR set your API key here
API_KEY = API_KEY

class PaperSummaryGenerator(Workflow):
    
    searcher: Agent = Agent(
        model=OpenAILike(
            id="yi-large-fc",
            api_key=API_KEY,
            base_url="https://api.lingyiwanwu.com/v1",
        ),
        tools=[PubmedTools()],
        instructions=[
            "Given a topic, search for relevant research papers.",
            "For each paper, provide the title, URL, and abstract in plain text format.",
            "Separate papers with '---' and use consistent formatting:",
        ],
        add_history_to_messages=True,
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
            api_key=API_KEY,
            base_url="https://api.lingyiwanwu.com/v1",
        ),
        add_history_to_messages=True,
    )

    def run(self, logs: list, topic: str, use_cache: bool = True) -> Iterator[RunResponse]:
        try:
            logger.info(f"Generating a summary on: {topic}")
            logs.append(f"Generating a summary on: {topic}")

            # Check cache
            if use_cache and "summaries" in self.session_state:
                logger.info("Checking if cached summary exists")
                logs.append("Checking if cached summary exists")
                for cached_summary in self.session_state["summaries"]:
                    if cached_summary["topic"] == topic:
                        logger.info("Found cached summary")
                        logs.append("Found cached summary")
                        yield RunResponse(content=cached_summary["summary"])
                        return

            # Step 1: Search and validate results
            all_papers = []
            for i in range(3):
                response = self.searcher.run(topic)
                if response and response.content:
                    all_papers.append(response.content)
                    logger.info(f"Search {i+1} completed successfully")
                else:
                    logger.warning(f"Search {i+1} returned no results")

            if not all_papers:
                yield RunResponse(content="No papers found for the given topic.")
                return

            # Combine results
            combined_input = "\n\n".join(all_papers)

            # Step 2: Generate summary with validation
            final_summary = ''
            for response in self.summarizer.run(combined_input, stream=True):
                i=0
                if response and i==1:
                    logger.info("Summary generated successfully")
                    i+=1
                    
                if response and response.content:
                    final_summary += response.content


            if not final_summary:
                yield RunResponse(content="Failed to generate summary.")
                return

            # Cache valid results
            if "summaries" not in self.session_state:
                self.session_state["summaries"] = []
            self.session_state["summaries"].append({"topic": topic, "summary": final_summary})

            yield RunResponse(content=final_summary)

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            yield RunResponse(content=f"Error: {str(e)}")

if __name__ == "__main__":
    paperai = PaperSummaryGenerator()
    logs = []
    result = paperai.run(logs, "language models")
    for res in result:
        print(res.content)
