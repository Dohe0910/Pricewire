#!/usr/bin/env python3
"""
Pricewire price bot -- Gemini edition (google-genai SDK).
Runs on a GitHub Actions schedule (free). Uses Gemini's free-tier API with
Google Search grounding to re-check laptop prices, most-stale-first, and
saves partial progress if it runs out of quota mid-run.

Requires env var: GEMINI_API_KEY
"""
import json
import os
import re
import sys
import time
from datetime import date

from google import genai
from google.genai import types

HTML_PATH = "pricewire.html"
START_TAG = '<script id="price-data" type="application/json">'
END_TAG = "</script>"

MAX_LAPTOPS_PER_RUN = 150
SECONDS_BETWEEN_CALLS = 5
MODEL = "gemini-2.5-flash"

TODAY = date.today().strftime("%B %-d, %Y") if os.name != "nt" else date.today().strftime("%B %d, %Y")


def load_data():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    start = html.index(START_TAG) + len(START_TAG)
    end = html.index(END_TAG, start)
    json_text = html[start:end]
    data = json.loads(json_text)
    return html, start, end, data


def save_data(html, start, end, data):
    new_json = json.dumps(data, indent=1, ensure_ascii=False)
    new_html = html[:start] + "\n" + new_json + "\n" + html[end:]
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)


def pick_stale_laptops(laptops, limit):
    def sort_key(l):
        return l.get("lastChecked", "0000-00-00")
    ordered = sorted(laptops, key=sort_key)
    return ordered[:limit]


PROMPT_TEMPLATE = """You are checking the current US price for exactly one laptop, using
Google Search. Laptop: "{name}" (spec hint: {specs}).

Search reputable US retailers. Check as many of these as are relevant:
Amazon, Best Buy, B&H Photo, Newegg, Walmart, Costco, Micro Center, Target,
Adorama, Sam's Club, Staples, Office Depot, Dell.com, HP.com, Lenovo.com,
ASUS Store, Acer Store, Razer.com, Framework.com, Antonline, and Woot. Find the
.

Respond with ONLY a JSON object, no other text, no markdown fences, in this exact shape:
{{
  "found": true or false,
  "retailers": [{{"name": "...", "price": "$...", "url": "..."}}],
  "note": "one short sentence, e.g. mentioning a sale or all-time low, or empty string",
  "why": "one short sentence on why this is/isn't the best pick"
}}
Include up to 3 retailers, best deal first. If you can't find a confident current
price, set "found": false and leave the other fields as empty defaults. Never
invent a price or a URL.
"""


def query_gemini(client, laptop):
    name = laptop.get("keys", ["unknown"])[0] if laptop.get("keys") else laptop.get("name", "unknown laptop")
    specs = laptop.get("specs", "")
    prompt = PROMPT_TEMPLATE.format(name=name, specs=specs)
    try:
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config,
        )
        text = (resp.text or "").strip()
        text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        return json.loads(text)
    except Exception as e:
        print(f"  ! error checking {name}: {e}", file=sys.stderr)
        return None


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    html, start, end, data = load_data()
    laptops = data["laptops"]

    targets = pick_stale_laptops(laptops, MAX_LAPTOPS_PER_RUN)
    target_ids = {id(l) for l in targets}

    checked, changed = 0, 0
    for laptop in laptops:
        if id(laptop) not in target_ids:
            continue
        name = laptop.get("keys", ["?"])[0] if laptop.get("keys") else "?"
        print(f"Checking: {name}")
        result = query_gemini(client, laptop)
        checked += 1

        if result and result.get("found") and result.get("retailers"):
            laptop["retailers"] = result["retailers"]
            laptop["bestIndex"] = 0
            if result.get("note"):
                laptop["note"] = result["note"]
            if result.get("why"):
                laptop["why"] = result["why"]
            laptop["verified"] = True
            laptop["lastChecked"] = date.today().isoformat()
            changed += 1
        else:
            laptop["lastChecked"] = date.today().isoformat()

        data["asOf"] = TODAY
        save_data(html, start, end, data)
        html, start, end, data = load_data()

        time.sleep(SECONDS_BETWEEN_CALLS)

    remaining = len(laptops) - len([l for l in laptops if l.get("lastChecked") == date.today().isoformat()])
    print(f"\nDone. Checked {checked} laptops, updated {changed} with new data.")
    print(f"~{remaining} laptops still due for a check -- next run picks up where this left off.")


if __name__ == "__main__":
    main()
