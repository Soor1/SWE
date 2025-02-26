import os
import json
import requests

key = os.getenv("API_KEY")

output = []

response = requests.get(f"https://api.congress.gov/v3/bill?api_key={key}")
bills = response.json().get("bills", [])

for bill in bills:
    bill_number = bill["number"]
    title = bill["title"]
    update_date = bill["updateDate"]
    origin_chamber = bill["originChamber"]
    bill_type = bill["type"]
    
    second_url = f"https://api.congress.gov/v3/bill/119/hr/{bill_number}/text?api_key={key}"
    second_response = requests.get(second_url)
    text_versions = second_response.json().get("textVersions", [])
    
    full_text_link = "No PDF available"
    for version in text_versions:
        for format_item in version.get("formats", []):
            if format_item["type"] == "PDF":
                full_text_link = format_item["url"]
                break
    
    bill_data = {
        "Title": title,
        "Bill_Number": bill_number,
        "Update_Date": update_date,
        "Origin_Chamber": origin_chamber,
        "Bill_Type": bill_type,
        "Full_Text_Link": full_text_link
    }
    output.append(bill_data)

with open("final_output.json", "w") as file:
    json.dump(output, file, indent=4)
