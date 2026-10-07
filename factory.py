#!/usr/bin/env python3
"""ai-factory v3: Build enterprise apps, push to GitHub, 1-for-1 rotation, clean local."""
import sys, os, json, shutil, subprocess, datetime, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GH_USER = "ALANDVO"
EMAIL = "alanvo@gmail.com"
BASE = os.path.expanduser("~/ai-factory/repos")
LOG = os.path.expanduser("~/ai-factory/pushed.log")
STATE = os.path.expanduser("~/ai-factory/state.json")

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")

def api(path, method="GET", data=None):
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
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def exists(name):
    r = api(f"/repos/{GH_USER}/{name}")
    return "id" in r

def create_repo(name, desc, homepage=""):
    if exists(name):
        return True
    d = {"name": name, "description": desc, "homepage": homepage, "private": False, "has_issues": True, "has_wiki": False}
    r = api("/user/repos", method="POST", data=d)
    if "id" in r:
        log(f"  created: {name}")
        return True
    log(f"  FAILED create {name}: {r}")
    return False

def sh(cmd, cwd):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)

def push(dir, name):
    sh("git init", dir)
    sh("git add -A", dir)
    sh(f"git -c user.name='Alan Vo' -c user.email='{EMAIL}' commit -m 'Initial commit'", dir)
    url = f"https://{GH_TOKEN}@github.com/{GH_USER}/{name}.git"
    r = sh(f"git push -f -u {url} main", dir)
    ok = r.returncode == 0
    log(f"  push: {'OK' if ok else 'FAIL ' + r.stderr[:200]}")
    return ok, r.stderr[:200] if not ok else ""

def repo_name(app_name):
    return f"{app_name}-alan-vo"

def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return {"repos": []}

def save_state(state):
    with open(STATE, "w") as f:
        json.dump(state, f, indent=2)

def mark_pushed(name, is_update=False):
    state = load_state()
    now = datetime.datetime.now().isoformat()
    existing = next((r for r in state["repos"] if r["name"] == name), None)
    if existing:
        existing["updated_at"] = now
        if is_update:
            existing["update_count"] = existing.get("update_count", 0) + 1
    else:
        state["repos"].append({"name": name, "pushed_at": now, "updated_at": now, "update_count": 0})
    save_state(state)

def clean_local(name):
    dir = os.path.join(BASE, name)
    if os.path.exists(dir):
        shutil.rmtree(dir)
        log(f"  cleaned local: {name}")

# ─── File generation helpers ───

def gen_readme(name, desc, features, install, usage, api_key, tech, links=None):
    d = datetime.datetime.now().strftime("%B %Y")
    feat_md = "\n".join(f"- **{f}**" for f in features)
    tech_md = " ".join(f"`{t}`" for t in tech)
    links_md = "\n".join(f"[{k}]({v})" for k, v in (links or {}).items())
    return f"""# {name}

> {desc}

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-React-3178C6)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![SSO](https://img.shields.io/badge/SSO-SAML%20%2F%20OAuth2-8A2BE2)
![License](https://img.shields.io/badge/License-MIT-green)
![AI](https://img.shields.io/badge/AI-Powered-purple)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

</div>

## Why {name}?

{desc}

Built by [Alan Vo](https://github.com/ALANDVO) — AI/ML & cybersecurity engineer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     {name}                                    │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│  Frontend   │   API Layer │  Services   │   LLM Engine      │
│  React/TS   │  FastAPI    │  Domain     │  Multi-provider   │
│  Dashboard  │  SSO/SAML   │  Logic      │  OpenAI/Claude/   │
│  Real-time  │  JWT Auth   │  Processing │  Gemini/Ollama    │
└─────────────┴─────────────┴─────────────┴───────────────────┘
         │              │              │               │
         ▼              ▼              ▼               ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐
    │ Browser │   │  REST   │   │  Domain │   │  LLM API    │
    │  SPA    │   │  API    │   │  Logic  │   │  (any)      │
    └─────────┘   └─────────┘   └─────────┘   └─────────────┘
```

## Features

{feat_md}

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/{GH_USER}/{name}.git
cd {name}
cp .env.example .env
docker compose up -d
# Open http://localhost:3000
```

### Local Development

```bash
git clone https://github.com/{GH_USER}/{name}.git
cd {name}
{install}
```

## Usage

```
{usage}
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `{api_key}` | LLM API key (OpenAI, Anthropic, Gemini) | Required |
| `LLM_BASE_URL` | Custom LLM endpoint (Ollama, vLLM) | `https://api.openai.com/v1` |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `SAML_IDP_ENTITY` | SAML Identity Provider URL | — |
| `JWT_SECRET` | JWT signing secret | Generate one |

## Tech Stack

{tech_md}

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login (SSO or email) |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/stats` | Statistics & metrics |
| `POST` | `/api/process` | Main processing endpoint |
| `GET` | `/api/results` | Query results |

## SSO Setup

### SAML
1. Set `SAML_IDP_ENTITY` to your IdP URL
2. Set `SAML_IDP_CERT` to your IdP certificate
3. Set `SAML_ACS_URL` to `https://yourdomain.com/saml/acs`

### OAuth2
1. Register your app with the OAuth provider
2. Set `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`
3. Set `OAUTH_REDIRECT_URI`

## License

MIT — see [LICENSE](LICENSE)

---

**Built by [Alan Vo](https://github.com/ALANDVO)** | alanvo@gmail.com | AI, ML & Cybersecurity

{links_md}
"""

