import pandas as pd
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def stream_csv(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        for line in f:
            row = line.strip().split(",")
            yield dict(zip(header, row))

def process_row(row):
    if row.get("Link Type") != "Public URL":
        return None
    json_filename = row.get("Equalify Scan Results", "").strip()
    if not json_filename or not json_filename.endswith(".json"):
        return None
    json_file = os.path.join("results", json_filename)
    if os.path.isdir(json_file):
        return None
    if not os.path.isfile(json_file):
        return None
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    violations = data.get("result", {}).get("results", {}).get("violations", [])
    total_violations = len(violations)
    unique_nodes = set()
    node_violation_count = defaultdict(lambda: {"html": "", "count": 0})
    violation_summary = defaultdict(int)
    for violation in violations:
        desc = violation.get("description", "No description")
        help_text = violation.get("help", "No help")
        vid = violation.get("id", "No ID")
        violation_summary[(desc, help_text, vid)] += 1
        for node in violation.get("nodes", []):
            for t in node.get("target", []):
                if isinstance(t, list):
                    unique_nodes.update(t)
                else:
                    unique_nodes.add(t)
            target = node.get("target", ["(no id)"])
            node_id = target[0] if isinstance(target, list) and target else "(no id)"
            if isinstance(node_id, list):
                node_id = node_id[0] if node_id else "(no id)"
            if node_violation_count[node_id]["html"] == "":
                node_violation_count[node_id]["html"] = node.get("html", "")[:100]
            node_violation_count[node_id]["count"] += 1
            # Add unique violation messages
            message = node.get("failureSummary", "").strip()
            if "messages" not in node_violation_count[node_id]:
                node_violation_count[node_id]["messages"] = set()
            if message:
                node_violation_count[node_id]["messages"].add(message)
    page_url = row.get("URL", "unknown")
    return total_violations, unique_nodes, node_violation_count, violation_summary, page_url

total_pages_scanned = 0
total_violations = 0
all_unique_nodes = set()
all_node_violation_count = defaultdict(lambda: {"html": "", "count": 0})
all_violation_summary = defaultdict(int)
page_violation_counts = defaultdict(int)

rows = list(stream_csv("output.csv"))
total_pages_scanned = sum(1 for row in rows if row.get("Link Type") == "Public URL")

with ThreadPoolExecutor() as executor:
    results = list(tqdm(executor.map(process_row, rows), total=len(rows), desc="Processing"))

for res in results:
    if res is None:
        continue
    t_violations, unique_nodes, node_violation_count, violation_summary, page_url = res
    total_violations += t_violations
    all_unique_nodes.update(unique_nodes)
    for nid, data in node_violation_count.items():
        if all_node_violation_count[nid]["html"] == "":
            all_node_violation_count[nid]["html"] = data["html"]
        all_node_violation_count[nid]["count"] += data["count"]
        if "messages" in data:
            if "messages" not in all_node_violation_count[nid]:
                all_node_violation_count[nid]["messages"] = set()
            all_node_violation_count[nid]["messages"].update(data["messages"])
    for key, count in violation_summary.items():
        all_violation_summary[key] += count
    page_violation_counts[page_url] += t_violations

summary_data = {
    "Pages Scanned": [total_pages_scanned],
    "Total Violations": [total_violations],
    "Unique Nodes": [len(all_unique_nodes)]
}
pd.DataFrame(summary_data).to_csv("output-summary.csv", index=False)

node_rows = []
for nid, data in all_node_violation_count.items():
    node_rows.append({
        "Node ID": nid,
        "Node HTML": data["html"],
        "Violation Count": data["count"],
        "Unique Violation Messages": " || ".join(sorted(data.get("messages", [])))
    })
pd.DataFrame(node_rows).to_csv("output-nodes.csv", index=False)

violation_rows = []
for (desc, help_text, vid), count in all_violation_summary.items():
    violation_rows.append({
        "Description": desc,
        "Help": help_text,
        "ID": vid,
        "Count": count
    })
pd.DataFrame(violation_rows).to_csv("output-violation_messages.csv", index=False)


# Collect page-level unique messages
from collections import defaultdict
page_violation_messages = defaultdict(set)
for res in results:
    if res is None:
        continue
    _, _, node_violation_count, _, page_url = res
    for node in node_violation_count.values():
        msg = node.get("messages", set())
        page_violation_messages[page_url].update(msg)

page_rows = [{
    "Page URL": url,
    "Violation Count": count,
    "Unique Violation Messages": " || ".join(sorted(page_violation_messages[url]))
} for url, count in page_violation_counts.items()]
pd.DataFrame(page_rows).to_csv("output-pages.csv", index=False)
