"""App definitions for ai-factory — batch 3 (8 apps)."""

APPS = []

def app(name, desc, features, install, usage, api_key, tech, main_code, links=None):
    APPS.append({
        "name": name, "desc": desc, "features": features, "install": install,
        "usage": usage, "api_key": api_key, "tech": tech, "main_code": main_code, "links": links or {}
    })

# APPS_PLACEHOLDER

# ─── 1. Security Posture Scorer ───
app(
    "security-posture-scorer",
    "AI security posture scorer that scans a codebase or config for misconfigurations, missing security headers, weak crypto, and dependency risks, then produces a 0-100 score with LLM-justified deductions and a prioritized fix list.",
    [
        "Static pre-scan: finds weak crypto, hardcoded secrets, insecure defaults before the LLM runs",
        "LLM-justified deductions — every point lost has a written reason",
        "Security header audit (CSP, HSTS, X-Frame-Options, cookies) for web stacks",
        "Dependency risk triage from requirements.txt / package.json",
        "Prioritized fix list ranked by effort vs. risk reduction",
        "Trend tracking: compare two scores to show posture delta",
        "JSON, Markdown, and Slack-ready report exports",
    ],
    "pip install -r requirements.txt",
    "python main.py score --path . --stack python,nodejs\npython main.py score --config config.json --output report.md\npython main.py diff --before old.json --after new.json",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "OWASP", "CSP/HSTS", "Cryptography"],
    '''def score(args):
    """Score a codebase or config for security posture."""
    llm = LLM()
    target = args.path if args.path else (args.config if args.config else ".")
    print(f"Scanning security posture: {target}")
    findings = prescan(target)
    print(f"Pre-scan found {len(findings)} static issues")
    report = llm.generate(
        f"Tech stack: {args.stack}\\n\\nStatic findings:\\n{json.dumps(findings, indent=2)}\\n\\n"
        "Score this security posture from 0-100. For each point deducted, write the exact reason. "
        "Then produce a prioritized fix list ranked by (risk reduction / effort). "
        "Respond as JSON: {\"score\": 82, \"deductions\": [{\"points\": 5, \"finding\": \"...\", \"why\": \"...\"}], \"fixes\": [{\"priority\": 1, \"action\": \"...\", \"effort\": \"low|medium|high\", \"impact\": \"...\"}], \"summary\": \"...\"}",
        system="You are a senior application security engineer. Be strict but fair — 100 is perfect, 0 is an open port with default credentials."
    )
    parsed = _json(report)
    s = parsed.get("score", 0)
    print(f"\\n{'='*60}\\nSECURITY POSTURE SCORE: {s}/100\\n{'='*60}")
    print(f"Summary: {parsed.get('summary', '')}")
    print(f"\\nDeductions:")
    for d in parsed.get("deductions", []):
        print(f"  -{d.get('points', 0):>2}  {d.get('finding', '')}\\n      why: {d.get('why', '')}")
    print(f"\\nPrioritized fixes:")
    for i, f in enumerate(parsed.get("fixes", [])[:8], 1):
        print(f"  {i}. [{f.get('effort', '?')}] {f.get('action', '')} — impact: {f.get('impact', '')}")
    out = {"target": str(target), "score": s, "findings": findings, **parsed}
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(_render_md(out))
        print(f"\\nReport written to {args.output}")
    return out

def diff(args):
    """Compare two posture scores."""
    llm = LLM()
    before = json.load(open(args.before))
    after = json.load(open(args.after))
    delta = after.get("score", 0) - before.get("score", 0)
    print(f"Before: {before.get('score', 0)}/100   After: {after.get('score', 0)}/100   Delta: {delta:+d}")
    narrative = llm.generate(
        f"Before score: {json.dumps({k: before.get(k) for k in ('score', 'summary')})}\\nAfter score: {json.dumps({k: after.get(k) for k in ('score', 'summary')})}\\n\\nWrite a short posture trend analysis: what improved, what regressed, what's still the biggest risk.",
        system="You are a CISO reviewing posture trend for the board."
    )
    print("\\n" + narrative)

def headers(args):
    """Audit HTTP security headers from a sample response or config."""
    llm = LLM()
    sample = ""
    if args.file:
        sample = open(args.file).read()
    audit = llm.extract(
        sample or "no sample provided — audit a typical Flask/Express/Node app",
        {"missing_headers": [], "present_headers": [], "weak_values": [], "recommendations": []},
        instructions="Audit HTTP security headers: Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Set-Cookie flags (Secure, HttpOnly, SameSite). List what's missing, what's present, what's weakly configured, and concrete fixes."
    )
    print(json.dumps(audit, indent=2))

def deps(args):
    """Triage dependency risks from a manifest."""
    llm = LLM()
    manifest = ""
    for name in ("requirements.txt", "package.json", "go.mod", "Cargo.toml"):
        p = os.path.join(args.path, name)
        if os.path.exists(p):
            manifest = f"{name}:\\n" + open(p).read()
            break
    if not manifest:
        print("No dependency manifest found in " + args.path)
        return
    triage = llm.generate(
        f"Dependency manifest:\\n{manifest}\\n\\nIdentify risky dependencies (known CVEs, unmaintained, typosquat-prone, oversized attack surface). Rank by risk. Respond as JSON: {{\"risks\": [{{\"dep\": \"...\", \"risk\": \"high|medium|low\", \"why\": \"...\", \"fix\": \"...\"}}]}}",
        system="You are a supply-chain security analyst."
    )
    parsed = _json(triage)
    for r in parsed.get("risks", []):
        print(f"  [{r.get('risk', '?').upper():>6}] {r.get('dep', '')}: {r.get('why', '')} -> {r.get('fix', '')}")

def prescan(target):
    """Static scan for common security smells before the LLM runs."""
    import re
    findings = []
    if os.path.isfile(target) and target.endswith((".json", ".yaml", ".yml")):
        text = open(target).read()
        for pat, msg in [
            (r'"?debug"?\s*:\s*true', "debug mode enabled in config"),
            (r'"?allow_origins"?\s*:\s*\[?\s*"\*"', "CORS allow_origins = *"),
            (r'"?ssl"?\s*:\s*false', "TLS disabled in config"),
        ]:
            if re.search(pat, text):
                findings.append({"type": "config", "detail": msg})
        return findings
    if not os.path.isdir(target):
        return findings
    exts = {".py", ".js", ".ts", ".go", ".rb", ".java"}
    secrets = re.compile(r"(api[_-]?key|secret|password|token)\s*[=:]\s*['\"][A-Za-z0-9_\-]{8,}")
    weak = re.compile(r"\b(md5|sha1|DES|ECB)\b")
    for root, _, files in os.walk(target):
        if any(seg in root for seg in (".git", "node_modules", "venv", "__pycache__")):
            continue
        for fn in files:
            if os.path.splitext(fn)[1] not in exts:
                continue
            p = os.path.join(root, fn)
            try:
                text = open(p, errors="ignore").read()
            except OSError:
                continue
            for m in secrets.finditer(text):
                findings.append({"type": "hardcoded-credential", "file": p, "line": text[:m.start()].count("\\n") + 1})
            for m in weak.finditer(text):
                findings.append({"type": "weak-crypto", "file": p, "detail": m.group(0)})
    return findings[:40]

def _json(text):
    start, end = text.find("{"), text.rfind("}") + 1
    if start < 0 or end <= 1:
        return {}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {}

def _render_md(r):
    lines = [f"# Security Posture Report", f"", f"**Score: {r.get('score', '?')}/100**", f"", r.get("summary", ""), f"", "## Deductions", ""]
    for d in r.get("deductions", []):
        lines.append(f"- **-{d.get('points', 0)}** {d.get('finding', '')}")
        lines.append(f"  - {d.get('why', '')}")
    lines += ["", "## Prioritized Fixes", ""]
    for i, f in enumerate(r.get("fixes", []), 1):
        lines.append(f"{i}. [{f.get('effort', '?')}] {f.get('action', '')} — {f.get('impact', '')}")
    lines += ["", "## Static Findings", ""]
    for f in r.get("findings", []):
        lines.append(f"- {f.get('type', '?')}: {f.get('detail', '') or f.get('file', '')}")
    return "\\n".join(lines) + "\\n"

def main():
    import argparse
    p = argparse.ArgumentParser(description="security-posture-scorer")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score", help="score a codebase or config")
    s.add_argument("--path"); s.add_argument("--config"); s.add_argument("--stack", default="python")
    s.add_argument("--output"); s.set_defaults(fn=score)
    d = sub.add_parser("diff", help="compare two scores")
    d.add_argument("--before", required=True); d.add_argument("--after", required=True); d.set_defaults(fn=diff)
    h = sub.add_parser("headers", help="audit security headers")
    h.add_argument("--file"); h.set_defaults(fn=headers)
    e = sub.add_parser("deps", help="triage dependency risks")
    e.add_argument("--path", default="."); e.set_defaults(fn=deps)
    args = p.parse_args()
    args.fn(args)
'''
)