def gen_license():
    return """MIT License

Copyright (c) 2026 Alan Vo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def gen_gitignore():
    return """__pycache__/
*.pyc
.env
.venv/
venv/
node_modules/
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
*.log
.DS_Store
frontend/node_modules/
frontend/dist/
"""

def gen_requirements(tech=None):
    base = """requests>=2.31.0
python-dotenv>=1.0.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6
"""
    if tech:
        if any("AWS" in t or "boto3" in t for t in tech):
            base += "boto3>=1.28.0\n"
        if any("GCP" in t or "Google" in t for t in tech):
            base += "google-cloud-bigquery>=3.11.0\ngoogle-cloud-storage>=2.10.0\n"
        if any("Azure" in t for t in tech):
            base += "azure-identity>=1.15.0\nazure-mgmt-resource>=21.0.0\n"
    return base

def gen_env_example(api_key):
    return f"""# LLM Configuration
{api_key}=your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o

# Auth
JWT_SECRET=generate-a-random-secret-here
# SAML_IDP_ENTITY=https://your-idp.com/saml
# SAML_ACS_URL=https://yourdomain.com/saml/acs

# Server
HOST=0.0.0.0
PORT=8000
"""

def gen_dockerfile(tech=None):
    return """FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Frontend (if exists)
RUN if [ -d "frontend" ]; then \\
    cd frontend && \\
    npm ci && \\
    npm run build; \\
    fi

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \\
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

def gen_docker_compose():
    return """services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""

def gen_contributing(name):
    return f"""# Contributing to {name}

## Setup
```bash
git clone https://github.com/ALANDVO/{name}.git
cd {name}
pip install -r requirements.txt
cp .env.example .env
```

## Code Style
- Python 3.10+, type hints, docstrings
- TypeScript strict mode for frontend
- No hardcoded secrets

## Submitting Changes
1. Fork → feature branch → test → PR
2. Include: what changed, why, how to test

## Issues
- Steps to reproduce
- Expected vs actual
- Log output (redact keys)

---
**Alan Vo** | alanvo@gmail.com | [GitHub](https://github.com/ALANDVO)
"""

def gen_main_py(name, desc, files):
    """Generate main.py entry point if not in files."""
    if "main.py" in files:
        return
    files["main.py"] = f'''#!/usr/bin/env python3
# {name} - {desc}
import sys, os, logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="{name}", version="1.0.0", description="{desc}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {{"status": "ok", "service": "{name}", "version": "1.0.0"}}

@app.get("/api/stats")
async def stats():
    return {{"service": "{name}", "version": "1.0.0"}}

# Serve frontend if built
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
'''

def build_app(app_def):
    """Create the full project directory from app definition."""
    name = repo_name(app_def["name"])
    dir = os.path.join(BASE, name)
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir, exist_ok=True)

    # Standard files
    files = {}
    files["README.md"] = gen_readme(name, app_def["desc"], app_def["features"], app_def["install"], app_def["usage"], app_def["api_key"], app_def["tech"], app_def.get("links"))
    files["LICENSE"] = gen_license()
    files[".gitignore"] = gen_gitignore()
    files["requirements.txt"] = gen_requirements(app_def.get("tech"))
    files[".env.example"] = gen_env_example(app_def["api_key"])
    files["Dockerfile"] = gen_dockerfile(app_def.get("tech"))
    files["docker-compose.yml"] = gen_docker_compose()
    files["CONTRIBUTING.md"] = gen_contributing(name)
    files[".github/CODEOWNERS"] = f"* @{GH_USER.lower()}\n"

    # App-specific files
    if "files" in app_def and app_def["files"]:
        files.update(app_def["files"])
    elif "main_code" in app_def:
        _name = app_def["name"]
        _desc = app_def["desc"]
        _code = app_def["main_code"]
        files["main.py"] = (f"#!/usr/bin/env python3\n"
                          f"# {_name} — {_desc}\n"
                          f"import sys, os\n"
                          f"sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
                          f"from llm_client import LLM\n"
                          f"{_code}\n"
                          f"if __name__ == '__main__':\n"
                          f"    main()\n")
        # Also add llm_client.py
        files["llm_client.py"] = """# Unified LLM client.
import os, json, requests

class LLM:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("LLM_API_KEY", "")
        self.base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = os.environ.get("LLM_MODEL", "gpt-4o")

    def chat(self, messages, temperature=0.7, max_tokens=2048):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        r = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def classify(self, text, categories, instructions=""):
        sep = ", "
        prompt = f"{instructions}Classify: {text}\nCategories: {sep.join(categories)}\nRespond as JSON: {{"category": "...", "confidence": 0.95, "reasoning": "..."}}"
        raw = self.chat([{"role": "system", "content": "Respond only with valid JSON."}, {"role": "user", "content": prompt}])
        start, end = raw.find("{"), raw.rfind("}") + 1
        try:
            return json.loads(raw[start:end])
        except:
            return {"category": "unknown", "confidence": 0.0, "reasoning": raw}

    def generate(self, prompt, system="You are a helpful AI assistant.", temperature=0.7):
        return self.chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}], temperature=temperature)
