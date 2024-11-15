import uuid
from AIs import TalkAI, TaskSplitterAI, OutputCheckerAI, ToolsAI  # 导入AI类
import os   
 
"""
    你可以使用这个做测试，但是！不要在这里写这个流程，
    app\Test\WorkFlowTest.py里面有一个完全一样的文件，
    你应该在那里写测试，这里只是用来展示给你看，怕你找不到。
"""





def main() -> None:
    session_id = str(uuid.uuid4())
    
    # Initialize AI instances with debug_mode enabled
    talk_ai = TalkAI(table_name=session_id, debug_mode=True, stream=True)
    task_splitter_ai = TaskSplitterAI(table_name=session_id, debug_mode=True)
    output_checker_ai = OutputCheckerAI(table_name=session_id, debug_mode=True)
    tools_ai = ToolsAI(table_name=session_id, debug_mode=True)
    
    messages = []
    
    while True:
        prompt = input("Enter your message (or type 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break
        messages.append({"role": "user", "content": prompt})
        
        # Process user input and generate task plan
        task_plan = talk_ai.process_input(user_input=prompt)
        messages.append({"role": "assistant", "content": task_plan})

        # Split tasks into a list
        task_list = task_splitter_ai.split_tasks(task_plan=task_plan)

        execution_results = []
        # Execute each task step
        for task in task_list:
            result = tools_ai.execute_task(task)
            execution_results.append(result)

        # Combine execution results
        combined_results = "\n".join(execution_results)

        # Check output
        output_feedback = output_checker_ai.check_output(output=combined_results)
        
        # Display feedback to user
        messages.append({"role": "assistant", "content": output_feedback})
        
        # Display all messages
        for message in messages:
            if message.get("role") in ["system", "tool"]:
                continue
            message_role = message.get("role")
            content = message.get("content")
            print(f"{message_role}: {content}")

if __name__ == "__main__":
    main()