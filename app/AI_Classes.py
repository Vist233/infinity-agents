from phi.agent import Agent
from phi.model.openai.like import OpenAILike
from phi.playground import Playground, serve_playground_app
from phi.tools.googlesearch import GoogleSearch
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.tools.pubmed import PubmedTools
from phi.storage.agent.sqlite import SqlAgentStorage
import uuid
import StructureOutput

session_id = str(uuid.uuid4())

userInterfaceCommunicatorStorage = SqlAgentStorage(
            table_name=session_id,
            db_file="./../DataBase/userInterfaceCommunicator.db"
        )

outputCheckerAndSummaryStorage = SqlAgentStorage(
            table_name=session_id,
            db_file="./../DataBase/outputCheckerAndSummary.db"
        )

toolsTeamStorage = SqlAgentStorage(
            table_name=session_id,
            db_file="./../DataBase/toolsTeam.db"
        )

taskSpliterStorage = SqlAgentStorage(
            table_name=session_id,
            db_file="./../DataBase/taskSpliter.db"
        )



userInterfaceCommunicator = Agent(
    storage = userInterfaceCommunicatorStorage,
    model=OpenAILike(
        id="yi-lightning",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI assistant that converts user requests into executable bioinformatics tasks.",
    instruction=[
    "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, phidata, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libxext6, libsm6, libxi6, python3.10.",
    "Break down complex tasks into smaller, executable steps.",
    "Avoid generating tasks that require external software installation or system configuration.",
    "Focus on data processing, analysis, and visualization tasks.",
    "If the enviroment's tools could not solve the problem, you could search something from the web to get the better answer from web or just return your answer.",
    ],
    add_history_to_messages=True,
    markdown=True,
    debug_mode=True
)

#should know what tools it could use and structure its output.AND CURRENT DIR LIST
taskSpliter = Agent(
    storage = taskSpliterStorage,
    model=OpenAILike(
        id="yi-lightning",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI that validates and distributes executable tasks to ToolsAI. The output should just a json format and not contain\"\`\`\`json \`\`\`\"",
    instruction=[
        "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, phidata, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libxext6, libsm6, libxi6, python3.10.",
        "Filter out any non-executable or invalid tasks.",
        "If the input contains the task that install new software or modify system configurations, ignore it",
        "If the input is not a task, return NOT A TASK.",
    ],
    add_history_to_messages=True,
    markdown=True,
    debug_mode=True,
    response_model=StructureOutput.taskSpliterAIOutput,
)

#structure its output
outputCheckerAndSummary = Agent(
    storage = outputCheckerAndSummaryStorage,
    model=OpenAILike(
        id="yi-medium-200k",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI that validates task outputs and execution status or summary the excution situation. The output should just a json format and not contain\"\`\`\`json \`\`\`\"",
    instruction=[
        "Verify that task outputs are complete and valid.",
        "Check for execution errors or tool limitations.",
        "Ensure results meet bioinformatics quality standards.",
        "Report any execution failures or incomplete tasks.",
        "Validate data formats and analysis results."
    ],
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    response_model=StructureOutput.outputCheckerOutput,
)



pythonExcutor = Agent(
    name="python excutor",
    role="Use python to solve the problem.",
    tools=[PythonTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

shellExcutor = Agent(
    name="shell excutor",
    role="Use shell to solve the problem.",
    tools=[ShellTools()],
    add_datetime_to_instructions=True,
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

webSeacher = Agent(
    name="Google Searcher",
    role="Reads articles from URLs.",
    tools=[GoogleSearch()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

pubmedSeacher = Agent(
    name="Pubmed Searcher",
    role="Searches PubMed for articles and summary the article.",
    tools=[PubmedTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

yiSeacher = Agent(
    name="Yi Searcher",
    role="Search from and summary web.",
    tools=[],
    model=OpenAILike(
        id="yi-large-rag",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

toolsTeam = Agent(
    name="Tools Team",
    team=[pythonExcutor, shellExcutor, webSeacher, pubmedSeacher],
    storage = toolsTeamStorage,
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="An AI that executes bioinformatics tasks using available Python packages and system tools. If the input don't need py or shell, you could search something from the web to get the better answer from web or just return your answer.",
    instruction=[
        "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, phidata, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libxext6, libsm6, libxi6, python3.10."
        "Execute only tasks that use existing Python packages and system tools.",
        "Process biological data using available resources.",
        "If a command is not a task skip it and return NOT A TASK.",
        "Focus on data analysis, file operations, and calculations.",
        "If a task cannot be executed, report the reason and suggest alternative approaches.",
    ],
    add_history_to_messages=False,
    show_tool_calls=True,
    markdown=True,
)

#How to deal with the PICTURE? use vision model seperately?
searchSummaryTeam = Agent(
    name="Search and Summary Team",
    team=[pubmedSeacher, yiSeacher],
    storage = toolsTeamStorage,
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="comprehensive the knowledge from pubmed and website to replay the user.",
    instruction=[
        "Search the web and pubmed to get what the user want."
    ],
    add_history_to_messages=True,
    show_tool_calls=True,
    markdown=True,
)

