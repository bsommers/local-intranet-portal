# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-06

### Added
- **Reverse Proxy Architecture:** Nginx dual-stack listener on port 8088 (`0.0.0.0:8088` and `[::]:8088`) reverse-proxying dynamic `/api/*` traffic to the Python backend on port 8081.
- **Backend API Gateway:** Zero-dependency asynchronous HTTP server (`backend/server.py`) with clean endpoints for system stats, source tree navigation, reports, calendar, and reading lists.
- **Dual Source Explorer:** Interactive source code tree and syntax-highlighted viewer for `~/src` and `~/ecosystem` with path traversal security boundaries.
- **Reading DB Integration:** Clickable hyperlinks for reading list items with direct upstream integration to `github.com/bsommers/reading-db` and live plugin `plugins/reading_db_sync.py`.
- **Dynamic Plugin Substrate:** Hot-pluggable Python module system under `plugins/` automatically exposed at `/api/plugins/<plugin_name>` (`hello_plugin.py`, `math_runner.py`, `reading_db_sync.py`).
- **Container Infrastructure:** Multi-stage `Dockerfile` (Python 3.12 Alpine + Nginx), `docker-compose.yml`, and `build-container.sh` supporting Docker, Podman, and Buildah.
- **Frontend Dashboard:** Dark glassmorphic responsive SPA featuring real-time host telemetry (32 cores, 197GB RAM), Chart.js charts, and KaTeX mathematical scratchpad.
- **Documentation & Verification:** Added `CAPABILITIES.md`, `capabilities.json`, `docs/ARCHITECTURE.md`, and automated coherence verification script `scripts/check_docs.py`.

### Security & Portability
- Bound to RFC 1918 LAN interfaces for home network access without internet exposure.
- Sanitized hardcoded user paths to portable `Path.home()` and environment defaults (`SRC_ROOT`, `ECO_ROOT`).
- Added comprehensive `.gitignore` preventing log, pid, or credential leakage into the repository.