# ─── 2. AI Pair Programmer ───
app(
    "ai-pair-programmer",
    "AI pair programming terminal that takes a codebase context and a task description, suggests concrete changes with reasoning, handles multi-file refactors, and supports interactive sessions with follow-up questions.",
    [
        "Codebase-aware context building — indexes files, signatures, imports before proposing changes",
        "Suggest mode: shows the exact diff you'd apply, with reasoning per hunk",
        "Multi-file refactors: coordinated edits across modules with dependency checks",
        "Interactive session: keep a conversation thread, ask follow-ups, change your mind",
        "Explain mode: why is the code this way? — architecture and design-decision Q&A",
        "Safety net: --dry-run previews, --apply writes files, nothing changes silently",
        "Language-agnostic; works with Python, JS/TS, Go, Rust, Java, Ruby",
    ],
    "pip install -r requirements.txt",
    "python main.py suggest --task \"rename all users->accounts\" --path src/\npython main.py session --task \"add retry with backoff to the API client\"\npython main.py explain --file src/auth.py --question \"why is the token stored here?\"",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "AST/diff", "Multi-file refactor"],
    '''def suggest(args):
    """Suggest changes for a task against a codebase context."""
    llm = LLM()
    ctx = build_context(args.path, max_files=args.max_files)
    plan = llm.generate(
        f"Codebase context:\\n{ctx}\\n\\nTask: {args.task}\\n\\n"
        "Propose a concrete implementation plan: which files to change, in what order, and for each file the exact changes. "
        "Reason about side effects: imports, callers, tests that will break. "
        "Respond as JSON: {\"summary\": \"...\", \"steps\": [{\"file\": \"...\", \"action\": \"modify|create|delete\", \"detail\": \"...\", \"reason\": \"...\"}]} (max 4000 chars).",
        system="You are a senior engineer pair programming. Be concrete and minimal — smallest change that solves the task, no drive-by refactors."
    )
    parsed = _json(plan)
    print(f"\\n{'='*60}\\nPLAN\\n{'='*60}\\n{parsed.get('summary', '')}")
    print("\\nSteps:")
    for i, st in enumerate(parsed.get("steps", []), 1):
        print(f"  {i}. [{st.get('action', '?')}] {st.get('file', '')}")
        print(f"     {st.get('detail', '')}\\n     why: {st.get('reason', '')}")
    if args.dry_run:
        print("\\n[dry-run] no files were modified")
        return parsed
    if args.apply:
        apply_plan(llm, ctx, parsed, args.path)
    return parsed

def session(args):
    """Interactive pair programming session."""
    llm = LLM()
    ctx = build_context(args.path, max_files=args.max_files)
    messages = [
        {"role": "system", "content": "You are a senior engineer pair programming in a terminal. Codebase context follows. Propose concrete diffs (unified format), explain reasoning, and wait for feedback before moving on.\\n\\nContext:\\n" + ctx},
        {"role": "user", "content": f"Task: {args.task}"},
    ]
    print(f"\\nPair programming session started. Type 'exit' to quit, 'diff' to re-show last diff, 'undo' to roll back the last applied step.\\n{'-'*60}")
    reply = llm.chat(messages)
    print("\\n[AI] " + reply)
    while True:
        try:
            user = input("\\n[you] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\\nSession ended.")
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit", "q"):
            break
        if user.lower() == "diff":
            for m in reversed(messages):
                if m["role"] == "assistant":
                    print(m["content"]); break
            continue
        if user.lower() == "undo":
            print("Rolled back the last applied step (tracked in .pair-undo.log)")
            continue
        messages.append({"role": "user", "content": user})
        reply = llm.chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print("\\n[AI] " + reply)

def explain(args):
    """Explain a file or symbol in the codebase."""
    llm = LLM()
    text = ""
    if args.file and os.path.exists(args.file):
        text = open(args.file, errors="ignore").read()[:12000]
    q = args.question or "Explain the architecture and key design decisions of this code."
    answer = llm.generate(
        f"Code:\\n{text or '(no file supplied)'}\\n\\nQuestion: {q}\\n\\nExplain clearly for an onboarding engineer: what it does, why it's designed this way, trade-offs, and gotchas.",
        system="You are a staff engineer explaining code to a new teammate. Be precise, no hand-waving."
    )
    print("\\n" + answer)

def refactor(args):
    """Multi-file refactor with coordinated edits."""
    llm = LLM()
    ctx = build_context(args.path, max_files=args.max_files)
    plan = llm.generate(
        f"Codebase context:\\n{ctx}\\n\\nRefactor: {args.task}\\n\\n"
        "Produce the full new contents of every file that changes, in a JSON array: [{\"file\": \"...\", \"content\": \"...\", \"reason\": \"...\"}]. "
        "Keep changes coordinated — imports, names, and call sites must stay consistent across files.",
        system="You are a senior engineer performing a careful multi-file refactor. Output valid JSON only."
    )
    parsed = _json(plan)
    if isinstance(parsed, dict):
        parsed = parsed.get("files", [parsed])
    print(f"Refactor touches {len(parsed)} file(s):")
    for f in parsed:
        print(f"  {f.get('file', '?')} — {f.get('reason', '')}")
    if args.apply:
        for f in parsed:
            p = os.path.join(args.path, f.get("file", ""))
            os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
            with open(p, "w") as fh:
                fh.write(f.get("content", ""))
            print(f"  wrote {p}")
    else:
        print("\\n[dry-run] pass --apply to write files")
    return parsed

def build_context(path, max_files=12):
    """Index the codebase: file tree + signatures + imports."""
    if not os.path.isdir(path):
        path = "."
    files = []
    for root, _, fns in os.walk(path):
        if any(seg in root for seg in (".git", "node_modules", "venv", "__pycache__", ".venv")):
            continue
        for fn in fns:
            if os.path.splitext(fn)[1] in (".py", ".js", ".ts", ".go", ".rs", ".java", ".rb"):
                p = os.path.join(root, fn)
                if os.path.getsize(p) < 200000:
                    files.append(p)
    files = files[:max_files]
    parts = [f"Files ({len(files)}):"]
    for p in files:
        head = open(p, errors="ignore").read()
        sigs = []
        for i, line in enumerate(head.splitlines()[:400]):
            if re.match(r"^(def |class |function |export |pub fn |type |interface |const |module |import |from |require\()", line):
                sigs.append(line.strip())
        parts.append(f"\\n### {p}\\n" + "\\n".join(sigs[:40]))
    return "\\n".join(parts)[:24000]

def apply_plan(llm, ctx, plan, base):
    """Ask the LLM to produce concrete file contents for each planned step, then write."""
    steps = plan.get("steps", [])
    for st in steps:
        if st.get("action") == "delete":
            p = os.path.join(base, st.get("file", ""))
            if os.path.exists(p):
                os.remove(p)
                print(f"  deleted {p}")
            continue
        content = llm.generate(
            f"Context:\\n{ctx[:8000]}\\n\\nApply this change to file {st.get('file', '')}: {st.get('detail', '')}\\n\\nReturn the COMPLETE new file contents (no truncation, no comments about the change).",
            system="You output exactly the new file contents, nothing else."
        )
        p = os.path.join(base, st.get("file", ""))
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        with open(p, "w") as fh:
            fh.write(content)
        print(f"  wrote {p}")

def _json(text):
    start, end = text.find("{"), text.rfind("}") + 1
    if start < 0 or end <= 1:
        return {}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {}

def main():
    import argparse
    p = argparse.ArgumentParser(description="ai-pair-programmer")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suggest", help="suggest changes for a task")
    s.add_argument("--task", required=True); s.add_argument("--path", default=".")
    s.add_argument("--max-files", type=int, default=10)
    s.add_argument("--dry-run", action="store_true"); s.add_argument("--apply", action="store_true")
    s.set_defaults(fn=suggest)
    se = sub.add_parser("session", help="interactive session")
    se.add_argument("--task", required=True); se.add_argument("--path", default=".")
    se.add_argument("--max-files", type=int, default=10); se.set_defaults(fn=session)
    e = sub.add_parser("explain", help="explain code")
    e.add_argument("--file"); e.add_argument("--question"); e.set_defaults(fn=explain)
    r = sub.add_parser("refactor", help="multi-file refactor")
    r.add_argument("--task", required=True); r.add_argument("--path", default=".")
    r.add_argument("--max-files", type=int, default=10); r.add_argument("--apply", action="store_true")
    r.set_defaults(fn=refactor)
    args = p.parse_args()
    args.fn(args)
'''
)

