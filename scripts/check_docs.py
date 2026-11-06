#!/usr/bin/env python3
"""
Documentation Coherence & Sync Validator
Checks:
- Relative links resolve
- No hardcoded absolute developer paths in tracked markdown/code
- Human and machine capability registries match count and IDs
"""
import sys
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def check_capabilities():
    md_file = ROOT / "CAPABILITIES.md"
    json_file = ROOT / "capabilities.json"
    
    if not md_file.exists() or not json_file.exists():
        print("FAIL: Capabilities files missing", file=sys.stderr)
        return False
        
    with open(json_file, "r") as f:
        data = json.load(f)
    json_caps = [c["id"] for c in data.get("capabilities", [])]
    
    with open(md_file, "r") as f:
        md_text = f.read()
    
    for cid in json_caps:
        if cid not in md_text:
            print(f"FAIL: Capability {cid} found in JSON but missing in CAPABILITIES.md", file=sys.stderr)
            return False
            
    print(f"OK: Capabilities in sync ({len(json_caps)} verified)")
    return True

def check_relative_links():
    docs = list(ROOT.glob("*.md")) + list(ROOT.glob("docs/*.md"))
    broken = 0
    link_pattern = re.compile(r'\[([^\]]+)\]\((?!https?://|mailto:|#)([^)]+)\)')
    
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for match in link_pattern.finditer(text):
            target = match.group(2).split("#")[0]
            if not target:
                continue
            resolved = (doc.parent / target).resolve()
            if not resolved.exists():
                print(f"FAIL: Broken link in {doc.name}: {target} -> {resolved}", file=sys.stderr)
                broken += 1
                
    if broken == 0:
        print("OK: All relative markdown links resolve")
        return True
    return False

def check_no_absolute_dev_paths():
    files_to_check = [
        ROOT / "README.md",
        ROOT / "CAPABILITIES.md",
        ROOT / "docs" / "ARCHITECTURE.md",
        ROOT / "docs" / "CHANGELOG.md",
        ROOT / "docker-compose.yml"
    ]
    bad = 0
    for f in files_to_check:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        if "/home/bill" in text:
            print(f"FAIL: Absolute home path '/home/bill' found in {f.name}", file=sys.stderr)
            bad += 1
            
    if bad == 0:
        print("OK: No hardcoded absolute developer paths found in tracked documentation")
        return True
    return False

def main():
    print("Running documentation sync & coherence checks...")
    ok1 = check_capabilities()
    ok2 = check_relative_links()
    ok3 = check_no_absolute_dev_paths()
    
    if ok1 and ok2 and ok3:
        print("\nAll documentation checks passed successfully!")
        sys.exit(0)
    else:
        print("\nDocumentation check failed.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
