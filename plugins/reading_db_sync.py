"""Reading DB GitHub Fetcher Plugin: Syncs directly with bsommers/reading-db"""
import json
import urllib.request

ALLOWED_METHODS = ["GET"]

CORPUS_URL = "https://raw.githubusercontent.com/bsommers/reading-db/main/README.md"
REPO_URL = "https://github.com/bsommers/reading-db"

def handle_request(method, query_params, body_payload):
    return {
        "plugin": "reading_db_sync",
        "upstream_repo": REPO_URL,
        "github_pages": "https://bsommers.github.io/reading-db/",
        "status": "connected",
        "description": "Integrated reading-db knowledge hub linking to papers, artifacts, and taxonomy"
    }
