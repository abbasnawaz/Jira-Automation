from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

load_dotenv()

FROM_EMAIL = 'abbasnawaz125@gmail.com'
TO_EMAIL = '191370041@gift.edu.pk'
SUBJECT = 'Jira Report'
BODY = 'Please find the attach file for the JIRA report'

SMTP_SERVER = "smtp.gmail.com"
PORT = 587
PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
CSV_FILE = 'Report.csv'

data = '''
[
    {
        "name": "John",
        "age": 30,
        "city": "New York"
    },
    {
        "name": "Jane",
        "age": 25,
        "city": "San Francisco"
    }
]
'''

json_data = json.loads(data)

def csv_file():
    csv_obj = open(CSV_FILE, 'w')
    csv_writer = csv.writer(csv_obj)
    header = json_data[0].keys()
    csv_writer.writerow(header)
    for item in json_data:
        csv_writer.writerow(item.values())
    csv_obj.close()

def send_email():
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY, 'plain'))

    try:
        # with open(path_to_file,'rb') as file:
        #     msg.attach(MIMEApplication(file.read(), Name="Report.csv"))
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
            print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

scheduler = BlockingScheduler()
scheduler.add_job(send_email, CronTrigger(hour=22, minute=0))

scheduler.start()