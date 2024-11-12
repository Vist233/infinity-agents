import streamlit as st
from AIs import TalkAI, TaskSplitterAI, OutputCheckerAI  # 导入AI类
import os
import uuid
import subprocess
from phi.agent import Agent
from phi.tools.shell import ShellTools
from phi.tools.python import PythonTools
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.agent import Agent, RunResponse
from phi.model.openai.like import OpenAILike

def main() -> None:
    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    

    session_id = st.session_state["session_id"]

    # Initialize AI instances with session_id as table_name
    talk_ai = TalkAI(table_name=session_id)
    task_splitter_ai = TaskSplitterAI(table_name=session_id)
    output_checker_ai = OutputCheckerAI(table_name=session_id)

    # 接收用户输入
    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

        # 处理用户输入并使用 TalkAI 生成任务计划
        task_plan = talk_ai.process_input(user_input=prompt)
        st.session_state["messages"].append({"role": "assistant", "content": task_plan})

        # 使用 TaskSplitterAI 处理任务计划
        execution_result = task_splitter_ai.process_task(task_plan=task_plan)

        # 使用 OutputCheckerAI 检查输出
        output_feedback = output_checker_ai.check_output(output=execution_result)

        # 将反馈展示给用户
        st.session_state["messages"].append({"role": "assistant", "content": output_feedback})

    # 显示聊天消息
    for message in st.session_state["messages"]:
        # Skip system and tool messages
        if message.get("role") in ["system", "tool"]:
            continue
        # Display the message
        message_role = message.get("role")
        if message_role is not None:
            with st.chat_message(message_role):
                content = message.get("content")
                if isinstance(content, list):
                    for item in content:
                        if item["type"] == "text":
                            st.write(item["text"])
                        elif item["type"] == "image_url":
                            st.image(item["image_url"]["url"], use_column_width=True)
                else:
                    st.write(content)

if __name__ == "__main__":
    main()
