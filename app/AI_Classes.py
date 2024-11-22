from phi.agent import Agent
from phi.model.openai.like import OpenAILike
from phi.tools.arxiv_toolkit import ArxivToolkit
from phi.tools.baidusearch import BaiduSearch
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.tools.pubmed import PubmedTools
from phi.tools.calculator import Calculator
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.file import FileTools
import StructureOutput
import CodeAIWorkflow


def create_storage(session_id: str, name: str) -> SqlAgentStorage:
    return SqlAgentStorage(
        table_name=session_id,
        db_file=f"./../DataBase/{name}.db"  # Changed to use workflow database
    )

# Add toolsTeamStorage definition at the top after create_storage
toolsTeamStorage = create_storage(CodeAIWorkflow.user_session_id, "toolsTeam")

userInterfaceCommunicator = Agent(
    storage=create_storage(CodeAIWorkflow.user_session_id, "userInterfaceCommunicator"),
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
    "Focus on data processing, search, analysis, and visualization tasks.",
    "Don't check the tools and libraries, all the tools and libraries are available in the environment.",
    ],
    add_history_to_messages=True,
    markdown=True,
    debug_mode=True
)

#should know what tools it could use and structure its output.AND CURRENT DIR LIST
taskSpliter = Agent(
    storage=create_storage(CodeAIWorkflow.user_session_id, "taskSpliter"),
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
    storage=create_storage(CodeAIWorkflow.user_session_id, "outputCheckerAndSummary"),
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
    storage=toolsTeamStorage,
    name="Python Excutor",
    role="Use python to solve the problem.",
    tools=[PythonTools(), FileTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

shellExcutor = Agent(
    storage=toolsTeamStorage,
    name="Shell Excutor",
    role="Use shell to solve the problem.",
    tools=[ShellTools()],
    add_datetime_to_instructions=True,
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

pubmedSeacher = Agent(
    storage=toolsTeamStorage,
    name="Pubmed Searcher",
    role="Searches PubMed for articles and summary the article.",
    tools=[PubmedTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

arxivSearcher = Agent(
    storage=toolsTeamStorage,
    name="Arxiv Searcher",
    role="Searches Arxiv for articles and summary the article.",
    tools=[ArxivToolkit()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

paperSearcher = Agent(
    storage=toolsTeamStorage,
    name="paper Searcher",
    role="Searches Arxiv and Pubmed for articles and summary the article.",
    tools=[ArxivToolkit(), PubmedTools()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

webSeacher = Agent(
    storage=toolsTeamStorage,
    name="Web Searcher",
    role="Search from and summary web.",
    tools=[BaiduSearch()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

calculatorai = Agent(
    storage=toolsTeamStorage,
    name="Calculator",
    role="Calculate the expression.",
    tools=[        
           Calculator(
            add=True,
            subtract=True,
            multiply=True,
            divide=True,
            exponentiate=True,
            factorial=True,
            is_prime=True,
            square_root=True,
        )],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    )
)

# toolsTeam = Agent(
#     name="Tools Team",
#     team=[pythonExcutor, shellExcutor, pubmedSeacher],
#     storage = toolsTeamStorage,
#     model=OpenAILike(
#         id="yi-large-fc",
#         api_key="1352a88fdd3844deaec9d7dbe4b467d5",
#         base_url="https://api.lingyiwanwu.com/v1",
#     ),
#     description="An AI that executes bioinformatics tasks using available Python packages and system tools. If the input don't need py or shell, you could search something from the web to get the better answer from web or just return your answer.",
#     instruction=[
#         "The following tools and libraries are available in the environment: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, phidata, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, wget, curl, bzip2, ca-certificates, libglib2.0-0, libx11-6, libxext6, libsm6, libxi6, python3.10."
#         "Execute only tasks that use existing Python packages and system tools.",
#         "Process biological data using available resources.",
#         "If a command is not a task skip it and return NOT A TASK.",
#         "Focus on data analysis, file operations, and calculations.",
#         "If a task cannot be executed, report the reason and suggest alternative approaches.",
#     ],
#     add_history_to_messages=False,
#     show_tool_calls=True,
#     markdown=True,
# )

