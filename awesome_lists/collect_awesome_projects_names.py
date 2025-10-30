import re
import json

def extract_links_github(file_in, file_out):
    pattern_github = r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"

    with open(file_in, "r", encoding="utf-8") as f:
        content = f.read()

    links = re.findall(pattern_github, content)
    unique_links = sorted(set(links))

    with open(file_out, "w", encoding="utf-8") as f:
        json.dump(unique_links, f, indent=4, ensure_ascii=False)


extract_links_github("awesome_lists/text.txt", "awesome_lists/awesome_list_projects_url.json")
