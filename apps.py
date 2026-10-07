"""App templates for ai-factory. Each template generates a complete, working project."""
import json, os, datetime

def _readme(name, desc, features, install, usage, api_key, tech, links):
    d = datetime.datetime.now().strftime("%B %Y")
    feat_md = "\n".join(f"- **{f}**" for f in features)
    tech_md = " ".join(f"`{t}`" for t in tech)
    links_md = "\n".join(f"[{k}]({v})" for k, v in links.items()) if links else ""
    return f"""# {name}

> {desc}

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![AI](https://img.shields.io/badge/AI-Powered-purple)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

</div>

## Why {name}?

{desc} Built by [Alan Vo](https://github.com/ALANDVO) — AI/ML & cybersecurity engineer.

## Features

{feat_md}

## Quick Start

```bash
git clone https://github.com/ALANDVO/{name}.git
cd {name}
{install}
```

## Usage

```
{usage}
```

## API Keys

Set your provider key:
```bash
export {api_key}="your-key-here"
```

Works with: OpenAI, Anthropic (Claude), Google Gemini, Ollama (local), or any OpenAI-compatible endpoint.

## Tech Stack

{tech_md}

## License

MIT — see [LICENSE](LICENSE)

---

**Built by [Alan Vo](https://github.com/ALANDVO)** | [GitHub](https://github.com/ALANDVO) | AI, ML & Cybersecurity

{links_md}
"""

def _license():
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

def _gitignore():
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
"""

def _requirements():
    return """requests>=2.31.0
python-dotenv>=1.0.0
"""

def _env_example(key):
    return f"""# Copy to .env and fill in
{key}=your-api-key-here
# Optional: use local Ollama instead
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL=llama3
"""

def _llm_client():
    return '''"""Unified LLM client — works with OpenAI, Claude, Gemini, Ollama, or any OpenAI-compatible API."""
import os, json, requests

class LLM:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("LLM_API_KEY", "")
        self.base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = os.environ.get("LLM_MODEL", "gpt-4o")

    def chat(self, messages, temperature=0.7, max_tokens=2048):
        """Send chat completion request. Returns assistant message string."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        r = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def classify(self, text, categories, instructions=""):
        """Classify text into one of the given categories. Returns category + confidence + reasoning."""
        prompt = f"{instructions}Classify the following text into one of these categories: {', '.join(categories)}.\\n\\nText: {text}\\n\\nRespond as JSON: {{\\"category\\": \\"...\\", \\"confidence\\": 0.95, \\"reasoning\\": \\"...\\", \\"key_findings\\": [\\"...\\"]}}"
        raw = self.chat([{"role": "system", "content": "You are an expert classifier. Respond only with valid JSON."}, {"role": "user", "content": prompt}])
        # Extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            return {"category": "unknown", "confidence": 0.0, "reasoning": raw, "key_findings": []}

    def extract(self, text, schema, instructions=""):
        """Extract structured data from text according to schema. Returns dict."""
        prompt = f"{instructions}Extract the following fields from the text:\\n{json.dumps(schema, indent=2)}\\n\\nText: {text}\\n\\nRespond as JSON matching the schema."
        raw = self.chat([{"role": "system", "content": "You are an expert data extraction engine. Respond only with valid JSON."}, {"role": "user", "content": prompt}])
        start, end = raw.find("{"), raw.rfind("}") + 1
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            return {"error": "parse_failed", "raw": raw}

    def generate(self, prompt, system="You are a helpful AI assistant.", temperature=0.7):
        return self.chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}], temperature=temperature)
'''

def _app_main(app_name, desc, main_code):
    return f"""#!/usr/bin/env python3
\"\"\"{app_name} — {desc}\"\"\"
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import LLM
{main_code}

if __name__ == "__main__":
    main()
"""
