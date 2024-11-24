from flask import Flask, render_template, request, jsonify
from Workflow import classExample

app = Flask(__name__)

workflow = classExample()

@app.route('/')
def index():
    return render_template("test1.html")

@app.route('/test', methods=['POST'])
def test():
    user_input = request.form['user_input']

    if not user_input:
        return jsonify({'status': 'error'}),400

    result = workflow.run(user_input)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)