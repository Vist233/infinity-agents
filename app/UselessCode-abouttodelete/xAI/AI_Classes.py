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
from phi.model.xai import xAI

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
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
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
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
    description="An AI that validates and distributes executable tasks to ToolsAI.",
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
    structured_outputs=False,
)

#structure its output
outputCheckerAndSummary = Agent(
    storage = outputCheckerAndSummaryStorage,
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
    description="An AI that validates task outputs and execution status or summary the excution situation.",
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
    structured_outputs=False,
)



pythonExcutor = Agent(
    name="python excutor",
    role="Use python to solve the problem.",
    tools=[PythonTools()],
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
)

shellExcutor = Agent(
    name="shell excutor",
    role="Use shell to solve the problem.",
    tools=[ShellTools()],
    add_datetime_to_instructions=True,
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
)

webSeacher = Agent(
    name="Google Searcher",
    role="Reads articles from URLs.",
    tools=[GoogleSearch()],
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
)

pubmedSeacher = Agent(
    name="Pubmed Searcher",
    role="Searches PubMed for articles and summary the article.",
    tools=[PubmedTools()],
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
)

yiSeacher = Agent(
    name="Yi Searcher",
    role="Search from and summary web.",
    tools=[],
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
)

toolsTeam = Agent(
    name="Tools Team",
    team=[pythonExcutor, shellExcutor, yiSeacher, pubmedSeacher],
    storage = toolsTeamStorage,
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
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
	model=xAI(
		id="grok-beta",
		api_key="xai-OAKIb9pRoafOYVfvXFR0ekE4nR6Ethvhj2rgM6bAOVxoKKIspe6N3gVhuERVednZu1RCevuCUmvrnYfj"
	),
    description="comprehensive the knowledge from pubmed and website to replay the user.",
    instruction=[
        "Search the web and pubmed to get what the user want."
    ],
    add_history_to_messages=True,
    show_tool_calls=True,
    markdown=True,
)
    
