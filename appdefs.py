"""App definitions for ai-factory. Each app is a complete project spec."""

APPS = []

def app(name, desc, features, install, usage, api_key, tech, main_code, links=None):
    APPS.append({
        "name": name, "desc": desc, "features": features, "install": install,
        "usage": usage, "api_key": api_key, "tech": tech, "main_code": main_code, "links": links or {}
    })

# ─── 1. AI Threat Intelligence Analyzer ───
app(
    "threat-intel-analyzer",
    "AI-powered threat intelligence platform that ingests CVEs, IOC feeds, and news to produce prioritized, actionable security briefings with LLM-generated context and risk scoring.",
    [
        "Ingest CVE feeds, YARA rules, and STIX/TAXII threat intelligence",
        "LLM-powered risk scoring and impact analysis per vulnerability",
        "Auto-generated security briefings with executive summaries",
        "Attack surface mapping — correlates CVEs to your tech stack",
        "Natural language queries: 'What critical RCEs affect our Python stack?'",
        "Export to PDF, JSON, or Slack-ready format",
        "Multi-source: NVD, MITRE ATT&CK, CISA KEV, custom feeds",
    ],
    "pip install -r requirements.txt\npython -m venv .venv && source .venv/bin/activate",
    "python main.py scan --stack python,nodejs --severity critical\npython main.py brief --date today --output brief.md\npython main.py query \"What RCEs affect our Flask apps?\"",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "CVE/NVD", "STIX/TAXII", "MITRE ATT&CK"],
    '''def scan(args):
    """Scan a tech stack against known CVEs using LLM risk scoring."""
    llm = LLM()
    stack = args.stack.split(",")
    print(f"Scanning stack: {stack}")
    # Load CVE data
    cves = load_cves(min_severity=args.severity)
    print(f"Loaded {len(cves)} CVEs (severity >= {args.severity})")
    # Score each CVE against the stack
    results = []
    for cve in cves:
        score = llm.classify(
            text=f"CVE: {cve['id']}\\nDescription: {cve['description']}\\nAffected: {cve['affected']}\\nStack: {stack}",
            categories=["critical", "high", "medium", "low", "not-affected"],
            instructions=f"Assess this CVE against our tech stack: {stack}. Consider exploitability, patch availability, and business impact.\\n"
        )
        results.append({"cve": cve, "assessment": score})
    # Sort by risk
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "not-affected": 4}
    results.sort(key=lambda x: sev_order.get(x["assessment"]["category"], 5))
    # Output
    top = [r for r in results if r["assessment"]["category"] in ("critical", "high")]
    print(f"\\n{'='*60}\\nTOP RISKS: {len(top)}\\n{'='*60}")
    for r in top[:10]:
        print(f"  {r['cve']['id']} [{r['assessment']['category'].upper()}] {r['cve']['description'][:80]}")
        print(f"    Why: {r['assessment']['reasoning'][:100]}")
    if args.output:
        write_brief(results, args.output)
    return results

def query(args):
    """Natural language query against threat intel."""
    llm = LLM()
    cves = load_cves()
    context = json.dumps([{"id": c["id"], "desc": c["description"][:100]} for c in cves[:50]], indent=2)
    answer = llm.generate(
        f"Threat database (top 50 by severity):\\n{context}\\n\\nQuestion: {args.text}\\n\\nGive specific CVE IDs, risk levels, and recommended actions.",
        system="You are a senior security analyst. Be specific, cite CVE IDs, and prioritize by exploitability."
    )
    print(f"\\n{'='*60}\\nANSWER\\n{'='*60}\\n{answer}")

def brief(args):
    """Generate a security briefing."""
    llm = LLM()
    cves = load_cves(min_severity="high")
    summary = llm.generate(
        f"Generate an executive security briefing for {args.date}.\\nTop CVEs: {json.dumps(cves[:20], indent=2)}\\n\\nFormat: 1) Executive Summary 2) Top 5 Threats 3) Recommended Actions 4) Watch List",
        system="You are a CISO writing a briefing for the board. Concise, actionable, no fluff."
    )
    print(summary)
    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Security Briefing — {args.date}\\n\\n{summary}\\n")
        print(f"\\nWritten to {args.output}")

def load_cves(min_severity="medium"):
    """Load CVEs from local cache or NVD API."""
    cache = os.path.join(os.path.dirname(__file__), "cve_cache.json")
    if os.path.exists(cache):
        with open(cache) as f:
            cves = json.load(f)
    else:
        cves = fetch_nvd(min_severity)
    sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    min_rank = sev_rank.get(min_severity, 2)
    return [c for c in cves if sev_rank.get(c.get("severity", "low"), 1) >= min_rank]

def fetch_nvd(min_severity="medium"):
    """Fetch from NVD API."""
    import requests
    r = requests.get("https://services.nvd.nist.gov/rest/json/cves/2.0", params={"keywordSearch": "RCE", "resultsPerPage": 50}, timeout=30)
    r.raise_for_status()
    data = r.json()
    cves = []
    for item in data.get("vulnerabilities", []):
        c = item["cve"]
        score = 0
        for m in c.get("metrics", {}).get("cvssMetricV31", []):
            score = max(score, m["cvssData"]["baseScore"])
        desc = c.get("descriptions", [{}])[0].get("value", "")
        cves.append({"id": c["id"], "description": desc, "severity": "critical" if score >= 9 else "high" if score >= 7 else "medium" if score >= 4 else "low", "affected": "", "score": score})
    with open(os.path.join(os.path.dirname(__file__), "cve_cache.json"), "w") as f:
        json.dump(cves, f)
    return cves

def write_brief(results, path):
    lines = [f"# Security Scan Results\\n", f"Generated: {datetime.datetime.now().isoformat()}\\n", f"Total CVEs assessed: {len(results)}\\n"]
    for r in results[:20]:
        lines.append(f"## {r['cve']['id']} [{r['assessment']['category'].upper()}]")
        lines.append(f"Score: {r['assessment']['confidence']}")
        lines.append(f"Reasoning: {r['assessment']['reasoning']}")
        lines.append("")
    with open(path, "w") as f:
        f.write("\\n".join(lines))
'''
)

