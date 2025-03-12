import os
import json
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

def load_chunked_data_to_json():
    load_dotenv(override=True)

    key = os.environ.get("API_KEY")

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

    def chunk_text(text, chunk_size=50):
        #chunk by words
        text_list = text.split()
        return [" ".join(text_list[i:i+chunk_size]) for i in range(0, len(text_list), chunk_size)]

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

        chunked_text = chunk_text(full_text)

        bill_data = {
            "title": title,
            "bill_number": bill_number,
            "update_date": update_date,
            "origin_chamber": origin_chamber,
            "bill_type": bill_type,
            "full_text_link": full_text_link,
            "full_text": full_text,
            "chunked_text": chunked_text 
        }
        
        final_output.append(bill_data)

    with open("data/chunked_data.json", "w") as file:
        json.dump(final_output, file, indent=4)
