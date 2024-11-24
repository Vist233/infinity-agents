from phi.agent import Agent
from phi.playground import Playground, serve_playground_app
from phi.tools.python import PythonTools
from phi.tools.shell import ShellTools
from phi.model.openai.like import OpenAILike
# from AI_Classes import toolsTeamStorage
from phi.tools.pubmed import PubmedTools
from phi.tools.arxiv_toolkit import ArxivToolkit

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

pubmedSearcher = Agent(
    tools=[ArxivToolkit()],
    model=OpenAILike(
        id="yi-large-fc",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ), 
    show_tool_calls=True,
    debug_mode=True,
    arbitrary_types_allowed=True
)

# toolsTeam = Agent(
#     name="Tools Team",
#     team=[pythonExcutor, shellExcutor],
#     storage = toolsTeamStorage,
#     model=OpenAILike(
#         id="yi-large-fc",
#         api_key="1352a88fdd3844deaec9d7dbe4b467d5",
#         base_url="https://api.lingyiwanwu.com/v1",
#     ),
#     description="An AI that executes bioinformatics tasks using available Python packages and system tools.",
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

# pp = Playground(agents=[pythonExcutor,shellExcutor,toolsTeam]).get_app()

# if __name__ == "__main__":
#     serve_playground_app("playground:app", reload=True)

taskSpliter = Agent(
    model=OpenAILike(
        id="yi-large",
        api_key="1352a88fdd3844deaec9d7dbe4b467d5",
        base_url="https://api.lingyiwanwu.com/v1",
    ),
    description="""Task analysis and distribution agent that:
    1. Validates input tasks for executability
    2. Breaks down complex operations into atomic tasks
    3. Assigns appropriate executors to each task
    4. Ensures proper task sequencing""",
    instruction=[
        "You are a specialized task analyzer for bioinformatics workflows.",
        "Available tools include: raxml-ng, modeltest, mafft, CPSTools, vcftools, gatk, biopython, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, HTSeq, PyVCF, pysam, samtools, bwa, snpeff, and basic Unix tools.",
        "For each task analyze and decide whether it needs Python (data processing, analysis, visualization) or Shell (command line tools, file operations) execution.",
        "Always validate tasks for:\n- Data availability\n- Tool compatibility\n- Resource requirements\n- Proper sequencing",
        "Provide clean, executable code snippets without installation or config steps.",
        "Output format must be valid JSON:\n{\"tasks\": [{\"id\": \"1\", \"description\": \"detailed task description\", \"code_snippet\": \"executable code\", \"dependencies\": [\"pythonExecutor/shellExecutor\"], \"result\": null}]}"
    ],
    add_history_to_messages=True,
    arbitrary_types_allowed=True
)


taskSpliter.print_response("请你使用mafft对当前文件夹中的seq2.fasta文件进行多序列比对。")