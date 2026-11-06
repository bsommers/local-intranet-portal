#!/usr/bin/env python3
"""
Lightweight Pluggable Intranet API Gateway & System Monitor
Zero external dependencies (uses Python standard library).
"""
import os
import sys
import json
import time
import shutil
import mimetypes
import importlib.util
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("PORT", 8081))
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
PLUGINS_DIR = BASE_DIR / "plugins"

SRC_ROOT = Path(os.environ.get("SRC_ROOT", Path.home() / "src")).resolve()
ECO_ROOT = Path(os.environ.get("ECO_ROOT", Path.home() / "ecosystem")).resolve()

# Safe roots map
ROOTS = {
    "src": SRC_ROOT,
    "ecosystem": ECO_ROOT
}

# In-memory dynamic plugin registry
PLUGINS = {}

def load_plugins():
    PLUGINS.clear()
    if not PLUGINS_DIR.exists():
        PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    
    for file in PLUGINS_DIR.glob("*.py"):
        if file.name.startswith("_"):
            continue
        plugin_name = file.stem
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "handle_request"):
                PLUGINS[plugin_name] = {
                    "module": module,
                    "doc": getattr(module, "__doc__", "").strip(),
                    "methods": getattr(module, "ALLOWED_METHODS", ["GET", "POST"])
                }
        except Exception as e:
            print(f"[Plugin Error] Failed to load {file.name}: {e}", file=sys.stderr)

def get_system_stats():
    uptime_sec = 0
    try:
        with open("/proc/uptime", "r") as f:
            uptime_sec = float(f.readline().split()[0])
    except Exception:
        pass

    # Load avg
    load1, load5, load15 = (0, 0, 0)
    try:
        load1, load5, load15 = os.getloadavg()
    except Exception:
        pass

    # Memory
    mem_total, mem_available = 0, 0
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if parts[0] == "MemTotal":
                    mem_total = int(parts[1].strip().split()[0]) * 1024
                elif parts[0] == "MemAvailable":
                    mem_available = int(parts[1].strip().split()[0]) * 1024
    except Exception:
        pass

    mem_used = mem_total - mem_available

    # Disk
    disk_usage = shutil.disk_usage(Path.home())

    # CPU cores
    cpu_count = os.cpu_count() or 1

    return {
        "hostname": os.uname().nodename,
        "os": f"{os.uname().sysname} {os.uname().release}",
        "uptime_seconds": uptime_sec,
        "load_avg": {"1m": round(load1, 2), "5m": round(load5, 2), "15m": round(load15, 2)},
        "cpu_cores": cpu_count,
        "memory": {
            "total_bytes": mem_total,
            "used_bytes": mem_used,
            "free_bytes": mem_available,
            "percent": round((mem_used / mem_total * 100), 1) if mem_total else 0
        },
        "disk": {
            "total_bytes": disk_usage.total,
            "used_bytes": disk_usage.used,
            "free_bytes": disk_usage.free,
            "percent": round((disk_usage.used / disk_usage.total * 100), 1)
        },
        "network": {
            "primary_ip": "192.168.1.245",
            "port": 8088
        }
    }

def read_json_file(file_path, default_val=None):
    if default_val is None:
        default_val = []
    if not file_path.exists():
        return default_val
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val

