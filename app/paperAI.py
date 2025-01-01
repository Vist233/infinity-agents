from typing import Iterator
from phi.agent import Agent
from phi.workflow import Workflow, RunResponse
from phi.utils.log import logger
from phi.model.openai.like import OpenAILike
from phi.tools.pubmed import PubmedTools
from phi.tools.arxiv_toolkit import ArxivToolkit
from config import API_KEY
from phi.model.deepseek import DeepSeekChat
import os
from typing import Optional, Dict, Iterator
from pydantic import BaseModel, Field

# Get the API key from environment variables OR set your API key here
API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

class NewsArticle(BaseModel):
    title: str = Field(..., description="Title of the article.")
    url: str = Field(..., description="Link to the article.")
    summary: Optional[str] = Field(..., description="Summary of the article if available.")
    
class SearchResults(BaseModel):
    articles: list[NewsArticle]

class ScrapedArticle(BaseModel):
    title: str = Field(..., description="Title of the article.")
    url: str = Field(..., description="Link to the article.")
    summary: Optional[str] = Field(..., description="Summary of the article if available.")
    content: Optional[str] = Field(
        ...,
        description="Content of the in markdown format if available. Return None if the content is not available or does not make sense.",
    )

class PaperSummaryGenerator(Workflow):
    searcher: Agent = Agent(
        model=DeepSeekChat(api_key=API),
        tools=[ArxivToolkit()],
        instructions=[
            "Given a topic, search for 10 articles and return the 5 most relevant articles.",
        ],
        add_history_to_messages=True,
        response_model=SearchResults,
    )

    summarizer: Agent = Agent(
        model=DeepSeekChat(api_key=API),
        instructions=[
            "Given a url, scrape the article and return the title, url, and markdown formatted content.",
            "If the content is not available or does not make sense, return None as the content.",
        ],
        # response_model=ScrapedArticle,
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
            for i in range(1):
                response = self.searcher.run(topic)
                if response and response.content:
                    # Format the articles data
                    articles_text = []
                    for article in response.content.articles:
                        article_info = f"Title: {article.title}\nURL: {article.url}\nSummary: {article.summary}\n"
                        articles_text.append(article_info)
                    all_papers.extend(articles_text)
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

