import requests
from bs4 import BeautifulSoup
import re
import os
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(
        description="Parse Improvement Proposal links from a Confluence wiki page and generate redirect index.html files."
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the Confluence wiki page listing Improvement Proposals (e.g., https://cwiki.apache.org/confluence/display/kafka/kafka+improvement+proposals)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory in which to create proposal folders with index.html redirects"
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="Prefix of proposals, e.g., KIP or FLIP. If not provided, prefix is inferred from the URL."
    )
    args = parser.parse_args()

    url = args.url
    output_dir = args.output_dir

    # Infer prefix if not provided
    if args.prefix:
        proposal_prefix = args.prefix
        project= ""
    elif "kafka" in url.lower():
        proposal_prefix = "KIP"
        project="kafka"
    elif "flink" in url.lower():
        proposal_prefix = "FLIP"
        project="flink"
    else:
        proposal_prefix = "IP"  # generic fallback
        project= ""

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Fetch the page
    print(f"Fetching {url} ...")
    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Regex to find e.g. KIP-1025 or FLIP-384, case-insensitive
    proposal_link_regex = re.compile(rf"\b{proposal_prefix}-(\d+)\b", re.IGNORECASE)

    proposal_links = {}

    # Find all links
    for a in soup.find_all("a", href=True):
        match = proposal_link_regex.search(a.text)
        if match:
            proposal_number = match.group(1)
            href = a["href"]
            # Some links might be relative, make them absolute
            if not href.startswith("http"):
                href = "https://cwiki.apache.org" + href
            proposal_links[proposal_number] = href

    # Write index.html in a directory for each proposal
    for proposal_number, proposal_url in proposal_links.items():
        dir_name = f"{proposal_prefix}-{proposal_number}"
        dir_path = os.path.join(output_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        index_filepath = os.path.join(dir_path, "index.html")
        html_content = f"""<!DOCTYPE html>
<html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0; url={proposal_url}" />
        <script type="text/javascript">
            window.location.href = "{proposal_url}"
        </script>
        <title>Redirecting to {proposal_prefix}-{proposal_number}</title>
    </head>
    <body>
        If you are not redirected automatically, follow this <a href='{proposal_url}'>link</a>.
    </body>
</html>
"""
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Also create file with proposal prefix in lower case
        lc_dir_name = f"{proposal_prefix}-{proposal_number}".lower()
        lc_dir_path = os.path.join(output_dir, lc_dir_name)
        os.makedirs(lc_dir_path, exist_ok=True)
        lc_index_filepath = os.path.join(lc_dir_path, "index.html")
        shutil.copyfile(index_filepath, lc_index_filepath)

        # Also create a redirect file with just the proposal number
        # this is for use with the <project-name> subdomain
        if project:
            # Add project prefix to the output directory
            prj_basename = f"{project}-{os.path.basename(output_dir)}"
            prj_output_dir = os.path.join(os.path.dirname(output_dir), prj_basename)
            num_dir_name = f"{proposal_number}"
            prj_dir_path = os.path.join(prj_output_dir, num_dir_name)
            os.makedirs(prj_dir_path, exist_ok=True)
            prj_index_filepath = os.path.join(prj_dir_path, "index.html")
            shutil.copyfile(index_filepath, prj_index_filepath)

    print(f"Generated {len(proposal_links)} {proposal_prefix} redirect folders (each with index.html) in '{output_dir}' directory.")

if __name__ == "__main__":
    main()