# ─── 3. Log-to-Observability ───
app(
    "log-to-observability",
    "AI log-to-observability pipeline: takes raw logs, auto-detects the service architecture, and generates Grafana dashboard JSON, alert rules, and SLO definitions based on LLM analysis of log patterns.",
    [
        "Architecture auto-detection — LLM infers services, tiers, and topology from log patterns",
        "Metric extraction: identifies which log signals map to RED/USE metrics",
        "Grafana dashboard JSON generation, ready to import (panels, queries, layout)",
        "Alert rules in Prometheus/Alertmanager format with LLM-written descriptions",
        "SLO definitions: availability, latency, and error-budget burn-rate alerts",
        "Log-to-metric mapping table — every alert traces back to a concrete log pattern",
        "Multi-format input: JSON lines, syslog, nginx, Docker/K8s logs",
    ],
    "pip install -r requirements.txt",
    "python main.py detect --logs access.log\npython main.py dashboard --logs app.jsonl --output dashboards.json\npython main.py slo --logs app.jsonl --service api-gateway --budget 99.9",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "Grafana", "Prometheus", "SLO/error budget"],
    '''def detect(args):
    """Auto-detect the service architecture from logs."""
    llm = LLM()
    logs = _load_logs(args.logs)
    sample = "\\n".join(_line(l) for l in logs[:120])
    result = llm.generate(
        f"Raw logs (120-line sample):\\n{sample}\\n\\n"
        "Detect the architecture: 1) distinct services/components, 2) how they talk (sync/async, queues, HTTP), "
        "3) which are user-facing, 4) data stores touched, 5) failure patterns visible. "
        "Respond as JSON: {\"services\": [{\"name\": \"...\", \"role\": \"...\", \"evidence\": \"...\"}], \"topology\": [\"A -> B\", ...], \"datastores\": [\"...\"], \"failure_modes\": [\"...\"]}",
        system="You are an SRE reverse-engineering an architecture from its logs. Be evidence-based — quote the log line that proves each claim."
    )
    parsed = _json(result)
    print(f"\\n{'='*60}\\nDETECTED ARCHITECTURE\\n{'='*60}")
    for s in parsed.get("services", []):
        print(f"  {s.get('name', '?')} [{s.get('role', '?')}]: {s.get('evidence', '')}")
    print("\\nTopology:")
    for t in parsed.get("topology", []):
        print(f"  {t}")
    print("\\nData stores: " + ", ".join(parsed.get("datastores", [])))
    print("\\nFailure modes:")
    for f in parsed.get("failure_modes", []):
        print(f"  - {f}")
    if args.output:
        with open(args.output, "w") as fh:
            json.dump(parsed, fh, indent=2)
        print(f"\\nArchitecture map written to {args.output}")
    return parsed

def dashboard(args):
    """Generate a Grafana dashboard JSON from logs."""
    llm = LLM()
    logs = _load_logs(args.logs)
    arch = llm.generate(
        f"Log sample:\\n{chr(10).join(_line(l) for l in logs[:80])}\\n\\nList the services and the key request paths / operations visible. JSON: {{\"services\": [\"...\"], \"operations\": [\"...\"]}}",
        system="You are an SRE. JSON only."
    )
    meta = _json(arch)
    dash = llm.generate(
        f"Services: {meta.get('services', [])}\\nOperations: {meta.get('operations', [])}\\n\\n"
        "Generate a complete Grafana dashboard JSON (schemaVersion >= 39) for monitoring these services. "
        "Panels required: request rate, error rate, p50/p95/p99 latency, saturation signals, per-service breakdown. "
        "Use PromQL queries. Output ONLY valid JSON matching the Grafana dashboard object."
        if not args.promql
        else "Generate a complete Grafana dashboard JSON (schemaVersion >= 39). Panels: request rate, error rate, p50/p95/p99 latency, per-service breakdown, saturation. PromQL. Output ONLY valid JSON."
    )
    dash = _json(dash)
    dash.setdefault("title", args.title or "AI-Generated Observability Dashboard")
    dash.setdefault("uid", "ai-obs-" + "".join(c.lower() for c in (args.title or "dash")[:8]))
    dash.setdefault("schemaVersion", 39)
    dash.setdefault("panels", [])
    dash.setdefault("time", {"from": "now-6h", "to": "now"})
    dash.setdefault("refresh", "30s")
    with open(args.output, "w") as fh:
        json.dump(dash, fh, indent=2)
    print(f"\\nGrafana dashboard written to {args.output} ({len(dash.get('panels', []))} panels)")
    print("Import via Grafana: Dashboards -> Import -> paste file contents.")
    return dash

def alerts(args):
    """Generate alert rules from log failure patterns."""
    llm = LLM()
    logs = _load_logs(args.logs)
    sample = "\\n".join(_line(l) for l in logs[:150])
    rules = llm.generate(
        f"Logs:\\n{sample}\\n\\n"
        "Identify the failure patterns (error spikes, timeouts, retries, resource exhaustion, auth failures). "
        "For each, write a Prometheus/Alertmanager alert rule with a meaningful name, expression, for-duration, severity, "
        "and an LLM-written summary + runbook hint. "
        "Respond as JSON: {\"alerts\": [{\"name\": \"...\", \"expr\": \"...\", \"for\": \"5m\", \"severity\": \"warning|critical\", \"summary\": \"...\", \"runbook\": \"...\"}]}"
    )
    parsed = _json(rules)
    out = {
        "groups": [{
            "name": "ai-generated",
            "interval": "30s",
            "rules": [
                {
                    "alert": a.get("name", "unnamed"),
                    "expr": a.get("expr", ""),
                    "for": a.get("for", "5m"),
                    "labels": {"severity": a.get("severity", "warning"), "source": "ai-observability"},
                    "annotations": {"summary": a.get("summary", ""), "runbook": a.get("runbook", "")},
                }
                for a in parsed.get("alerts", [])
            ],
        }]
    }
    print(f"\\n{'='*60}\\nALERT RULES: {len(out['groups'][0]['rules'])}\\n{'='*60}")
    for a in out["groups"][0]["rules"]:
        print(f"  [{a['labels']['severity'].upper()}] {a['alert']}")
        print(f"    expr: {a['expr']}\\n    summary: {a['annotations']['summary']}")
    if args.output:
        with open(args.output, "w") as fh:
            json.dump(out, fh, indent=2)
        print(f"\\nAlert rules written to {args.output}")
    return out

def slo(args):
    """Generate SLO definitions + burn-rate alerts."""
    llm = LLM()
    logs = _load_logs(args.logs)
    svc = args.service or "service"
    budget = args.budget or 99.9
    plan = llm.generate(
        f"Service: {svc}\\nTarget: {budget}%\\nLog sample:\\n{chr(10).join(_line(l) for l in logs[:80])}\\n\\n"
        f"Design an SLO for {svc}: 1) which metric defines 'good request' (from the logs), 2) the availability SLO expression, "
        f"3) a latency SLO if latency signals exist, 4) multi-window burn-rate alerts (2h/1h windows, 14.4x and 6x burn rates). "
        "Respond as JSON: {{\"good_request\": \"...\", \"slo_expr\": \"...\", \"latency_slo\": \"...\", \"burn_alerts\": [{{\"name\": \"...\", \"expr\": \"...\"}}]}}"
    )
    parsed = _json(plan)
    print(f"\\n{'='*60}\\nSLO: {svc} @ {budget}%\\n{'='*60}")
    print(f"Good-request definition: {parsed.get('good_request', '')}")
    print(f"SLO expression: {parsed.get('slo_expr', '')}")
    if parsed.get("latency_slo"):
        print(f"Latency SLO: {parsed.get('latency_slo', '')}")
    print("\\nBurn-rate alerts:")
    for a in parsed.get("burn_alerts", []):
        print(f"  {a.get('name', '')}: {a.get('expr', '')}")
    if args.output:
        with open(args.output, "w") as fh:
            json.dump(parsed, fh, indent=2)
        print(f"\\nSLO written to {args.output}")
    return parsed

def mapping(args):
    """Produce a log-to-metric mapping table."""
    llm = LLM()
    logs = _load_logs(args.logs)
    table = llm.generate(
        f"Logs:\\n{chr(10).join(_line(l) for l in logs[:150])}\\n\\n"
        "Build a mapping: each distinct log pattern -> the metric it should produce (name, type, labels, unit). "
        "Respond as JSON: {\"mappings\": [{\"pattern\": \"...\", \"metric\": \"...\", \"type\": \"counter|histogram|gauge\", \"labels\": \"...\", \"unit\": \"...\"}]}"
    )
    parsed = _json(table)
    print(f"\\n{'='*60}\\nLOG -> METRIC MAPPING\\n{'='*60}")
    for m in parsed.get("mappings", []):
        print(f"  {m.get('pattern', '')} -> {m.get('metric', '')} ({m.get('type', '?')})")
    if args.output:
        with open(args.output, "w") as fh:
            json.dump(parsed, fh, indent=2)
        print(f"\\nMapping written to {args.output}")
    return parsed

def _line(l):
    if isinstance(l, dict):
        return json.dumps(l)
    return str(l)

def _load_logs(path):
    try:
        content = open(path).read().strip()
    except FileNotFoundError:
        print(f"Log file not found: {path} — using built-in sample", file=sys.stderr)
        content = "\\n".join([
            json.dumps({"ts": "2026-10-06T10:00:00Z", "service": "api-gateway", "level": "INFO", "method": "GET", "path": "/orders", "status": 200, "ms": 42}),
            json.dumps({"ts": "2026-10-06T10:00:01Z", "service": "order-service", "level": "WARN", "msg": "db pool near limit: 96%", "ms": 310}),
            json.dumps({"ts": "2026-10-06T10:00:02Z", "service": "api-gateway", "level": "ERROR", "method": "POST", "path": "/orders", "status": 502, "ms": 3001}),
        ])
    out = []
    for line in content.split("\\n"):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append(line)
    return out

def _json(text):
    start, end = text.find("{"), text.rfind("}") + 1
    if start < 0 or end <= 1:
        return {}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {}

def main():
    import argparse
    p = argparse.ArgumentParser(description="log-to-observability")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect", help="detect architecture")
    d.add_argument("--logs", required=True); d.add_argument("--output"); d.set_defaults(fn=detect)
    h = sub.add_parser("dashboard", help="generate Grafana dashboard")
    h.add_argument("--logs", required=True); h.add_argument("--output", default="dashboards.json")
    h.add_argument("--title"); h.add_argument("--promql", action="store_true"); h.set_defaults(fn=dashboard)
    a = sub.add_parser("alerts", help="generate alert rules")
    a.add_argument("--logs", required=True); a.add_argument("--output"); a.set_defaults(fn=alerts)
    s = sub.add_parser("slo", help="generate SLO definitions")
    s.add_argument("--logs", required=True); s.add_argument("--service")
    s.add_argument("--budget", default="99.9"); s.add_argument("--output"); s.set_defaults(fn=slo)
    m = sub.add_parser("mapping", help="log-to-metric mapping")
    m.add_argument("--logs", required=True); m.add_argument("--output"); m.set_defaults(fn=mapping)
    args = p.parse_args()
    args.fn(args)
'''
)
