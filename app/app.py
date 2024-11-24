from flask import Flask, request, jsonify
from phi.storage.workflow.sqlite import SqlWorkflowStorage

from CodeAIWorkFlow import CodeAIWorkflow, user_session_id  # 假设该类在 your_module 中

app = Flask(__name__)

workflow_instance = CodeAIWorkflow(
    session_id=user_session_id,  # Use the user provided or generated session_id
    storage=SqlWorkflowStorage(
        table_name=user_session_id,
        db_file="./../Database/CodeWorkflows.db",
    ),
)

@app.route('/run_workflow', methods=['POST'])
def run_workflow():
    try:
        user_input = request.json.get('user_input', '')
        if not user_input:
            return jsonify({'error': 'user_input is required'}), 400

        response_data = []
        for response in workflow_instance.run(user_input=user_input):
            response_data.append({
                'run_id': response.run_id,
                'event': response.event.name,
                'content': response.content
            })

        return jsonify({'workflow_results': response_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
