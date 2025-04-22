import os
import json
import requests
import time
import re

#fixed summary stuff
def chunk_summary(summary, min_length=200, max_length=250):
    chunks = []
    while summary:
        if len(summary) <= max_length:
            chunks.append(summary.strip())
            break

        chunk = summary[:max_length]
        match = re.search(r"\. ", chunk[::-1])  
        if match:
            end_idx = max_length - match.start()
        else:
            end_idx = max_length  

        chunks.append(summary[:end_idx].strip())
        summary = summary[end_idx:].strip()

    return chunks
def process_data(datapath):
    key = os.getenv("API_KEY")
    today = time.strftime("%Y-%m-%d")
    how_many_days = 5
    start = time.strftime("%Y-%m-%d", time.localtime(time.time() - how_many_days*86400))

    url = f"https://api.congress.gov/v3/summaries?fromDateTime={start}T00:00:00Z&toDateTime={today}T00:00:00Z&sort=updateDate+asc&api_key={key}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    data = response.json()
    print(json.dumps(data, indent=4, ensure_ascii=False))
    summaries = data.get("summaries", [])

    output = []

    for summary in summaries:
        bill = summary.get("bill", {}) 
        summary_text = summary.get("text", "").strip()

        second_url = f"https://api.congress.gov/v3/bill/119/hr/{bill.get("number", "")}/text?api_key={key}"
        second_response = requests.get(second_url)
        text_versions = second_response.json().get("textVersions", [])
        
        full_text_link = "No XML available"
        for version in text_versions:
            for format_item in version.get("formats", []):
                if format_item["type"] == "Formatted XML": 
                    full_text_link = format_item["url"]
                    break

        data = {
            "date": today,
            "congress": bill.get("congress", ""),
            "number": bill.get("number", ""),
            "originChamber": bill.get("originChamber", ""),
            "originChamberCode": bill.get("originChamberCode", ""),
            "title": bill.get("title", ""),
            "bill_type": bill.get("type", ""),
            "url": bill.get("url", ""),
            "summary": summary_text,
            "summary_chunks": chunk_summary(summary_text) if summary_text else [],
            "full_text_link": full_text_link
        }
        print(data)

        output.append(data)

    with open(datapath, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)
