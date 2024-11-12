# main.py
from flask import Flask, render_template, jsonify, request
from jira_client1 import get_all_projects, get_timelogs_for_project, get_all_employees_timelogs,get_employee_timelogs
import os
from datetime import datetime

app = Flask(__name__)

# Load environment variables
os.environ["JIRA_API_TOKEN"]
os.environ["JIRA_EMAIL"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects', methods=['GET'])
def fetch_projects():
    try:
        projects = get_all_projects()
        return jsonify(projects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/project_timelogs', methods=['POST'])
def project_timelogs():
    project_id = request.json.get('project_id')
    try:
        timelogs_by_member = get_timelogs_for_project(project_id)
        return jsonify(timelogs_by_member)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# New route for fetching complete employee timelogs report
@app.route('/all_employees_timelogs', methods=['GET'])
def all_employees_timelogs():
    fields = request.args.getlist('fields')  # Optional field filter
    date = request.args.get('date')  # Add date filter
    try:
        timelogs = get_all_employees_timelogs(fields=fields, date=date)  # Pass date
        return jsonify(timelogs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/employee_timelogs', methods=['GET'])
def employee_timelogs():
    employee_name_or_id = request.args.get('employee')
    fields = request.args.getlist('fields')
    date = request.args.get('date')  # Add date filter
    if not employee_name_or_id:
        return jsonify({"error": "Employee name or ID required"}), 400
    try:
        timelogs = get_employee_timelogs(employee_name_or_id, fields=fields, date=date)  # Pass date
        return jsonify(timelogs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