"""

    # Write all files
    total_bytes = 0
    for path, content in files.items():
        full = os.path.join(dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
        total_bytes += len(content)

    log(f"  built: {len(files)} files, {total_bytes:,} bytes")
    return dir, name

def load_all_apps():
    """Load apps from all appdefs files."""
    all_apps = []
    modules = [
        ("appdefs", "APPS"),
        ("appdefs_batch2", "APPS"),
        ("appdefs_batch3", "APPS"),
        ("appdefs_enterprise", "APPS"),
        ("appdefs_enterprise2", "APPS"),
        ("appdefs_cloud", "APPS"),
    ]
    for mod_name, var in modules:
        try:
            mod = __import__(mod_name)
            apps = getattr(mod, var, [])
            if apps:
                log(f"  loaded {len(apps)} apps from {mod_name}")
                all_apps.extend(apps)
        except ImportError:
            pass
    return all_apps

def update_repo(repo_entry, all_apps):
    """Pull, enhance, and push an existing repo."""
    name = repo_entry["name"]
    # Find the app definition
    app = None
    for a in all_apps:
        if repo_name(a["name"]) == name:
            app = a
            break
    if not app:
        log(f"  No app definition found for {name}")
        return

    dir = os.path.join(BASE, name)
    # Clone existing repo
    url = f"https://{GH_TOKEN}@github.com/{GH_USER}/{name}.git"
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(os.path.dirname(dir), exist_ok=True)
    sh(f"git clone {url} {dir}", ".")

    # Rebuild app files over existing
    build_app_into(app, dir)

    # Commit and push
    sh("git add -A", dir)
    r = sh(f"git -c user.name='Alan Vo' -c user.email='{EMAIL}' commit -m 'Update cycle {repo_entry.get('update_count', 0) + 1}'", dir)
    if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
        log(f"  commit: {r.stderr[:100]}")
        return

    r = sh(f"git push {url} main", dir)
    if r.returncode == 0:
        mark_pushed(name, is_update=True)
        clean_local(name)
        log(f"  UPDATED: https://github.com/{GH_USER}/{name}")
    else:
        log(f"  push: FAIL {r.stderr[:200]}")

def build_app_into(app_def, dir):
    """Write app files into an existing directory (for updates)."""
    files = {}
    # Generate standard files
    name = repo_name(app_def["name"])
    desc = app_def["desc"]
    features = app_def.get("features", [])
    install = app_def.get("install", "")
    usage = app_def.get("usage", "")
    api_key = app_def.get("api_key", "")
    tech = app_def.get("tech", [])
    links = app_def.get("links")

    files["README.md"] = gen_readme(name, desc, features, install, usage, api_key, tech, links)
    files["LICENSE"] = gen_license()
    files[".gitignore"] = gen_gitignore()
    files["requirements.txt"] = gen_requirements()
    files["Dockerfile"] = gen_dockerfile()
    files["docker-compose.yml"] = gen_docker_compose()
    files["CONTRIBUTING.md"] = gen_contributing(name)
    files[".github/CODEOWNERS"] = f"* @{GH_USER.lower()}\n"

    # App-specific files
    if "files" in app_def and app_def["files"]:
        files.update(app_def["files"])

    # Write all files
    for path, content in files.items():
        full = os.path.join(dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)

def main():
    log("=" * 60)
    log(f"ai-factory run @ {datetime.datetime.now().isoformat()}")
    log("=" * 60)

    all_apps = load_all_apps()
    if not all_apps:
        log("No apps found! Create appdefs files first.")
        return

    state = load_state()
    pushed = {r["name"] for r in state["repos"]}

    # Pick next unpushed app
    app = None
    for a in all_apps:
        name = repo_name(a["name"])
        if name not in pushed:
            app = a
            break

    if not app:
        log("All apps pushed! Starting update cycle.")
        # Update oldest repo
        if state["repos"]:
            repos = sorted(state["repos"], key=lambda r: r.get("updated_at", r["pushed_at"]))
            oldest = repos[0]
            log(f"Updating oldest: {oldest['name']} (updates: {oldest.get('update_count', 0)})")
            update_repo(oldest, all_apps)
        return

    name = repo_name(app["name"])
    log(f"Building: {name}")

    dir, name = build_app(app)

    if not create_repo(name, app["desc"]):
        log("FAILED: could not create repo")
        return

    ok, err = push(dir, name)
    if ok:
        mark_pushed(name)
        clean_local(name)
        log(f"  DONE: https://github.com/{GH_USER}/{name}")
    else:
        log(f"  FAILED: {err}")

if __name__ == "__main__":
    main()
