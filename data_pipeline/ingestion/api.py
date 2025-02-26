import os
import json
import requests
import xml.etree.ElementTree as ET

key = os.getenv("API_KEY")

final_output = []

response = requests.get(f"https://api.congress.gov/v3/bill?api_key={key}")
bills = response.json().get("bills", [])

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

for bill in bills:
    bill_number = bill["number"]
    title = bill["title"]
    update_date = bill["updateDate"]
    origin_chamber = bill["originChamber"]
    bill_type = bill["type"]
    
    second_url = f"https://api.congress.gov/v3/bill/119/hr/{bill_number}/text?api_key={key}"
    second_response = requests.get(second_url)
    text_versions = second_response.json().get("textVersions", [])
    
    full_text_link = "No XML available"
    for version in text_versions:
        for format_item in version.get("formats", []):
            if format_item["type"] == "Formatted XML": 
                full_text_link = format_item["url"]
                break
    
    full_text = "No XML available"
    if full_text_link != "No XML available":
        full_text = extract_text_from_xml(full_text_link)

    bill_data = {
        "Title": title,
        "Bill_Number": bill_number,
        "Update_Date": update_date,
        "Origin_Chamber": origin_chamber,
        "Bill_Type": bill_type,
        "Full_Text_Link": full_text_link,
        "Full_Text": full_text
    }
    final_output.append(bill_data)

with open("final_output.json", "w") as file:
    json.dump(final_output, file, indent=4)
