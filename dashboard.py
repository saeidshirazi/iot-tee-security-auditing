#!/usr/bin/env python3
"""
dashboard.py
-------------
Generates a complete HTML dashboard with:

- Statistics summary
- Alert filters
- Paginated event table
- Integrated PyVis provenance graph
- Multi-color alert badges (spoofing, masking, TLS violations)

Output:
    dashboard.html
"""

import json
from pathlib import Path
from datetime import datetime
from pyvis.network import Network

AUDIT_LOG = "audit_log.jsonl"
OUTPUT_HTML = "dashboard.html"

# Color map for alerts / states
COLOR_MAP = {
    "ok": "#10b981",            # green
    "spoofing": "#ef4444",      # red
    "masking": "#f59e0b",       # orange
    "tls_violation": "#7c3aed", # purple
    "event": "#3b82f6"          # blue
}

# ------------------------------------------------------------
# Load Events
# ------------------------------------------------------------
def load_events():
    events = []
    if not Path(AUDIT_LOG).exists():
        print("[ERROR] audit_log.jsonl not found. Run ree.py | tee.py first.")
        return []

    with open(AUDIT_LOG, "r") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except:
                continue

    events.sort(key=lambda x: x.get("event_id", 0))
    return events


# ------------------------------------------------------------
# Compute Stats
# ------------------------------------------------------------
def compute_stats(events):
    stats = {"total": len(events), "ok": 0, "spoofing": 0, "masking": 0, "tls_violation": 0}

    for e in events:
        alerts = e.get("alerts", [])
        if not alerts:
            stats["ok"] += 1
        for a in alerts:
            if a in stats:
                stats[a] += 1

    return stats


# ------------------------------------------------------------
# Build PyVis Graph (cleaner, less cluttered)
# ------------------------------------------------------------
def build_graph(events):
    net = Network(height="600px", width="100%", directed=True, bgcolor="#fafafa")

    # Better layout settings
    net.set_options("""
    var options = {
      "nodes": {"borderWidth": 1, "shape": "dot", "size": 12},
      "edges": {"arrows": {"to": {"enabled": true}}},
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -4000,
          "centralGravity": 0.2,
          "springLength": 120
        }
      }
    }
    """)

    for e in events:
        evt = f"Event_{e['event_id']}"
        physical = f"physical={e['actual_state']}"
        reported = f"reported={e['reported_state']}"
        network = f"net={e['network_attempt']}"

        # Event node
        net.add_node(evt, color=COLOR_MAP["event"], label=evt)

        # Physical state node
        net.add_node(physical, color="#0f766e")
        net.add_edge(evt, physical)

        # Reported state node
        net.add_node(reported, color="#fbbf24")
        net.add_edge(evt, reported)

        # Network attempt node
        net.add_node(network, color="#fb923c")
        net.add_edge(evt, network)

        # Alerts (multi-color properly)
        alerts = e.get("alerts", [])
        if not alerts:
            ok_node = f"OK_{e['event_id']}"
            net.add_node(ok_node, label="OK", color=COLOR_MAP["ok"], shape="box")
            net.add_edge(evt, ok_node)
        else:
            for a in alerts:
                a_node = f"{a}_{e['event_id']}"
                net.add_node(a_node, label=a.upper(), color=COLOR_MAP[a], shape="box")
                net.add_edge(evt, a_node)

    net.write_html("graph_component.html")
    return "graph_component.html"


# ------------------------------------------------------------
# Event Table with Multi-Color Badges
# ------------------------------------------------------------
def generate_event_table(events):
    rows = []

    for e in events:

        # Each alert gets its own badge
        alerts = e["alerts"] if e["alerts"] else ["ok"]

        badge_html = "".join([
            f"<span class='badge' style='background:{COLOR_MAP[a]};margin-right:4px'>{a}</span>"
            for a in alerts
        ])

        rows.append(f"""
        <tr data-alerts="{' '.join(alerts)}">
            <td>{e['event_id']}</td>
            <td>{e['device']}</td>
            <td>{e['actual_state']}</td>
            <td>{e['reported_state']}</td>
            <td>{e['network_attempt']}</td>
            <td>{badge_html}</td>
            <td>{datetime.fromtimestamp(e['time_tee']).strftime("%Y-%m-%d %H:%M:%S")}</td>
        </tr>
        """)

    return "\n".join(rows)


