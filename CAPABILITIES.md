# System Capabilities

Human-readable registry of verified platform capabilities. For machine consumption, see [capabilities.json](capabilities.json).

| ID | Category | Capability | Status | Endpoint / Target |
|---|---|---|---|---|
| `cap-telemetry` | Observability | Live Linux kernel resource monitoring | Verified | `GET /api/system/status` |
| `cap-src-viewer` | Developer Tools | Dual source tree explorer for `~/src` and `~/ecosystem` | Verified | `GET /api/sources/list`, `GET /api/sources/read` |
| `cap-reading-db` | Knowledge Hub | Hyperlinked reading list with `bsommers/reading-db` sync | Verified | `GET /api/reading-list`, `GET /api/plugins/reading_db_sync` |
| `cap-math-repl` | Computation | Safe arithmetic & mathematical formula evaluator | Verified | `POST /api/plugins/math_runner` |
| `cap-plugins` | Extensibility | Hot-pluggable Python microservice substrate | Verified | `GET /api/plugins` |
| `cap-container` | Deployment | Hermetic container runtime (Docker / Podman / Buildah) | Verified | `Dockerfile`, `docker-compose.yml` |
| `cap-lan-reach` | Networking | Dual-stack 0.0.0.0 and [::] LAN binding | Verified | Port 8088 |
