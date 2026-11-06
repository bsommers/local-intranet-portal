# Local Intranet Web Server & Ecosystem Hub

A high-performance local dashboard, source viewer, and pluggable micro-framework server running on the local home network.

## 🚀 URLs
- **Local Dashboard:** [http://localhost:8088](http://localhost:8088)
- **Home Network Dashboard:** [http://192.168.1.245:8088](http://192.168.1.245:8088)
- **Raw Reports Directory:** [http://192.168.1.245:8088/raw-reports/](http://192.168.1.245:8088/raw-reports/)
- **Pluggable REST API:** [http://192.168.1.245:8088/api/](http://192.168.1.245:8088/api/)

---

## 🛠️ Architecture

```
[Browser / Home Network Client (192.168.1.245:8088)]
                       │
             ┌─────────▼─────────┐
             │    Nginx 1.31     │ (Reverse Proxy & Static Asset Server)
             │   (Port 8088)     │
             └─────────┬─────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
  (Static / Reports)             (/api/*)
        │                             │
 ┌──────▼──────┐             ┌────────▼────────┐
 │ static/     │             │ Python Backend  │ (Async HTTP Gateway)
 │ reports/    │             │   (Port 8081)   │
 └─────────────┘             └────────┬────────┘
                                      │
                   ┌──────────────────┼──────────────────┐
                   │                  │                  │
            ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
            │   System    │    │ Source Code │    │   Plugins   │
            │  Telemetry  │    │  Explorer   │    │  Substrate  │
            │ (/proc stats)    │(~/src, ~/eco)    │ (plugins/*.py)
            └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 📂 Sub-Pages & Capabilities

1. **📊 Dashboard:** Real-time host telemetry (32 cores, 197GB RAM, disk gauges, load averages, uptime).
2. **💻 Source Viewer:** Interactive directory tree and code viewer for `~/src` and `~/ecosystem` with PrismJS syntax highlighting and directory traversal safeguards.
3. **📑 Reports:** Dynamic viewer for HTML/Markdown/JSON audits and artifacts generated across the workspace (`reports/`).
4. **📈 Charts & Metrics:** Real-time canvas/Chart.js telemetry charts for CPU load history and memory distribution.
5. **🧮 Math & Scratchpad:** Interactive KaTeX math renderer and live mathematical expression evaluator powered by backend plugin `math_runner`.
6. **📚 Reading Lists:** Searchable and filterable reading queue with live additions and persistent storage (`data/reading_list.json`).
7. **📖 Documentation:** Quick markdown reference and architectural manuals.
8. **📅 Calendar:** Local schedule and event organizer with persistent storage (`data/calendar.json`).
9. **🔌 REST & Plugins:** Interactive REST API browser and testing console for dynamic micro-framework endpoints.

---

## 🔌 Pluggable Architecture

Drop any standalone Python file into `plugins/` that defines `handle_request(method, query_params, body_payload)`. It will immediately and dynamically mount under `/api/plugins/<filename>`.

Example (`plugins/custom_service.py`):
```python
ALLOWED_METHODS = ["GET", "POST"]

def handle_request(method, query, body):
    return {"status": "ok", "custom_data": 42}
```

Endpoint automatically created:
`GET /api/plugins/custom_service`

---

## 🚦 Server Management

Start server:
```bash
./start.sh
```

Stop server:
```bash
./stop.sh
```