# ------------------------------------------------------------
# HTML Dashboard Template
# ------------------------------------------------------------
def generate_dashboard(events, stats, graph_file):
    rows_html = generate_event_table(events)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>IoT Security Auditing Dashboard</title>

<style>
body {{
    font-family: Arial, sans-serif;
    background: #f3f4f6;
    margin: 0;
}}
header {{
    background: #111827;
    color: white;
    padding: 20px;
}}
.cards {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
    margin: 20px;
}}
.card {{
    background: white;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}}
.badge {{
    color: white;
    padding: 3px 6px;
    border-radius: 6px;
    font-size: 0.75em;
}}
button.filter {{
    padding: 8px 12px;
    border-radius: 6px;
    border: none;
    margin-right: 8px;
    cursor: pointer;
    color: white;
}}
table {{
    width: 96%;
    margin: 20px auto;
    background: white;
    border-collapse: collapse;
}}
th, td {{
    padding: 8px;
    border-bottom: 1px solid #ddd;
}}
iframe {{
    border: none;
    margin: 20px;
    border-radius: 12px;
}}
</style>

</head>
<body>

<header>
    <h1>IoT Security Auditing Dashboard</h1>
</header>

<div class="cards">
    <div class="card"><h3>Total</h3><p>{stats['total']}</p></div>
    <div class="card"><h3>OK</h3><p>{stats['ok']}</p></div>
    <div class="card"><h3>Spoofing</h3><p>{stats['spoofing']}</p></div>
    <div class="card"><h3>Masking</h3><p>{stats['masking']}</p></div>
    <div class="card"><h3>TLS Violations</h3><p>{stats['tls_violation']}</p></div>
</div>

<h2 style="margin-left:20px;">Filters</h2>
<div style="margin-left:20px;">
    <button class="filter" onclick="filterTable('all')" style="background:#6366f1;">All</button>
    <button class="filter" onclick="filterTable('ok')" style="background:{COLOR_MAP['ok']}">OK</button>
    <button class="filter" onclick="filterTable('spoofing')" style="background:{COLOR_MAP['spoofing']}">Spoofing</button>
    <button class="filter" onclick="filterTable('masking')" style="background:{COLOR_MAP['masking']}">Masking</button>
    <button class="filter" onclick="filterTable('tls_violation')" style="background:{COLOR_MAP['tls_violation']}">TLS</button>
</div>

<table id="eventsTable">
<thead>
<tr>
    <th>ID</th><th>Device</th><th>Physical</th>
    <th>Reported</th><th>Network</th><th>Alerts</th><th>TEE Time</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>

<div class="pagination" style="text-align:center;margin:10px;">
<button onclick="prevPage()">Prev</button>
<span id="pageInfo"></span>
<button onclick="nextPage()">Next</button>
</div>

<h2 style="margin-left:20px;">Interactive Provenance Graph</h2>
<iframe src="{graph_file}" width="96%" height="650px"></iframe>

<script>
var table = document.getElementById("eventsTable");
var rows = table.getElementsByTagName("tr");
var currentPage = 1;
var pageSize = 20;

function paginate() {{
    for (var i = 1; i < rows.length; i++) {{
        rows[i].style.display = "none";
        if (i > (currentPage - 1) * pageSize && i <= currentPage * pageSize)
            rows[i].style.display = "";
    }}
    document.getElementById("pageInfo").innerHTML =
        "Page " + currentPage + " / " + Math.ceil((rows.length-1) / pageSize);
}}

function nextPage() {{
    if (currentPage * pageSize < rows.length - 1) {{
        currentPage++;
        paginate();
    }}
}}

function prevPage() {{
    if (currentPage > 1) {{
        currentPage--;
        paginate();
    }}
}}

function filterTable(alertType) {{
    for (var i = 1; i < rows.length; i++) {{
        let alerts = rows[i].getAttribute("data-alerts");
        if (alertType === "all" || alerts.includes(alertType))
            rows[i].style.display = "";
        else
            rows[i].style.display = "none";
    }}
}}

paginate();
</script>

</body>
</html>
"""
    return html


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    events = load_events()
    stats = compute_stats(events)

    print("[INFO] Building provenance graph...")
    graph_file = build_graph(events)

    print("[INFO] Building dashboard...")
    html = generate_dashboard(events, stats, graph_file)

    Path(OUTPUT_HTML).write_text(html, encoding="utf-8")
    print(f"[INFO] Dashboard generated: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