# ─── 2. AI Log Anomaly Detector ───
app(
    "log-anomaly-detector",
    "AI-powered log analysis that uses LLMs to detect anomalies, correlate events across services, and generate incident summaries from raw application and system logs.",
    [
        "Real-time log streaming with LLM-powered anomaly detection",
        "Cross-service event correlation and timeline reconstruction",
        "Automatic incident severity classification (P1-P4)",
        "Root cause hypothesis generation from correlated events",
        "Supports: JSON logs, syslog, nginx, Docker, Kubernetes, custom formats",
        "Alert rules with LLM-generated context and recommended actions",
        "Historical pattern learning — 'this is normal for Tuesday 3am'",
    ],
    "pip install -r requirements.txt",
    "python main.py tail -f /var/log/app.log --anomaly-threshold 0.8\npython main.py analyze --file logs.json --correlate\npython main.py incident --time \"2026-04-09T14:00\" --window 5m",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "ELK/Splunk patterns", "Kubernetes", "Syslog"],
    '''def tail(args):
    """Stream logs and detect anomalies in real-time."""
    llm = LLM()
    print(f"Tailing {args.file}... (threshold: {args.anomaly_threshold})")
    print(f"{'-'*60}")
    patterns = []
    with open(args.file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            verdict = llm.classify(
                text=f"Log line: {line}\\nRecent context: {json.dumps(patterns[-5:], indent=0)}",
                categories=["normal", "warning", "anomaly", "critical"],
                instructions="Classify this log line. Consider: error codes, unusual timestamps, rate patterns, unexpected sequences. Be conservative — flag only genuine anomalies."
            )
            if verdict["category"] in ("anomaly", "critical"):
                ts = line[:20] if len(line) > 20 else ""
                print(f"\\n{'!':*60}")
                print(f"ANOMALY [{verdict['category'].upper()}] conf={verdict['confidence']}")
                print(f"  {line[:120]}")
                print(f"  Why: {verdict['reasoning'][:150]}")
                print(f"{'!'*60}")
            patterns.append(line[:200])
            if len(patterns) > 100:
                patterns.pop(0)

def analyze(args):
    """Analyze a log file for anomalies and correlations."""
    llm = LLM()
    logs = load_logs(args.file)
    print(f"Loaded {len(logs)} log entries")
    # Chunk and analyze
    anomalies = []
    chunk_size = 20
    for i in range(0, len(logs), chunk_size):
        chunk = logs[i:i+chunk_size]
        verdict = llm.classify(
            text=f"Log sequence:\\n{json.dumps(chunk, indent=2)}",
            categories=["normal", "degraded", "anomaly", "incident"],
            instructions="Analyze this sequence of log entries. Look for: error bursts, timeout cascades, resource exhaustion patterns, unusual request patterns, security events."
        )
        if verdict["category"] != "normal":
            anomalies.append({"range": f"{i}-{i+len(chunk)}", "assessment": verdict, "logs": chunk})
    # Correlate
    if args.correlate and len(anomalies) > 1:
        timeline = llm.generate(
            f"Here are correlated anomalies from the same log file:\\n{json.dumps(anomalies, indent=2)}\\n\\nReconstruct the incident timeline. What happened, in what order, and what's the likely root cause?",
            system="You are an SRE reconstructing an incident timeline. Be precise with timestamps and causal links."
        )
        print(f"\\n{'='*60}\\nINCIDENT TIMELINE\\n{'='*60}\\n{timeline}")
    print(f"\\nAnomalies detected: {len(anomalies)}")

def incident(args):
    """Generate an incident report for a specific time window."""
    llm = LLM()
    print(f"Generating incident report for {args.time} (window: {args.window})")
    # Load logs around the time
    logs = load_logs("incident_logs.json")
    summary = llm.generate(
        f"Incident window: {args.time} (+/- {args.window})\\n\\nLogs:\\n{json.dumps(logs[:100], indent=2)}\\n\\nGenerate: 1) Impact Assessment 2) Timeline 3) Root Cause Hypothesis 4) Remediation Steps 5) Communication Draft (for stakeholders)",
        system="You are an incident commander. Write a post-incident review that's actionable and honest."
    )
    print(summary)

def load_logs(path):
    try:
        with open(path) as f:
            content = f.read().strip()
        # Try JSON lines
        try:
            return [json.loads(line) for line in content.split("\\n") if line.strip()]
        except json.JSONDecodeError:
            return [line for line in content.split("\\n") if line.strip()]
    except FileNotFoundError:
        # Generate sample logs for demo
        return generate_sample_logs()

def generate_sample_logs():
    import random
    logs = []
    services = ["api-gateway", "auth-service", "payment-service", "db-proxy", "cache-layer"]
    for i in range(50):
        svc = random.choice(services)
        level = random.choices(["INFO", "WARN", "ERROR", "CRITICAL"], weights=[70, 15, 10, 5])[0]
        msg = random.choice([
            "Request completed", "Connection pool exhausted", "Timeout after 30s",
            "Authentication failed for user", "Cache miss", "Slow query: 2.3s",
            "Memory usage at 92%", "Circuit breaker OPEN", "Retry attempt 3/5"
        ])
        logs.append({"ts": f"2026-04-09T14:{i//60:02d}:{i%60:02d}", "service": svc, "level": level, "msg": msg})
    return logs
'''
)
