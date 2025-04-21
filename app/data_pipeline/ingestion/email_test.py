# future improvments???
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

API_URL = 'https://api.congress.gov/v3/summaries?fromDateTime={yesterday}T00:00:00Z&toDateTime={today}T00:00:00Z&sort=updateDate+asc&api_key={key}'  
FROM_EMAIL = 'my_email'
FROM_PASSWORD = 'my_password' 
TO_EMAIL = 'output_email'
SUBJECT = 'Your Daily Legislation Newsletter'

def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'API returned status code {response.status_code}')

def format_html(data):
    html = "<h1>Today's Futurama Characters</h1><ul>"
    for character in data[:5]: 
        html += f"<li><strong>{character['name']['first']} {character['name']['last']}</strong> — {character['species']}</li>"
    html += "</ul>"
    return html

def send_email(html_content):
    msg = MIMEMultipart('alternative')
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = SUBJECT

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(FROM_EMAIL, FROM_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        print("Newsletter sent successfully!")

if __name__ == "__main__":
    try:
        data = fetch_data()
        html = format_html(data)
        send_email(html)
    except Exception as e:
        print(f"error")
