import os
import json
import requests
import re
import xml.etree.ElementTree as ET

def extract_text_from_xml(xml_url):
    try:
        response = requests.get(xml_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            text = " ".join([element.text for element in root.iter() if element.text])
            return text.strip()
        else:
            return "Error retrieving XML"
    except Exception as e:
        return "Error fetching XML"

key = os.getenv("API_KEY")
final_output = []

response = requests.get(f"https://api.congress.gov/v3/bill?api_key={key}")
bills = response.json().get("bills", [])

for bill in bills:
    bill_number = int(bill["number"])
    congress = bill["congress"]
    title = bill["title"]
    update_date = bill["updateDate"]
    origin_chamber = bill["originChamber"]
    bill_type = bill["type"].lower()
    
    response2 = requests.get(f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}/summaries?api_key={key}")
    summaries = response2.json().get("summaries", [])
    summary_text = " ".join([summary["text"] for summary in summaries])
        
    response3 = requests.get(f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}/text?api_key={key}")
    text_versions = response3.json().get("textVersions", [])
    full_text = " ".join([
        extract_text_from_xml(fmt["url"])
        for text_version in text_versions
        for fmt in text_version["formats"]
        if fmt["type"] == "Formatted XML"
    ])
    
    bill_data = { 
        "bill_number": bill_number,
        "congress": congress,
        "title": title,
        "update_date": update_date,
        "origin_chamber": origin_chamber,
        "bill_type": bill_type,
        "summaries": summary_text,
        "full_text": full_text
    }
    
    final_output.append(bill_data)
    
with open("final_output.json", "w") as file:
    json.dump(final_output, file, indent=4)