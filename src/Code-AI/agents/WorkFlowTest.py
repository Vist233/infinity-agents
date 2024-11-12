
import uuid
from AIs import TalkAI, TaskSplitterAI, OutputCheckerAI  # 导入AI类
import os

def main() -> None:
    session_id = str(uuid.uuid4())
    
    # Initialize AI instances with debug mode enabled
    talk_ai = TalkAI(table_name=session_id, debug=True)
    task_splitter_ai = TaskSplitterAI(table_name=session_id, debug=True)
    output_checker_ai = OutputCheckerAI(table_name=session_id, debug=True)
    
    messages = []
    
    while True:
        prompt = input("Enter your message (or type 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break
        messages.append({"role": "user", "content": prompt})
        
        # Process user input and generate task plan
        task_plan = talk_ai.process_input(user_input=prompt)
        messages.append({"role": "assistant", "content": task_plan})
        
        # Process task plan
        execution_result = task_splitter_ai.process_task(task_plan=task_plan)
        
        # Check output
        output_feedback = output_checker_ai.check_output(output=execution_result)
        
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