def write_json_file(file_path, data):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class IntranetAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text, content_type="text/plain; charset=utf-8", status=200):
        body = text.encode("utf-8") if isinstance(text, str) else text
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # 1. System status
        if path == "/api/system/status":
            return self._send_json(get_system_stats())

        # 2. Source Code Tree
        elif path == "/api/sources/list":
            root_key = query.get("root", ["src"])[0]
            subpath = query.get("subpath", [""])[0].strip("/")
            
            if root_key not in ROOTS:
                return self._send_json({"error": "Invalid root. Use 'src' or 'ecosystem'."}, 400)
            
            target_root = ROOTS[root_key]
            target_dir = (target_root / subpath).resolve()

            # Prevent directory traversal
            try:
                target_dir.relative_to(target_root)
            except ValueError:
                return self._send_json({"error": "Access denied: Path outside root boundary."}, 403)

            if not target_dir.exists() or not target_dir.is_dir():
                return self._send_json({"error": "Directory not found."}, 404)

            items = []
            try:
                for entry in sorted(os.scandir(target_dir), key=lambda e: (not e.is_dir(), e.name.lower())):
                    if entry.name.startswith(".git") and entry.name != ".gitignore":
                        continue
                    is_dir = entry.is_dir()
                    item_info = {
                        "name": entry.name,
                        "path": str(Path(subpath) / entry.name) if subpath else entry.name,
                        "is_dir": is_dir,
                        "size": entry.stat().st_size if not is_dir else 0,
                        "mtime": entry.stat().st_mtime
                    }
                    items.append(item_info)
            except PermissionError:
                return self._send_json({"error": "Permission denied reading directory."}, 403)

            return self._send_json({
                "root": root_key,
                "current_path": subpath,
                "items": items
            })

        # 3. Source Code File Content
        elif path == "/api/sources/read":
            root_key = query.get("root", ["src"])[0]
            filepath = query.get("filepath", [""])[0].strip("/")

            if root_key not in ROOTS:
                return self._send_json({"error": "Invalid root."}, 400)

            target_root = ROOTS[root_key]
            target_file = (target_root / filepath).resolve()

            try:
                target_file.relative_to(target_root)
            except ValueError:
                return self._send_json({"error": "Path traversal prohibited."}, 403)

            if not target_file.exists() or not target_file.is_file():
                return self._send_json({"error": "File not found."}, 404)

            # Limit size to 3MB for responsiveness
            stat = target_file.stat()
            if stat.st_size > 3 * 1024 * 1024:
                return self._send_json({"error": "File size exceeds 3MB limit."}, 413)

            mime, _ = mimetypes.guess_type(str(target_file))
            try:
                with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                return self._send_json({
                    "name": target_file.name,
                    "filepath": filepath,
                    "root": root_key,
                    "mime": mime or "text/plain",
                    "size": stat.st_size,
                    "content": content
                })
            except Exception as e:
                return self._send_json({"error": str(e)}, 500)

        # 4. Reports List & View
        elif path == "/api/reports":
            reports = []
            if REPORTS_DIR.exists():
                for f in sorted(REPORTS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                    if f.is_file() and f.suffix in [".html", ".htm", ".md", ".json", ".txt"]:
                        reports.append({
                            "name": f.name,
                            "size": f.stat().st_size,
                            "mtime": f.stat().st_mtime,
                            "type": f.suffix.lstrip("."),
                            "url": f"/raw-reports/{f.name}"
                        })
            return self._send_json({"reports": reports})

        # 5. Calendar
        elif path == "/api/calendar":
            events = read_json_file(DATA_DIR / "calendar.json", [])
            return self._send_json(events)

        # 6. Reading List
        elif path == "/api/reading-list":
            items = read_json_file(DATA_DIR / "reading_list.json", [])
            return self._send_json(items)

        # 7. Plugins Registry
        elif path == "/api/plugins":
            load_plugins()
            meta = [
                {
                    "name": name,
                    "doc": info["doc"],
                    "methods": info["methods"],
                    "endpoint": f"/api/plugins/{name}"
                }
                for name, info in PLUGINS.items()
            ]
            return self._send_json({"plugins": meta})

        # 8. Plugin Dynamic Invocation
        elif path.startswith("/api/plugins/"):
            plugin_name = path[len("/api/plugins/"):].split("/")[0]
            if plugin_name not in PLUGINS:
                load_plugins()
            if plugin_name in PLUGINS:
                try:
                    res = PLUGINS[plugin_name]["module"].handle_request("GET", query, None)
                    return self._send_json(res)
                except Exception as e:
                    return self._send_json({"error": f"Plugin error: {str(e)}"}, 500)
            return self._send_json({"error": f"Plugin '{plugin_name}' not found."}, 404)

        else:
            return self._send_json({"error": "Endpoint not found", "available": ["/api/system/status", "/api/sources/list", "/api/sources/read", "/api/reports", "/api/calendar", "/api/reading-list", "/api/plugins"]}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if path == "/api/calendar":
            events = read_json_file(DATA_DIR / "calendar.json", [])
            payload["id"] = int(time.time() * 1000)
            events.append(payload)
            write_json_file(DATA_DIR / "calendar.json", events)
            return self._send_json({"status": "created", "item": payload}, 201)

        elif path == "/api/reading-list":
            items = read_json_file(DATA_DIR / "reading_list.json", [])
            payload["id"] = int(time.time() * 1000)
            items.append(payload)
            write_json_file(DATA_DIR / "reading_list.json", items)
            return self._send_json({"status": "created", "item": payload}, 201)

        elif path.startswith("/api/plugins/"):
            plugin_name = path[len("/api/plugins/"):].split("/")[0]
            if plugin_name not in PLUGINS:
                load_plugins()
            if plugin_name in PLUGINS:
                try:
                    res = PLUGINS[plugin_name]["module"].handle_request("POST", {}, payload)
                    return self._send_json(res)
                except Exception as e:
                    return self._send_json({"error": f"Plugin execution error: {str(e)}"}, 500)
            return self._send_json({"error": f"Plugin '{plugin_name}' not found."}, 404)

        return self._send_json({"error": "Method not supported"}, 405)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)
        item_id = int(query.get("id", [0])[0])

        if path == "/api/calendar":
            events = read_json_file(DATA_DIR / "calendar.json", [])
            events = [e for e in events if e.get("id") != item_id]
            write_json_file(DATA_DIR / "calendar.json", events)
            return self._send_json({"status": "deleted", "id": item_id})

        elif path == "/api/reading-list":
            items = read_json_file(DATA_DIR / "reading_list.json", [])
            items = [i for i in items if i.get("id") != item_id]
            write_json_file(DATA_DIR / "reading_list.json", items)
            return self._send_json({"status": "deleted", "id": item_id})

        return self._send_json({"error": "Method not allowed"}, 405)

def run():
    load_plugins()
    server = HTTPServer(("0.0.0.0", PORT), IntranetAPIHandler)
    print(f"Intranet Backend Server running on http://0.0.0.0:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    run()
