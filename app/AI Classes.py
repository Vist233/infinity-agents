from phi.agent import Agent
from phi.model.openai.like import OpenAILike
from phi.tools.googlesearch import GoogleSearch
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.tools.pubmed import PubmedTools
from phi.storage.agent.sqlite import SqlAgentStorage
import uuid

session_id = str(uuid.uuid4())

userInterfaceCommunicatorStorage = SqlAgentStorage(
            table_name=session_id,
            db_file="./../DataBase/userInterfaceCommunicator.db"
        ),

outputCheckerStorage = SqlAgentStorage(
            table_name=session_id,
            db_file="./../DataBase/outputChecker.db"
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
    add_history_to_messages=True,
    markdown=True
)

taskSpliter = Agent(
    storage = taskSpliterStorage,
    model=OpenAILike(
        id="yi-lightning",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    add_history_to_messages=True,
    markdown=True
)

outputChecker = Agent(
    storage = outputCheckerStorage,
    model=OpenAILike(
        id="yi-lightning",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    add_history_to_messages=False,
    markdown=True
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

toolsTeam = Agent(
    name="Tools Team",
    team=[pythonExcutor, shellExcutor],
    storage = toolsTeamStorage,
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
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
    add_history_to_messages=False,
    show_tool_calls=True,
    markdown=True,
)

