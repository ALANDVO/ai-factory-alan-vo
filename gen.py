#!/usr/bin/env python3
"""ai-factory: Generate and push AI/ML repos to GitHub. Each repo is a complete, working project."""
import json, os, sys, subprocess, random, datetime, hashlib

GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GH_USER = "ALANDVO"
BASE = os.path.expanduser("~/ai-factory/repos")
LOG = os.path.expanduser("~/ai-factory/pushed.log")

def log(msg):
    print(msg)
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")

def api(path, method="GET", data=None):
    import urllib.request
    url = f"https://api.github.com{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"token {GH_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "ai-factory")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        try:
            return json.loads(e.read())
        except:
            return {"error": str(e)}

def exists(name):
    r = api(f"/repos/{GH_USER}/{name}")
    return "id" in r

def create_repo(name, desc, homepage=""):
    if exists(name):
        return True
    d = {"name": name, "description": desc, "homepage": homepage, "private": False, "has_issues": True, "has_wiki": False}
    r = api("/user/repos", method="POST", data=d)
    if "id" in r:
        log(f"created repo: {name}")
        return True
    log(f"FAILED create {name}: {r}")
    return False

def push(dir, name):
    cd = lambda c: subprocess.run(c, shell=True, cwd=dir, capture_output=True, text=True)
    cd("git init")
    cd("git add -A")
    cd("git -c user.name='Alan Vo' -c user.email='alanvo@gmail.com' commit -m 'Initial commit'")
    url = f"https://{GH_TOKEN}@github.com/{GH_USER}/{name}.git"
    r = cd(f"git push -u {url} main")
    ok = r.returncode == 0
    log(f"push {name}: {'OK' if ok else 'FAIL ' + r.stderr[:200]}")
    return ok, "" if ok else r.stderr[:200]

def repo_name(app_name):
    """Format: <app-name>-alan-vo"""
    return f"{app_name}-alan-vo"
