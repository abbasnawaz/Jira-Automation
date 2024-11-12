
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

JIRA_DOMAIN = "https://hypernym.atlassian.net/"
API_TOKEN = os.getenv("JIRA_API_TOKEN")
EMAIL = os.getenv("JIRA_EMAIL")

HEADERS = {
    "Authorization": f"{requests.auth._basic_auth_str(EMAIL, API_TOKEN)}",
    "Content-Type": "application/json",
}

def get_all_projects():
    """
    Fetch all projects from Jira.
    """
    url = f"{JIRA_DOMAIN}/rest/api/3/project"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def get_timelogs_for_project(project_id):
    """
    Fetch time logs for all users in a specified project.
    """
    search_url = f"{JIRA_DOMAIN}/rest/api/3/search"
    jql = f"project = {project_id}"
    
    query = {
        "jql": jql,
        "fields": ["worklog", "assignee"],
        "maxResults": 100  # Adjust as needed
    }
    
    response = requests.get(search_url, headers=HEADERS, params=query)
    timelogs_by_member = {}

    if response.status_code == 200:
        issues = response.json().get("issues", [])
        
        for issue in issues:
            worklogs = issue.get("fields", {}).get("worklog", {}).get("worklogs", [])
            
            # Collect time logs for each worklog author
            for log in worklogs:
                author = log.get("author", {}).get("displayName")
                time_spent = log.get("timeSpent")
                created = log.get("created")[:10]

                # Aggregate time logs by each author
                if author not in timelogs_by_member:
                    timelogs_by_member[author] = []
                
                timelogs_by_member[author].append({
                    "issue_id": issue.get("id"),
                    "time_spent": time_spent,
                    "created": created
                })
        
        return timelogs_by_member
    else:
        response.raise_for_status()




def get_all_employees_timelogs(fields=None, date=None):
    search_url = f"{JIRA_DOMAIN}/rest/api/3/search"
    jql = "worklogAuthor is not EMPTY"
    default_fields = ["worklog", "assignee", "summary", "status", "updated"]
    selected_fields = fields if fields else default_fields

    query = {
        "jql": jql,
        "fields": selected_fields,
        "maxResults": 10
    }
    print(query)
    timelogs_by_employee = {}
    start_at = 0

    # Process date filter
    date_filter = date


    # Fetch data with pagination
    while True:
        query["startAt"] = start_at
        response = requests.get(search_url, headers=HEADERS, params=query)

        if response.status_code == 200:
            data = response.json()
            issues = data.get("issues", [])

            for issue in issues:
                worklogs = issue.get("fields", {}).get("worklog", {}).get("worklogs", [])
                
                for log in worklogs:
                    created_date = log.get("created", "")[:10]

                    # Filter by date if specified
                    if date_filter and created_date != date_filter:
                        continue

                    author = log.get("author", {}).get("displayName")
                    time_spent = log.get("timeSpent")
                    summary = issue.get("fields", {}).get("summary")
                    status = issue.get("fields", {}).get("status", {}).get("name")
                    updated = issue.get("fields", {}).get("updated", "")[:10]

                    if author not in timelogs_by_employee:
                        timelogs_by_employee[author] = []
                    
                    log_entry = {
                        "issue_id": issue.get("id"),
                        "time_spent": time_spent,
                        "created": created_date
                    }

                    if "summary" in selected_fields and summary:
                        log_entry["summary"] = summary
                    if "status" in selected_fields and status:
                        log_entry["status"] = status
                    if "updated" in selected_fields and updated:
                        log_entry["updated"] = updated

                    timelogs_by_employee[author].append(log_entry)

            start_at += len(issues)
            if len(issues) < query["maxResults"]:
                break
        else:
            response.raise_for_status()

    return timelogs_by_employee



def parse_time_spent(time_spent):
    """Helper function to convert time spent (e.g., '2h 30m') into hours as a float."""
    total_hours = 0
    if time_spent:
        time_units = time_spent.split()
        for unit in time_units:
            if 'h' in unit:
                total_hours += int(unit.replace('h', ''))
            elif 'm' in unit:
                total_hours += int(unit.replace('m', '')) / 60  
    return total_hours

def get_employee_timelogs(employee_name_or_id, fields=None, date=None):
    search_url = f"{JIRA_DOMAIN}/rest/api/3/search"
    jql = f"worklogAuthor = '{employee_name_or_id}'"
    default_fields = ["worklog", "summary", "status", "project", "issuetype"]
    selected_fields = fields if fields else default_fields

    query = {
        "jql": jql,
        "fields": selected_fields,
        "maxResults": 100
    }

    employee_timelogs = []
    total_hours = 0  # Initialize total hours counter
    start_at = 0

    while True:
        query["startAt"] = start_at
        response = requests.get(search_url, headers=HEADERS, params=query)

        if response.status_code == 200:
            data = response.json()
            issues = data.get("issues", [])

            for issue in issues:
                worklogs = issue.get("fields", {}).get("worklog", {}).get("worklogs", [])
                
                for log in worklogs:
                    author_id = log.get("author", {}).get("accountId")
                    author_name = log.get("author", {}).get("displayName")
                    
                    if employee_name_or_id in [author_id, author_name]:
                        created_date = log.get("created", "")[:10]
                        if date and created_date != date:
                            continue  # Skip entries that don’t match the date

                        # Retrieve additional fields
                        time_spent = log.get("timeSpent")
                        worklog_id = log.get("id")  # Worklog ID
                        summary = issue.get("fields", {}).get("summary")
                        status = issue.get("fields", {}).get("status", {}).get("name")
                        project = issue.get("fields", {}).get("project", {}).get("name")
                        issue_type = issue.get("fields", {}).get("issuetype", {}).get("name")
                        issue_key = issue.get("key")  # Unique issue key

                        # Parse and accumulate total hours
                        total_hours += parse_time_spent(time_spent)

                        log_entry = {
                            "issue_id": issue.get("id"),
                            "issue_key": issue_key,
                            "summary": summary,
                            "status": status,
                            "project": project,
                            "issue_type": issue_type,
                            "worklog_id": worklog_id,
                            "time_spent": time_spent,
                            "created": created_date
                        }

                        employee_timelogs.append(log_entry)

            start_at += len(issues)
            if len(issues) < query["maxResults"]:
                break
        else:
            response.raise_for_status()

    return {"total_hours": total_hours, "logs": employee_timelogs}
