import feedparser
import requests
from datetime import datetime

def fetch_feed_entries(path, limit=10):
    feed = feedparser.parse(path)
    entries = []

    for entry in feed.entries[:limit]:
        title = entry.get("title", "No title")
        link = entry.get("link", "#")
        date = entry.get("published", entry.get("updated", ""))
        # Only show date if it's not already part of the hyperlink
        if "://" in link and date and date not in link:
            try:
                parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
                date_str = f" {parsed_date.strftime('%Y-%m-%d')}"
            except ValueError:
                date_str = ""
        else:
            date_str = ""
        entries.append(f"- [{title}{date_str}]({link})")

    return entries

def fetch_codewalker_commits(limit=10):
    url = "https://api.github.com/repos/dexyfex/CodeWalker/commits"
    response = requests.get(url)
    commits = response.json()
    entries = []

    for commit in commits[:limit]:
        sha = commit["sha"][:7]
        msg = commit["commit"]["message"].split("\n")[0]
        url = commit["html_url"]
        date_str = commit["commit"]["author"]["date"][:10]  # ISO format date
        entries.append(f"- [{msg} ({sha}) {date_str}]({url})")

    return entries

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
    sources = [
        ("ENHANCED", "RSS", "PatchnotesEnhancedRSS.rss"),
        ("LEGACY", "RSS", "PatchnotesLegacyRSS.rss"),
        ("SHVDN", "RSS", "https://ci.appveyor.com/nuget/scripthookvdotnet-nightly"),
        ("CODEWALKER", "RSS", None)
    ]

    for name, prefix, path in sources:
        if name == "CODEWALKER":
            entries = fetch_codewalker_commits()
        else:
            entries = fetch_feed_entries(path)
        print(f"Updated section for {name} with {len(entries)} entries.")
        update_readme_section(prefix, name, entries)

if __name__ == "__main__":
    main()