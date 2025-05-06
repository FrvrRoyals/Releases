import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def parse_date(text):
    formats = ["%d %b %Y", "%B %d, %Y", "%d/%m/%y", "%d/%m/%Y", "%d %B %Y", "%d %b %y"]
    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    return None

def fetch_scripthookv():
    url = "http://www.dev-c.com/gtav/scripthookv/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    date_cell = soup.find("td", string=lambda s: s and "Released" in s)
    version_cell = soup.find("td", string=lambda s: s and "Version" in s)

    if not date_cell:
        return []

    date_value = date_cell.find_next_sibling("td")
    version_value = version_cell.find_next_sibling("td") if version_cell else None

    date = parse_date(date_value.text) if date_value else None
    version = version_value.text.strip() if version_value else "Unknown"

    download_link = url  # Best approximation since no direct file URL is exposed

    if date:
        return [f"- [ScriptHookV {version}](http://www.dev-c.com/gtav/scripthookv/)"]
    return []

def fetch_openrpf():
    url = "https://www.gta5-mods.com/tools/openrpf-openiv-asi-for-gta-v-enhanced"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    versions = []

    changelog = soup.find("div", class_="download-list")
    if changelog:
        for entry in changelog.find_all("li")[:10]:
            date_tag = entry.find("span", class_="date")
            version_tag = entry.find("strong")
            download_button = entry.find("a", class_="download-link")
            if date_tag and version_tag:
                version = version_tag.text.strip()
                link = url  # Could try to parse download link more precisely
                versions.append(f"- [OpenRPF {version}]({link})")

    return versions

def update_readme_section(prefix, name, entries):
    start_marker = f"<!-- {prefix}-{name}-START -->"
    end_marker = f"<!-- {prefix}-{name}-END -->"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"Markers not found: {start_marker} / {end_marker}")

    section = f"{start_marker}\n" + "\n".join(entries[:10]) + f"\n{end_marker}"
    updated = content[:start_idx] + section + content[end_idx + len(end_marker):]

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

def main():
    sections = [
        {"name": "SCRIPTHOOKV", "prefix": "RSS", "entries": fetch_scripthookv()},
        {"name": "OPENRPF", "prefix": "RSS", "entries": fetch_openrpf()},
    ]

    for section in sections:
        logging.info(f"{section['name']}: {len(section['entries'])} entries found")
        update_readme_section(section["prefix"], section["name"], section["entries"])

if __name__ == "__main__":
    main()