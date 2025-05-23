import requests
from bs4 import BeautifulSoup
import re
import os

# URL of the Kafka Improvement Proposals page
URL = "https://cwiki.apache.org/confluence/display/kafka/kafka+improvement+proposals"

# Output directory for KIP folders
OUTPUT_DIR = "kip_redirects"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch the page
response = requests.get(URL)
response.raise_for_status()
html = response.text

# Parse with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# Regex to find KIP-<number> in link text or href
kip_link_regex = re.compile(r"KIP-(\d+)", re.IGNORECASE)

kip_links = {}

# Find all links
for a in soup.find_all("a", href=True):
    match = kip_link_regex.search(a.text)
    if match:
        kip_number = match.group(1)
        href = a["href"]
        # Some links might be relative, make them absolute
        if not href.startswith("http"):
            href = "https://cwiki.apache.org" + href
        kip_links[kip_number] = href

# Write index.html in a directory for each KIP
for kip_number, kip_url in kip_links.items():
    dir_name = f"KIP-{kip_number}"
    dir_path = os.path.join(OUTPUT_DIR, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    index_filepath = os.path.join(dir_path, "index.html")
    html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url={kip_url}" />
    <title>Redirecting to KIP-{kip_number}</title>
  </head>
  <body>
    <p>Redirecting to <a href="{kip_url}">{kip_url}</a></p>
  </body>
</html>
"""
    with open(index_filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

print(f"Generated {len(kip_links)} KIP redirect folders (each with index.html) in '{OUTPUT_DIR}' directory.")
