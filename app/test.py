from phi.agent import Agent
from phi.playground import Playground, serve_playground_app
from phi.tools.python import PythonTools
from phi.tools.shell import ShellTools
from phi.model.openai.like import OpenAILike
from app.AI_Classes import toolsTeamStorage

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

pp = Playground(agents=[pythonExcutor,shellExcutor,toolsTeam]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)