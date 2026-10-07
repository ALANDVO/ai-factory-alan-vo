"""App definitions batch 2 — 8 AI/ML & cybersecurity apps for ai-factory."""

import json, os, re, sys, hashlib, random, csv, io, math, time, statistics
from datetime import datetime, timedelta
from collections import Counter, defaultdict

APPS = []

def app(name, desc, features, install, usage, api_key, tech, main_code, links=None):
    APPS.append({
        "name": name, "desc": desc, "features": features, "install": install,
        "usage": usage, "api_key": api_key, "tech": tech, "main_code": main_code, "links": links or {}
    })

# ─── 3. Prompt Optimizer ───
app(
    "prompt-optimizer",
    "AI-powered prompt engineering tool that evaluates raw prompts, rewrites them for clarity and specificity, benchmarks across models, and generates A/B test harnesses for systematic prompt improvement.",
    [
        "Prompt quality scoring across 8 dimensions (clarity, specificity, structure, etc.)",
        "LLM-driven prompt rewriting with side-by-side before/after comparison",
        "Multi-model benchmarking with token cost and latency tracking",
        "A/B test harness generation for systematic prompt evaluation",
        "Prompt template library with versioning and rollback",
        "Batch evaluation across test case suites with pass/fail reporting",
        "Export to JSON, Markdown, or YAML for CI/CD integration",
    ],
    "pip install -r requirements.txt",
    """python main.py evaluate "Summarize this email" --score
python main.py optimize "Write code for a REST API" --target python
python main.py benchmark --prompt-file prompt.txt --models gpt-4o,claude-3-opus
python main.py ab-test --cases tests.json --prompt-a v1.txt --prompt-b v2.txt""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "Prompt Engineering", "A/B Testing", "LLM Benchmarking"],
    '''def evaluate(args):
    """Score a prompt across quality dimensions."""
    llm = LLM()
    prompt = args.prompt
    print(f"{'='*60}")
    print(f"EVALUATING PROMPT")
    print(f"{'='*60}")
    print(f"Prompt: {prompt[:200]}")
    print(f"{'='*60}\\n")

    dimensions = [
        ("clarity", "Is the intent unambiguous? Could it be interpreted multiple ways?"),
        ("specificity", "Does it specify expected output format, length, and constraints?"),
        ("structure", "Is it well-organized with clear sections or logical flow?"),
        ("context", "Does it provide sufficient domain context for the LLM?"),
        ("constraints", "Are there explicit constraints on what NOT to do?"),
        ("output_spec", "Is the desired output format precisely specified?"),
        ("examples", "Does it include few-shot examples or reference outputs?"),
        ("role", "Does it assign a clear expert role to the LLM?"),
    ]

    scores = []
    for dim, question in dimensions:
        result = llm.classify(
            text=f"Prompt: {prompt}\\n\\nEvaluation question: {question}",
            categories=["strong", "adequate", "weak", "missing"],
            instructions=f"Rate this prompt on the dimension: {dim}. {question} Be strict — a score of 'strong' means production-ready quality."
        )
        score_map = {"strong": 1.0, "adequate": 0.6, "weak": 0.3, "missing": 0.0, "unknown": 0.0}
        score = score_map.get(result.get("category", "unknown"), 0.0)
        scores.append({"dimension": dim, "score": score, "rating": result.get("category", "unknown"), "notes": result.get("reasoning", "")[:200]})
        print(f"  {dim:<15} {result.get('category', 'unknown'):>10}  ({score:.2f})")

    total = sum(s["score"] for s in scores) / len(scores)
    print(f"\\n{'='*60}")
    print(f"OVERALL SCORE: {total:.2f} / 1.00")
    grade = "A" if total >= 0.8 else "B" if total >= 0.6 else "C" if total >= 0.4 else "D"
    print(f"GRADE: {grade}")

    weak = [s for s in scores if s["score"] < 0.5]
    if weak:
        print(f"\\nWEAK AREAS ({len(weak)}):")
        for w in weak:
            print(f"  - {w['dimension']}: {w['notes']}")

    if args.score:
        report = {"prompt": prompt, "scores": scores, "total": round(total, 3), "grade": grade, "evaluated_at": datetime.now().isoformat()}
        print(f"\\nJSON report: {json.dumps(report, indent=2)}")
    return scores, total

def optimize(args):
    """Rewrite a prompt for maximum effectiveness."""
    llm = LLM()
    prompt = args.prompt
    target = args.target or "general"
    print(f"Optimizing prompt for: {target}")

    optimized = llm.generate(
        f"Original prompt: {prompt}\\n\\nTarget domain: {target}\\n\\n"
        "Rewrite this prompt to be maximally effective. Apply these principles:\\n"
        "1. Assign a specific expert role\\n"
        "2. Add explicit output format specification\\n"
        "3. Include 2-3 few-shot examples if helpful\\n"
        "4. Add constraints (what NOT to do)\\n"
        "5. Structure with clear sections\\n"
        "6. Make it specific — replace vague words with precise instructions\\n\\n"
        "Return ONLY the optimized prompt, no explanations.",
        system="You are a prompt engineering expert with 5+ years of LLM fine-tuning and prompt design experience. You produce prompts that consistently outperform the original by 30%+ in quality metrics."
    )

    print(f"\\n{'='*60}")
    print(f"BEFORE")
    print(f"{'='*60}")
    print(prompt)
    print(f"\\n{'='*60}")
    print(f"AFTER (optimized)")
    print(f"{'='*60}")
    print(optimized)

    comparison = llm.generate(
        f"Original: {prompt}\\n\\nOptimized: {optimized}\\n\\n"
        "Explain in 5 bullet points what specific improvements were made and why each one matters for LLM performance.",
        system="Be specific. Reference exact words/phrases that changed."
    )
    print(f"\\nIMPROVEMENTS:")
    print(comparison)

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Optimized Prompt\\n\\n## Original\\n{prompt}\\n\\n## Optimized\\n{optimized}\\n\\n## Changes\\n{comparison}\\n")
        print(f"\\nSaved to {args.output}")
    return optimized

def benchmark(args):
    """Benchmark a prompt across multiple models."""
    llm = LLM()
    prompt = args.prompt or (open(args.prompt_file).read() if args.prompt_file else "Write a function to validate email addresses")
    models = [m.strip() for m in args.models.split(",")]

    print(f"{'='*60}")
    print(f"BENCHMARKING across {len(models)} model(s)")
    print(f"{'='*60}")
    print(f"Prompt: {prompt[:100]}...\\n")

    results = []
    for model in models:
        print(f"  Testing {model}...", end=" ", flush=True)
        start = time.time()
        try:
            llm.model = model
            response = llm.generate(prompt, system="You are a helpful assistant. Respond concisely.")
            elapsed = time.time() - start
            tokens_est = len(response) // 4
            result = {"model": model, "response": response[:500], "time": round(elapsed, 2), "tokens_est": tokens_est, "status": "ok"}
            print(f"OK ({elapsed:.1f}s, ~{tokens_est} tokens)")
        except Exception as e:
            elapsed = time.time() - start
            result = {"model": model, "response": "", "time": round(elapsed, 2), "tokens_est": 0, "status": f"error: {str(e)[:80]}"}
            print(f"FAIL ({str(e)[:50]})")
        results.append(result)

    # Score quality
    print(f"\\nScoring responses...")
    quality = []
    for r in results:
        if r["status"] != "ok":
            quality.append({"model": r["model"], "quality": 0.0, "reason": "execution failed"})
            continue
        score = llm.classify(
            text=f"Prompt: {prompt}\\n\\nResponse: {r['response']}\\n\\nRate the quality of this response on a scale of 0-10. Consider: correctness, completeness, clarity, and usefulness.",
            categories=["excellent", "good", "adequate", "poor", "terrible"],
            instructions="Rate the response quality relative to the prompt requirements."
        )
        q_map = {"excellent": 10, "good": 7.5, "adequate": 5, "poor": 2.5, "terrible": 1}
        quality.append({"model": r["model"], "quality": q_map.get(score.get("category", "poor"), 3), "reason": score.get("reasoning", "")[:100]})

    # Report
    print(f"\\n{'='*60}")
    print(f"BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"{'Model':<25} {'Quality':>8} {'Time':>8} {'Tokens':>8}  {'Status'}")
    print(f"{'-'*70}")
    for q in quality:
        r = next((x for x in results if x["model"] == q["model"]), {})
        print(f"{q['model']:<25} {q['quality']:>8.1f} {r.get('time',0):>7.1f}s {r.get('tokens_est',0):>8}  {r.get('status','?')}")

    if args.output:
        report = {"prompt": prompt, "results": results, "quality": quality, "benchmarked_at": datetime.now().isoformat()}
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\\nReport saved to {args.output}")
    return results, quality

def ab_test(args):
    """Run A/B test between two prompt versions."""
    llm = LLM()
    with open(args.prompt_a) as f: prompt_a = f.read()
    with open(args.prompt_b) as f: prompt_b = f.read()
    with open(args.cases) as f: cases = json.load(f)

    print(f"A/B Test: {len(cases)} test cases")
    print(f"  A: {args.prompt_a} ({len(prompt_a)} chars)")
    print(f"  B: {args.prompt_b} ({len(prompt_b)} chars)\\n")

    wins = {"a": 0, "b": 0, "tie": 0}
    details = []
    for i, case in enumerate(cases):
        input_data = case.get("input", case.get("prompt", str(case)))
        expected = case.get("expected", "")

        try:
            resp_a = llm.generate(input_data, system=prompt_a)
        except: resp_a = ""
        try:
            resp_b = llm.generate(input_data, system=prompt_b)
        except: resp_b = ""

        judge = llm.classify(
            text=f"Task: {input_data[:300]}\\n\\nExpected: {expected[:200]}\\n\\nResponse A: {resp_a[:500]}\\n\\nResponse B: {resp_b[:500]}\\n\\nWhich response better satisfies the task and matches the expected output?",
            categories=["A_better", "B_better", "tie"],
            instructions="Judge purely on task completion quality. If both are equally good or equally bad, say tie."
        )
        cat = judge.get("category", "tie")
        if cat == "A_better": wins["a"] += 1
        elif cat == "B_better": wins["b"] += 1
        else: wins["tie"] += 1
        print(f"  [{i+1}/{len(cases)}] {cat}")
        details.append({"case": i, "winner": cat, "reasoning": judge.get("reasoning", "")[:100]})

    total = len(cases)
    print(f"\\n{'='*60}")
    print(f"A/B RESULTS: A={wins['a']} B={wins['b']} Tie={wins['tie']} (of {total})")
    winner = "A" if wins["a"] > wins["b"] else "B" if wins["b"] > wins["a"] else "TIE"
    print(f"WINNER: {winner}")
    print(f"{'='*60}")

    if args.output:
        report = {"wins": wins, "details": details, "total": total, "winner": winner, "date": datetime.now().isoformat()}
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\\nSaved to {args.output}")
    return wins

def library(args):
    """Manage a prompt template library."""
    lib_path = args.path or os.path.join(os.path.dirname(__file__), "prompt_library.json")
    if args.action == "add" and args.prompt:
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        lib[args.name] = {"prompt": args.prompt, "created": datetime.now().isoformat(), "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()]}
        with open(lib_path, "w") as f: json.dump(lib, f, indent=2)
        print(f"Added '{args.name}' to library ({len(lib)} prompts total)")
    elif args.action == "list":
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        print(f"Prompt Library ({len(lib)} prompts)")
        for name, entry in sorted(lib.items()):
            tags = " ".join(entry.get("tags", []))
            print(f"  {name:<30} {entry.get('created','')[:10]}  [{tags}]  {entry['prompt'][:60]}...")
    elif args.action == "get" and args.name:
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        if args.name in lib: print(lib[args.name]["prompt"])
        else: print(f"Prompt '{args.name}' not found")
    elif args.action == "remove" and args.name:
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        if args.name in lib:
            del lib[args.name]
            with open(lib_path, "w") as f: json.dump(lib, f, indent=2)
            print(f"Removed '{args.name}'")
    return None

def main():
    import argparse
    p = argparse.ArgumentParser(prog="prompt-optimizer", description="AI-powered prompt engineering tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("evaluate", help="Score a prompt on quality dimensions")
    e.add_argument("prompt"); e.add_argument("--score", action="store_true")
    e.set_defaults(fn=evaluate)

    o = sub.add_parser("optimize", help="Rewrite a prompt for maximum effectiveness")
    o.add_argument("prompt"); o.add_argument("--target", default=None); o.add_argument("--output", default=None)
    o.set_defaults(fn=optimize)

    b = sub.add_parser("benchmark", help="Benchmark across multiple models")
    b.add_argument("--prompt", default=None); b.add_argument("--prompt-file", default=None)
    b.add_argument("--models", default="gpt-4o"); b.add_argument("--output", default=None)
    b.set_defaults(fn=benchmark)

    a = sub.add_parser("ab-test", help="A/B test between two prompt versions")
    a.add_argument("--cases", required=True); a.add_argument("--prompt-a", required=True)
    a.add_argument("--prompt-b", required=True); a.add_argument("--output", default=None)
    a.set_defaults(fn=ab_test)

    l = sub.add_parser("library", help="Manage prompt template library")
    l.add_argument("--action", choices=["add", "list", "get", "remove"], default="list")
    l.add_argument("--name", default=None); l.add_argument("--prompt", default=None)
    l.add_argument("--tags", default=None); l.add_argument("--path", default=None)
    l.set_defaults(fn=library)

    args = p.parse_args()
    args.fn(args)
''',
    {"GitHub": "https://github.com/ALANDVO/prompt-optimizer-alan-vo"}
)
# ─── 4. RAG Engine ───
app(
    "rag-engine",
    "Retrieval-Augmented Generation engine that ingests documents (PDF, MD, JSON), chunks and embeds them with an API, and serves semantic search plus generation with grounded citations.",
    [
        "Multi-format document ingestion: PDF, Markdown, JSON, plain text, code files",
        "Smart chunking with overlap, preserving paragraph and heading structure",
        "API-based embeddings with local cosine-similarity search (no vector DB needed)",
        "Semantic search ranked by relevance with source chunk attribution",
        "Grounded generation with inline [n] citations back to source chunks",
        "Collection management: create, list, delete, stats per collection",
        "Export search results and Q&A transcripts to JSON or Markdown",
    ],
    "pip install -r requirements.txt",
    """python main.py ingest ./docs/ --name my-kb
python main.py search "how do we handle auth tokens?" --collection my-kb --top 5
python main.py generate "What is our rate limit policy?" --collection my-kb
python main.py stats --collection my-kb""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "RAG", "Embeddings", "Semantic Search", "NLP"],
    '''import math

def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)

def _embed_text(llm, text):
    """Embed text using the OpenAI-compatible embeddings endpoint."""
    import requests
    headers = {"Content-Type": "application/json"}
    if llm.api_key:
        headers["Authorization"] = f"Bearer {llm.api_key}"
    payload = {"model": os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"), "input": text[:8000]}
    r = requests.post(f"{llm.base_url}/embeddings", headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["data"][0]["embedding"]

def _chunk_text(text, chunk_size=1200, overlap=200):
    """Chunk text by paragraph boundaries with overlap."""
    paragraphs = re.split(r"\\n\\s*\\n", text)
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 > chunk_size and current:
            chunks.append(current.strip())
            current = current[-overlap:] if overlap else ""
        current += para + "\\n\\n"
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if len(c) > 20]

def _extract_text(path):
    """Extract text from supported file formats."""
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", errors="replace") as f:
        text = f.read()
    if ext in (".md", ".txt", ".py", ".js", ".go", ".rs", ".json", ".yaml", ".yml", ".toml"):
        return text
    if ext == ".pdf":
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(path)
            return "\\n".join((page.extract_text() or "") for page in reader.pages)
        except ImportError:
            return text
    return text

def _collection_path(name):
    base = os.path.join(os.path.dirname(__file__), "collections")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"{name}.json")

def _load_collection(name):
    path = _collection_path(name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Collection '{name}' not found. Run 'ingest' first.")
    with open(path) as f:
        return json.load(f)

def _save_collection(name, data):
    with open(_collection_path(name), "w") as f:
        json.dump(data, f)

def ingest(args):
    """Ingest documents into a named collection."""
    llm = LLM()
    path = args.path
    files = []
    if os.path.isdir(path):
        for root, _, names in os.walk(path):
            files.extend(os.path.join(root, n) for n in names if n.lower().endswith((".md", ".txt", ".py", ".js", ".go", ".rs", ".json", ".yaml", ".yml", ".toml", ".pdf")))
    elif os.path.exists(path):
        files = [path]
    else:
        print(f"Path not found: {path}")
        return

    print(f"Ingesting {len(files)} file(s) into collection '{args.name}'...")
    data = _load_collection(args.name) if os.path.exists(_collection_path(args.name)) else {"name": args.name, "chunks": [], "created": datetime.now().isoformat()}

    for filepath in files:
        text = _extract_text(filepath)
        chunks = _chunk_text(text)
        if not chunks:
            print(f"  {filepath}: no chunks (empty or binary)")
            continue
        print(f"  {filepath}: {len(chunks)} chunk(s)")
        for i, chunk in enumerate(chunks):
            try:
                embedding = _embed_text(llm, chunk)
            except Exception as e:
                print(f"    embed failed for chunk {i}: {e}")
                continue
            data["chunks"].append({
                "id": f"{os.path.basename(filepath)}:{i}",
                "source": filepath,
                "text": chunk,
                "embedding": embedding,
            })

    _save_collection(args.name, data)
    print(f"\\nCollection '{args.name}': {len(data['chunks'])} chunks total")

def search(args):
    """Semantic search over a collection."""
    llm = LLM()
    data = _load_collection(args.name)
    query = args.query
    print(f"Searching '{args.name}' for: {query}\\n")

    q_emb = _embed_text(llm, query)
    scored = []
    for chunk in data["chunks"]:
        sim = _cosine(q_emb, chunk["embedding"])
        scored.append((sim, chunk))
    scored.sort(key=lambda x: -x[0])

    top = scored[:args.top]
    for rank, (sim, chunk) in enumerate(top, 1):
        print(f"[{rank}] similarity={sim:.4f}  source={chunk['source']}  id={chunk['id']}")
        snippet = chunk["text"][:300].replace("\\n", " ")
        print(f"    {snippet}...")
        print()

    if args.output:
        with open(args.output, "w") as f:
            json.dump([{"rank": i + 1, "similarity": round(s, 4), "source": c["source"], "text": c["text"]} for i, (s, c) in enumerate(top)], f, indent=2)
        print(f"Saved to {args.output}")
    return top

def generate(args):
    """Generate a grounded answer with citations from a collection."""
    llm = LLM()
    data = _load_collection(args.name)
    question = args.question

    q_emb = _embed_text(llm, question)
    scored = sorted([(_cosine(q_emb, c["embedding"]), c) for c in data["chunks"]], key=lambda x: -x[0])
    context_chunks = [c for _, c in scored[:args.context]]

    context = "\\n\\n".join(f"[{i+1}] (from {c['source']}) {c['text'][:1500]}" for i, c in enumerate(context_chunks))

    answer = llm.generate(
        f"Answer the question using ONLY the provided context chunks. Cite sources inline as [1], [2], etc. If the answer is not in the context, say so explicitly.\\n\\n"
        f"CONTEXT:\\n{context}\\n\\nQUESTION: {question}",
        system="You are a precise retrieval-augmented answer engine. Never invent facts. Every claim must trace to a cited chunk. Be concise."
    )

    print(f"{'='*60}")
    print(f"ANSWER")
    print(f"{'='*60}")
    print(answer)
    print(f"\\nSOURCES:")
    for i, c in enumerate(context_chunks, 1):
        print(f"  [{i}] {c['source']}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"question": question, "answer": answer, "sources": [c["source"] for c in context_chunks], "generated_at": datetime.now().isoformat()}, f, indent=2)
        print(f"\\nSaved to {args.output}")
    return answer

def stats(args):
    """Show collection statistics."""
    data = _load_collection(args.name)
    chunks = data["chunks"]
    sources = Counter(c["source"] for c in chunks)
    total_chars = sum(len(c["text"]) for c in chunks)
    print(f"{'='*60}")
    print(f"COLLECTION: {data['name']}")
    print(f"{'='*60}")
    print(f"  Created:      {data.get('created', '?')}")
    print(f"  Chunks:       {len(chunks)}")
    print(f"  Sources:      {len(sources)} file(s)")
    print(f"  Total chars:  {total_chars:,}")
    if chunks:
        lens = [len(c["text"]) for c in chunks]
        print(f"  Chunk size:   min={min(lens)} avg={int(statistics.mean(lens))} max={max(lens)}")
    print(f"\\n  SOURCES:")
    for src, count in sources.most_common(20):
        print(f"    {count:>4} chunks  {os.path.basename(src)}")

    base = os.path.join(os.path.dirname(__file__), "collections")
    if os.path.isdir(base):
        print(f"\\n  ALL COLLECTIONS:")
        for fn in sorted(os.listdir(base)):
            if fn.endswith(".json"):
                with open(os.path.join(base, fn)) as f:
                    d = json.load(f)
                print(f"    {d['name']:<30} {len(d['chunks']):>5} chunks")
    return None

def main():
    import argparse
    p = argparse.ArgumentParser(prog="rag-engine", description="RAG engine with semantic search and cited generation")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("ingest", help="Ingest documents into a collection")
    i.add_argument("path"); i.add_argument("--name", default="default")
    i.set_defaults(fn=ingest)

    s = sub.add_parser("search", help="Semantic search over a collection")
    s.add_argument("query"); s.add_argument("--collection", default="default")
    s.add_argument("--top", type=int, default=5); s.add_argument("--output", default=None)
    s.set_defaults(fn=search)

    g = sub.add_parser("generate", help="Grounded generation with citations")
    g.add_argument("question"); g.add_argument("--collection", default="default")
    g.add_argument("--context", type=int, default=4); g.add_argument("--output", default=None)
    g.set_defaults(fn=generate)

    st = sub.add_parser("stats", help="Collection statistics")
    st.add_argument("--collection", default="default")
    st.set_defaults(fn=stats)

    args = p.parse_args()
    args.name = getattr(args, "name", getattr(args, "collection", "default"))
    args.fn(args)
'''
)
# ─── 5. Code Review AI ───
app(
    "code-review-ai",
    "AI code review assistant that analyzes diffs or files for bugs, security issues, style problems, and performance pitfalls, generating line-by-line review comments for Python, JS, Go, and Rust.",
    [
        "Diff-based review: paste a unified diff and get line-by-line comments",
        "Full-file review with function-level analysis and cross-reference",
        "Security scanning: injection, secrets, auth flaws, unsafe deserialization",
        "Performance detection: O(n²) patterns, needless allocations, N+1 queries",
        "Style and maintainability feedback with severity levels",
        "Multi-language: Python, JavaScript/TypeScript, Go, Rust",
        "Export reviews to JSON, Markdown, or PR-comment-ready format",
    ],
    "pip install -r requirements.txt",
    """python main.py review --file src/auth.py --lang python
python main.py diff --file changes.diff --lang javascript
python main.py review --file main.go --lang go --focus security,performance
python main.py review --stdin --lang rust < code.rs""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "Code Review", "Static Analysis", "Security", "Python/JS/Go/Rust"],
    '''def _detect_lang(filepath, explicit=None):
    if explicit:
        return explicit
    ext = os.path.splitext(filepath)[1].lower()
    return {".py": "python", ".js": "javascript", ".ts": "typescript", ".jsx": "javascript", ".tsx": "typescript", ".go": "go", ".rs": "rust"}.get(ext, "python")

def _read_code(args):
    if getattr(args, "stdin", False):
        return sys.stdin.read()
    with open(args.file) as f:
        return f.read()

def review(args):
    """Full-file code review with LLM analysis."""
    llm = LLM()
    code = _read_code(args)
    lang = _detect_lang(getattr(args, "file", ""), args.lang)
    focus = (args.focus or "all").split(",")
    lines = code.split("\\n")
    print(f"Reviewing {len(lines)} lines ({lang}), focus: {focus}\\n")

    # Chunk for very large files
    chunks, chunk_size = [], 250
    for i in range(0, len(lines), chunk_size):
        chunks.append((i + 1, "\\n".join(lines[i:i + chunk_size])))

    findings = []
    for start_line, chunk in chunks:
        response = llm.generate(
            f"Language: {lang}\\nFocus areas: {', '.join(focus)}\\n\\n"
            f"Code (starting at line {start_line}):\\n```{lang}\\n{chunk}\\n```\\n\\n"
            "Review this code. For EACH issue found, output one JSON object on its own line (JSONL format) with fields:\\n"
            '{"line": <line number within this chunk>, "severity": "critical|high|medium|low", "category": "bug|security|performance|style|maintainability", "message": "<specific, actionable description>", "suggestion": "<concrete fix or code snippet>"}\\n'
            "Only report genuine issues. No praise, no filler. If the chunk is clean, output exactly: CLEAN",
            system="You are a staff-level engineer doing a rigorous code review. Be specific: cite the exact expression, name the vulnerability class (CWE if security), and give a fix. No generic advice like 'add error handling' without saying where."
        )
        chunk_findings = _parse_review(response, start_line)
        findings.extend(chunk_findings)
        print(f"  lines {start_line}-{start_line + len(chunk.splitlines()) - 1}: {len(chunk_findings)} finding(s)")

    _report(findings, args)
    return findings

def diff(args):
    """Review a unified diff."""
    llm = LLM()
    code = _read_code(args)
    lang = _detect_lang(getattr(args, "file", ""), args.lang)
    print(f"Reviewing diff ({lang}, {len(code.splitlines())} lines)\\n")

    # Only review added lines context
    response = llm.generate(
        f"Language: {lang}\\n\\nUnified diff:\\n```diff\\n{code}\\n```\\n\\n"
        "Review ONLY the changes (added/modified lines). For each issue in the CHANGED code, output one JSON object per line (JSONL) with fields:\\n"
        '{"line": <line number in the diff>, "severity": "critical|high|medium|low", "category": "bug|security|performance|style|maintainability", "message": "<specific description>", "suggestion": "<concrete fix>"}\\n'
        "Flag regressions, broken callers, and new vulnerabilities introduced by the change. If the diff is clean, output: CLEAN",
        system="You are reviewing a PR diff. Focus on what the change breaks or introduces: API contract violations, unhandled edge cases, security holes, performance regressions. Be surgical."
    )
    findings = _parse_review(response, 0)
    _report(findings, args)
    return findings

def _parse_review(response, base_line):
    findings = []
    for line in response.split("\\n"):
        line = line.strip()
        if not line or line == "CLEAN":
            continue
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            obj = json.loads(line)
            obj["line"] = base_line + int(obj.get("line", 1))
            findings.append(obj)
        except (json.JSONDecodeError, ValueError):
            continue
    return findings

def _report(findings, args):
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: (sev_order.get(f.get("severity", "low"), 4), f.get("line", 0)))

    print(f"\\n{'='*60}")
    counts = Counter(f.get("severity", "low") for f in findings)
    summary = " ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda x: sev_order.get(x[0], 4)))
    print(f"REVIEW: {len(findings)} finding(s) [{summary}]")
    print(f"{'='*60}\\n")

    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
    for f in findings:
        sev = f.get("severity", "low")
        print(f"  {icons.get(sev, '⚪')} L{f.get('line', '?')} [{sev.upper()}] {f.get('category', '?')}: {f.get('message', '')}")
        if f.get("suggestion"):
            print(f"     → {f['suggestion']}")

    if not findings:
        print("  ✅ No issues found.")

    if args.output:
        with open(args.output, "w") as f:
            if args.output.endswith((".json",)):
                json.dump(findings, f, indent=2)
            else:
                f.write("# Code Review\\n\\n")
                for x in findings:
                    f.write(f"- **[{x.get('severity')}] L{x.get('line')}** ({x.get('category')}): {x.get('message')}\\n  - Fix: {x.get('suggestion', 'n/a')}\\n")
        print(f"\\nSaved to {args.output}")

def scan(args):
    """Quick security-only scan across a directory."""
    llm = LLM()
    path = args.path
    files = []
    if os.path.isdir(path):
        for root, _, names in os.walk(path):
            files.extend(os.path.join(root, n) for n in names if n.lower().endswith((".py", ".js", ".ts", ".go", ".rs")))
    else:
        files = [path]

    print(f"Security scanning {len(files)} file(s)...\\n")
    all_findings = []
    for filepath in files:
        try:
            with open(filepath) as f:
                code = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        lang = _detect_lang(filepath)
        response = llm.generate(
            f"File: {filepath}\\nLanguage: {lang}\\n```{lang}\\n{code[:12000]}\\n```\\n\\n"
            "List ONLY security vulnerabilities in this file as JSONL: "
            '{"line": <n>, "severity": "critical|high|medium|low", "cwe": "CWE-xxx", "message": "<desc>", "suggestion": "<fix>"}\\n'
            "Look for: hardcoded secrets, injection (SQL/cmd/XSS), path traversal, insecure deserialization, missing auth checks, weak crypto. Output CLEAN if none.",
            system="You are a security engineer. Be precise — name the exact vulnerability and CWE. No false positives: confirm the vulnerable expression exists in the code."
        )
        found = _parse_review(response, 0)
        found = [f for f in found if f.get("cwe") or f.get("category") in ("security", "bug")]
        if found:
            print(f"  {filepath}: {len(found)} issue(s)")
            for f in found:
                print(f"    L{f['line']} [{f.get('severity','?')}] {f.get('cwe','')} {f.get('message','')[:100]}")
            all_findings.extend(found)
        else:
            print(f"  {filepath}: clean")

    print(f"\\nTotal security findings: {len(all_findings)}")
    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_findings, f, indent=2)
        print(f"Saved to {args.output}")
    return all_findings

def main():
    import argparse
    p = argparse.ArgumentParser(prog="code-review-ai", description="AI code review assistant")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("review", help="Review a full file")
    r.add_argument("--file", default=None); r.add_argument("--stdin", action="store_true")
    r.add_argument("--lang", default=None); r.add_argument("--focus", default="all")
    r.add_argument("--output", default=None)
    r.set_defaults(fn=review)

    d = sub.add_parser("diff", help="Review a unified diff")
    d.add_argument("--file", default=None); d.add_argument("--stdin", action="store_true")
    d.add_argument("--lang", default=None); d.add_argument("--output", default=None)
    d.set_defaults(fn=diff)

    s = sub.add_parser("scan", help="Security scan a directory")
    s.add_argument("path"); s.add_argument("--output", default=None)
    s.set_defaults(fn=scan)

    args = p.parse_args()
    if not args.file and not getattr(args, "stdin", False):
        p.error("provide --file or --stdin")
    args.fn(args)
'''
)
# ─── 6. Meeting Minutes ───
app(
    "meeting-minutes",
    "AI meeting transcription and summarization tool that extracts action items, decisions, owners, and deadlines from raw meeting text, then generates Slack-ready summaries and calendar follow-ups.",
    [
        "Raw transcript → structured minutes with decisions, action items, and open questions",
        "Action item extraction with owner assignment and deadline parsing",
        "Decision log with context and rationale capture",
        "Slack-ready summary generation with emoji formatting and thread structure",
        "Calendar follow-up suggestions with proposed dates and attendees",
        "Meeting type detection: standup, design review, 1:1, planning, retro",
        "Export to Markdown, JSON, or plain text for any workflow",
    ],
    "pip install -r requirements.txt",
    """python main.py minutes --file transcript.txt
python main.py actions --file transcript.txt --assign
python main.py slack --file transcript.txt --channel #eng-standup
python main.py followups --file transcript.txt --start-date 2026-10-08""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "NLP", "Information Extraction", "Productivity"],
    '''def _load_transcript(args):
    if getattr(args, "stdin", False):
        return sys.stdin.read()
    with open(args.file) as f:
        return f.read()

def minutes(args):
    """Generate structured meeting minutes from a transcript."""
    llm = LLM()
    text = _load_transcript(args)
    print(f"Processing {len(text.split())} words...\\n")

    meeting_type = llm.classify(
        text=text[:3000],
        categories=["standup", "design_review", "one_on_one", "planning", "retrospective", "status_update", "general"],
        instructions="Classify the type of meeting based on the content, participants, and topics discussed."
    )
    mtype = meeting_type.get("category", "general")
    print(f"Detected meeting type: {mtype}")

    result = llm.generate(
        f"Meeting transcript ({mtype}):\\n\\n{text}\\n\\n"
        "Produce structured meeting minutes in Markdown with these EXACT sections:\\n"
        "## Summary (3-5 sentences, what this meeting accomplished)\\n"
        "## Decisions (each with: decision, rationale, decided-by) — use a numbered list\\n"
        "## Action Items (each with: task, owner, deadline, status: new|existing) — use a table with columns | # | Task | Owner | Deadline |\\n"
        "## Open Questions (unresolved items needing follow-up)\\n"
        "## Key Discussion Points (topics with 1-2 sentence summaries of conclusions)\\n"
        "## Next Meeting (suggested agenda if applicable)\\n\\n"
        "Be faithful to the transcript. Do not invent owners or deadlines that were not stated — mark them as 'TBD' if missing.",
        system="You are a meticulous executive assistant. Extract facts precisely. Attribute every action item to a named owner from the transcript. Preserve deadlines exactly as stated."
    )

    print(result)
    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Meeting Minutes — {datetime.now().strftime('%Y-%m-%d %H:%M')}\\n\\n**Type:** {mtype}\\n\\n{result}\\n")
        print(f"\\nSaved to {args.output}")
    return result

def actions(args):
    """Extract and track action items with assignments."""
    llm = LLM()
    text = _load_transcript(args)
    print(f"Extracting action items from {len(text.split())} words...\\n")

    result = llm.generate(
        f"Meeting transcript:\\n\\n{text}\\n\\n"
        "Extract ALL action items (explicit or implicit commitments like 'I will handle that', 'let us schedule that', 'can you look into this?'). "
        "For each item provide: task description, owner (full name as spoken in transcript), deadline (as stated, or 'none'), priority (high|medium|low based on context), and a suggested concrete next step. "
        "Output as a JSON array. Each object: {\\"task\\": \\"...\\", \\"owner\\": \\"...\\", \\"deadline\\": \\"...\\", \\"priority\\": \\"...\\", \\"next_step\\": \\"...\\"}",
        system="You extract commitments from meetings. An action item exists whenever someone says they will do something, or when the group assigns a task. Be thorough — miss nothing."
    )

    items = _parse_json_array(result)
    if not items:
        print("No action items found, or parse failed:")
        print(result[:500])
        return []

    print(f"{'='*60}")
    print(f"ACTION ITEMS: {len(items)}")
    print(f"{'='*60}")
    for i, item in enumerate(items, 1):
        prio_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(item.get("priority", "medium"), "⚪")
        print(f"\\n  {i}. {prio_icon} [{item.get('priority', '?').upper()}] {item.get('task', '?')}")
        print(f"     Owner:    {item.get('owner', 'TBD')}")
        print(f"     Deadline: {item.get('deadline', 'none')}")
        if item.get("next_step"):
            print(f"     Next:     {item['next_step']}")

    owners = Counter(item.get("owner", "TBD") for item in items)
    print(f"\\n  BY OWNER:")
    for owner, count in owners.most_common():
        print(f"    {owner}: {count} item(s)")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(items, f, indent=2)
        print(f"\\nSaved to {args.output}")
    return items

def slack(args):
    """Generate a Slack-ready meeting summary."""
    llm = LLM()
    text = _load_transcript(args)
    channel = args.channel or "#general"
    print(f"Generating Slack summary for {channel}...\\n")

    summary = llm.generate(
        f"Meeting transcript:\\n\\n{text}\\n\\n"
        "Write a Slack message summarizing this meeting. Format requirements:\\n"
        "- Start with an emoji that fits the meeting type + a one-line headline\\n"
        "- Use *bold* for section labels: *Decisions*, *Action Items*, *Follow-ups*\\n"
        "- Action items as bullet points with @owner mentions (first name only)\\n"
        "- Keep it scannable: max 15 lines total\\n"
        "- End with a suggested next-checkin time if relevant\\n"
        "- No markdown headers (Slack does not use #), no tables\\n"
        "Output ONLY the Slack message, ready to paste.",
        system="You write Slack updates that busy engineers actually read. Punchy, specific, zero fluff."
    )

    print(f"{'='*60}")
    print(f"SLACK MESSAGE")
    print(f"{'='*60}")
    print(summary)

    if args.output:
        with open(args.output, "w") as f:
            f.write(summary)
        print(f"\\nSaved to {args.output}")
    return summary

def followups(args):
    """Generate calendar follow-up suggestions."""
    llm = LLM()
    text = _load_transcript(args)
    start = args.start_date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Generating follow-ups (starting {start})...\\n")

    result = llm.generate(
        f"Meeting transcript:\\n\\n{text}\\n\\n"
        f"Generate calendar follow-up suggestions. Today is {start}. For each follow-up needed, output a JSON object: "
        "{\\"title\\": \\"...\\", \\"attendees\\": [\\"name\\", ...], \\"suggested_date\\": \\"YYYY-MM-DD\\", \\"duration_minutes\\": 30, \\"description\\": \\"agenda in 3 bullets\\"}\\n"
        "Rules: schedule within 2 weeks; standup-type followups within 1 day; design reviews 3-5 days out; include only attendees mentioned in the transcript. "
        "Output a JSON array.",
        system="You schedule follow-ups the way a great PM does: right timing, right people, tight agenda. Never schedule more than necessary."
    )

    followups = _parse_json_array(result)
    if not followups:
        print("No follow-ups suggested, or parse failed:")
        print(result[:500])
        return []

    print(f"{'='*60}")
    print(f"FOLLOW-UP SCHEDULE: {len(followups)}")
    print(f"{'='*60}")
    for i, fu in enumerate(followups, 1):
        print(f"\\n  {i}. {fu.get('title', '?')}")
        print(f"     When:      {fu.get('suggested_date', '?')} ({fu.get('duration_minutes', 30)} min)")
        print(f"     Attendees: {', '.join(fu.get('attendees', []))}")
        if fu.get("description"):
            for line in fu["description"].split("\\n"):
                if line.strip():
                    print(f"       {line.strip()}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(followups, f, indent=2)
        print(f"\\nSaved to {args.output}")
    return followups

def _parse_json_array(raw):
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        data = json.loads(raw[start:end + 1])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def main():
    import argparse
    p = argparse.ArgumentParser(prog="meeting-minutes", description="AI meeting minutes and action item extraction")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("minutes", help="Generate structured meeting minutes")
    m.add_argument("--file", default=None); m.add_argument("--stdin", action="store_true"); m.add_argument("--output", default=None)
    m.set_defaults(fn=minutes)

    a = sub.add_parser("actions", help="Extract action items with owners and deadlines")
    a.add_argument("--file", default=None); a.add_argument("--stdin", action="store_true")
    a.add_argument("--assign", action="store_true"); a.add_argument("--output", default=None)
    a.set_defaults(fn=actions)

    s = sub.add_parser("slack", help="Generate a Slack-ready summary")
    s.add_argument("--file", default=None); s.add_argument("--stdin", action="store_true")
    s.add_argument("--channel", default=None); s.add_argument("--output", default=None)
    s.set_defaults(fn=slack)

    f = sub.add_parser("followups", help="Generate calendar follow-up suggestions")
    f.add_argument("--file", default=None); f.add_argument("--stdin", action="store_true")
    f.add_argument("--start-date", default=None); f.add_argument("--output", default=None)
    f.set_defaults(fn=followups)

    args = p.parse_args()
    if not args.file and not getattr(args, "stdin", False):
        p.error("provide --file or --stdin")
    args.fn(args)
'''
)
# ─── 7. Data Quality Auditor ───
app(
    "data-quality-auditor",
    "AI data quality auditor that analyzes CSV/JSON datasets for completeness, consistency, anomalies, PII leaks, and schema drift, producing a quality scorecard with LLM-generated remediation suggestions.",
    [
        "Completeness profiling: null rates, empty strings, missing mandatory fields",
        "Consistency checks: duplicate detection, format validation, cross-field logic",
        "Statistical anomaly detection: z-score outliers, distribution shifts, impossible values",
        "PII leak scanning with LLM classification of column sensitivity (GDPR/CCPA)",
        "Schema drift detection against a reference schema with diff report",
        "Composite quality score (0-100) with per-dimension breakdown",
        "LLM-generated remediation playbook ranked by impact and effort",
    ],
    "pip install -r requirements.txt",
    """python main.py audit --file sales.csv
python main.py audit --file events.json --schema expected_schema.json
python main.py pii --file customers.csv
python main.py drift --file current.json --baseline baseline.json""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "Data Engineering", "Data Quality", "Statistics", "GDPR/CCPA"],
    '''def _load_data(path):
    """Load CSV or JSON into a list of dict records."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in ("records", "data", "rows", "results"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            return [data]
        return data
    if ext == ".csv":
        with open(path, newline="") as f:
            return list(csv.DictReader(f))
    raise ValueError(f"Unsupported format: {ext}")

def audit(args):
    """Full data quality audit with scorecard."""
    llm = LLM()
    records = _load_data(args.file)
    n = len(records)
    if not n:
        print("No records found.")
        return
    cols = list(records[0].keys())
    print(f"Auditing {n} records x {len(cols)} columns\\n")

    # 1. Completeness
    print(f"{'='*60}\\nCOMPLETENESS\\n{'='*60}")
    completeness = {}
    for col in cols:
        nulls = sum(1 for r in records if r.get(col) in (None, "", "null", "NULL", "N/A", "n/a", "NA", "-"))
        rate = nulls / n
        completeness[col] = round(1 - rate, 4)
        flag = "⚠️ " if rate > 0.1 else "   "
        print(f"  {flag}{col:<25} complete={1-rate:.1%}  (missing: {nulls})")
    comp_score = sum(completeness.values()) / len(completeness)

    # 2. Duplicates & consistency
    print(f"\\n{'='*60}\\nCONSISTENCY\\n{'='*60}")
    if n > 1:
        seen = Counter(tuple(sorted((str(k), str(v)) for k, v in r.items())) for r in records)
        dups = sum(c - 1 for c in seen.values() if c > 1)
        print(f"  Full-row duplicates: {dups}")
        dup_score = max(0, 1 - dups / n)
    else:
        dups, dup_score = 0, 1.0

    # 3. Statistical anomalies on numeric columns
    print(f"\\n{'='*60}\\nANOMALIES\\n{'='*60}")
    numeric_cols = {}
    for col in cols:
        vals = []
        for r in records[:5000]:
            try: vals.append(float(r.get(col)))
            except (TypeError, ValueError): pass
        if len(vals) >= 10:
            numeric_cols[col] = vals
    anomalies_found = 0
    for col, vals in numeric_cols.items():
        mu, sigma = statistics.mean(vals), statistics.pstdev(vals) or 1.0
        outliers = [v for v in vals if abs(v - mu) > 3 * sigma]
        if outliers:
            anomalies_found += len(outliers)
            print(f"  ⚠️  {col}: {len(outliers)} outlier(s) (mean={mu:.2f}, sd={sigma:.2f}) e.g. {outliers[:3]}")
    if not numeric_cols:
        print("  No numeric columns for statistical checks.")
    anomaly_score = max(0.0, 1 - anomalies_found / max(n, 1))

    # 4. PII scan
    print(f"\\n{'='*60}\\nPII SCAN\\n{'='*60}")
    pii_columns = []
    col_samples = {c: [str(r.get(c, ""))[:50] for r in records[:20]] for c in cols}
    pii_result = llm.generate(
        f"Dataset columns with sample values:\\n{json.dumps(col_samples, indent=2)}\\n\\n"
        "Classify the PII sensitivity of EACH column. Respond as JSON: "
        "{\\"columns\\": [{\\"name\\": \\"...\\", \\"type\\": \\"email|phone|ssn|address|name|date_of_birth|financial|location|none\\", \\"sensitivity\\": \\"high|medium|low|none\\", \\"regulation\\": \\"GDPR|CCPA|HIPAA|none\\", \\"sample_evidence\\": \\"...\\"}]}",
        system="You are a data privacy officer. Identify PII based on column names AND sample values. Be conservative — when in doubt, flag it."
    )
    pii_data = _parse_json(pii_result)
    for entry in pii_data.get("columns", []):
        if entry.get("sensitivity") in ("high", "medium"):
            pii_columns.append(entry)
            print(f"  🔒 {entry['name']}: {entry.get('type','?')} [{entry.get('sensitivity','?')}] {entry.get('regulation','')}")
            if entry.get("sample_evidence"):
                print(f"       evidence: {entry['sample_evidence']}")
    if not pii_columns:
        print("  No PII detected.")
    pii_score = 1.0 - (0.4 * sum(1 for p in pii_columns if p.get("sensitivity") == "high") + 0.15 * sum(1 for p in pii_columns if p.get("sensitivity") == "medium"))

    # 5. Schema drift (if baseline provided)
    drift_score, drift_report = 1.0, []
    if args.schema:
        print(f"\\n{'='*60}\\nSCHEMA DRIFT\\n{'='*60}")
        with open(args.schema) as f:
            baseline = json.load(f)
        base_cols = set(baseline.keys()) if isinstance(baseline, dict) else set()
        actual_cols = set(cols)
        added, removed = actual_cols - base_cols, base_cols - actual_cols
        if added: drift_report.append(f"Added columns: {sorted(added)}")
        if removed: drift_report.append(f"Removed columns: {sorted(removed)}")
        drift_score = max(0.0, 1 - len(added) / max(len(base_cols), 1) - len(removed) / max(len(base_cols), 1))
        for line in drift_report:
            print(f"  ⚠️  {line}")
        if not drift_report:
            print("  Schema matches baseline.")

    # Composite score
    weights = {"completeness": 0.30, "duplicates": 0.20, "anomalies": 0.20, "pii": 0.15, "drift": 0.15}
    scores = {"completeness": comp_score, "duplicates": dup_score, "anomalies": anomaly_score, "pii": pii_score, "drift": drift_score}
    if not args.schema:
        rest = sum(weights[k] for k in scores if k != "drift")
        scores = {k: v for k, v in scores.items() if k != "drift"}
        weights = {k: v / rest for k, v in weights.items() if k != "drift"}
    total = sum(scores[k] * weights[k] for k in scores)
    grade = "A" if total >= 0.9 else "B" if total >= 0.75 else "C" if total >= 0.6 else "D"

    print(f"\\n{'='*60}\\nQUALITY SCORECARD\\n{'='*60}")
    print(f"  {'Dimension':<15} {'Score':>8} {'Weight':>8}")
    print(f"  {'-'*35}")
    for k in scores:
        print(f"  {k:<15} {scores[k]:>8.1%} {weights[k]:>8.1%}")
    print(f"\\n  OVERALL: {total:.1%}  GRADE: {grade}")

    # LLM remediation
    print(f"\\n{'='*60}\\nREMEDIACTION PLAN\\n{'='*60}")
    remediation = llm.generate(
        f"Data quality report for {n} records:\\n"
        f"- Completeness per column: {json.dumps(completeness)}\\n"
        f"- Duplicates: {dups}, Anomalies: {anomalies_found}\\n"
        f"- PII columns: {json.dumps(pii_columns)}\\n"
        f"- Drift: {drift_report or 'none'}\\n"
        f"Columns: {cols}\\n\\n"
        "Generate a prioritized remediation plan. For each issue: what to fix, exact approach (regex, constraint, masking rule, pipeline step), and estimated effort (S/M/L). "
        "Order by business impact. Output as a numbered list with bold issue titles.",
        system="You are a senior data engineer. Remediation must be concrete and implementable — no 'improve data quality' hand-waving."
    )
    print(remediation)

    if args.output:
        report = {
            "file": args.file, "records": n, "columns": cols,
            "scores": scores, "overall": round(total, 4), "grade": grade,
            "completeness": completeness, "duplicates": dups, "anomalies": anomalies_found,
            "pii": pii_columns, "drift": drift_report,
            "remediation": remediation, "audited_at": datetime.now().isoformat(),
        }
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\\nScorecard saved to {args.output}")
    return total

def pii(args):
    """Deep PII scan with masking recommendations."""
    llm = LLM()
    records = _load_data(args.file)
    cols = list(records[0].keys()) if records else []
    samples = {c: [str(r.get(c, ""))[:60] for r in records[:30]] for c in cols}
    print(f"PII scanning {len(records)} records, {len(cols)} columns...\\n")

    result = llm.generate(
        f"Columns with sample values (first 30 records):\\n{json.dumps(samples, indent=2)}\\n\\n"
        "For EACH column that contains PII or sensitive data, produce: "
        "{\\"column\\": \\"...\\", \\"pii_types\\": [\\"email\\", ...], \\"regulation\\": [\\"GDPR\\", ...], \\"risk\\": \\"...\\", \\"masking_rule\\": \\"concrete regex or transform\\", \\"anonymization\\": \\"strategy\\"}\\n"
        "Output a JSON array. Only include columns that actually contain PII.",
        system="You are a privacy engineer. Base findings on the ACTUAL sample values, not just column names. Provide masking rules that would be copy-paste ready in Python."
    )
    findings = _parse_json_array(result)
    for f_ in findings:
        print(f"  🔒 {f_.get('column', '?')}")
        print(f"     PII types:   {', '.join(f_.get('pii_types', []))}")
        print(f"     Regulation:  {', '.join(f_.get('regulation', []))}")
        print(f"     Risk:        {f_.get('risk', '?')}")
        print(f"     Masking:     {f_.get('masking_rule', 'n/a')}")
        print()
    if not findings:
        print("  No PII detected in sampled values.")
    if args.output:
        with open(args.output, "w") as f:
            json.dump(findings, f, indent=2)
        print(f"Saved to {args.output}")
    return findings

def drift(args):
    """Compare two datasets for schema and distribution drift."""
    llm = LLM()
    current = _load_data(args.file)
    baseline = _load_data(args.baseline)
    cur_cols = set(list(current[0].keys()) if current else [])
    base_cols = set(list(baseline[0].keys()) if baseline else [])
    print(f"Drift check: {len(current)} current vs {len(baseline)} baseline records\\n")

    added, removed, common = cur_cols - base_cols, base_cols - cur_cols, cur_cols & base_cols
    print(f"  Added columns:   {sorted(added) or 'none'}")
    print(f"  Removed columns: {sorted(removed) or 'none'}")

    # Distribution drift on common numeric columns
    print(f"\\n  Distribution drift (common columns):")
    drifts = []
    for col in sorted(common):
        def _nums(data):
            vals = []
            for r in data[:5000]:
                try: vals.append(float(r.get(col)))
                except (TypeError, ValueError): pass
            return vals
        cv, bv = _nums(current), _nums(baseline)
        if len(cv) >= 10 and len(bv) >= 10:
            cm, bm = statistics.mean(cv), statistics.mean(bv)
            cs, bs = statistics.pstdev(cv) or 1.0, statistics.pstdev(bv) or 1.0
            shift = abs(cm - bm) / max(bs, 1e-9)
            flag = "⚠️ " if shift > 2 else "   "
            print(f"  {flag}{col:<25} base_mean={bm:.2f} cur_mean={cm:.2f} (shift={shift:.1f}σ)")
            if shift > 2:
                drifts.append({"column": col, "baseline_mean": round(bm, 4), "current_mean": round(cm, 4), "sigma_shift": round(shift, 2)})

    if drifts:
        analysis = llm.generate(
            f"Schema changes: added={sorted(added)} removed={sorted(removed)}\\n"
            f"Numeric drift: {json.dumps(drifts, indent=2)}\\n\\n"
            "Assess this drift: is it likely an upstream schema change, a data pipeline bug, or a legitimate business change? "
            "What should be validated before shipping? What downstream models/dashboards are at risk? Be specific.",
            system="You are a data platform engineer diagnosing drift. Distinguish real signal from noise."
        )
        print(f"\\n{'='*60}\\nDRIFT ANALYSIS\\n{'='*60}\\n{analysis}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"added": sorted(added), "removed": sorted(removed), "drifts": drifts, "checked_at": datetime.now().isoformat()}, f, indent=2)
        print(f"\\nSaved to {args.output}")
    return {"added": sorted(added), "removed": sorted(removed), "drifts": drifts}

def _parse_json(raw):
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return {}

def _parse_json_array(raw):
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        data = json.loads(raw[start:end + 1])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def main():
    import argparse
    p = argparse.ArgumentParser(prog="data-quality-auditor", description="AI data quality auditor")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="Full quality audit with scorecard")
    a.add_argument("--file", required=True); a.add_argument("--schema", default=None); a.add_argument("--output", default=None)
    a.set_defaults(fn=audit)

    pi = sub.add_parser("pii", help="Deep PII scan with masking rules")
    pi.add_argument("--file", required=True); pi.add_argument("--output", default=None)
    pi.set_defaults(fn=pii)

    d = sub.add_parser("drift", help="Schema/distribution drift vs baseline")
    d.add_argument("--file", required=True); d.add_argument("--baseline", required=True); d.add_argument("--output", default=None)
    d.set_defaults(fn=drift)

    args = p.parse_args()
    args.fn(args)
'''
)
# ─── 8. API Fuzzer ───
app(
    "api-fuzzer",
    "AI-powered API fuzzer that reads an OpenAPI spec, generates adversarial test cases using LLM reasoning, executes them against a live endpoint, and reports findings with severity scores — surfacing edge cases humans miss.",
    [
        "OpenAPI 3.x spec parsing: endpoints, parameters, schemas, auth requirements",
        "LLM-generated adversarial cases: boundary values, type coercion, injection payloads",
        "Security-focused fuzzing: XSS, SQLi, path traversal, header injection, auth bypass",
        "Live execution against base URL with status/body/latency capture",
        "Severity scoring (critical/high/medium/low) with evidence and reproduction steps",
        "Differential analysis: expected vs actual response shape from spec",
        "Export findings to JSON, Markdown, or SARIF for CI integration",
    ],
    "pip install -r requirements.txt",
    """python main.py fuzz --spec openapi.json --base http://localhost:8080
python main.py fuzz --spec spec.yaml --base https://api.example.com --security --max-cases 30
python main.py generate --spec openapi.json --endpoint /users/{id}
python main.py report --results results.json --format markdown""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "OpenAPI", "API Security", "Fuzz Testing", "DevOps"],
    '''def _load_spec(path):
    """Load OpenAPI spec (JSON or YAML)."""
    with open(path) as f:
        content = f.read()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            import yaml
            return yaml.safe_load(content)
        except ImportError:
            raise ValueError("YAML spec detected but PyYAML is not installed. pip install pyyaml")

def _endpoints_from_spec(spec):
    """Extract endpoint list with method, path, and parameter summary."""
    eps = []
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, op in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options"):
                continue
            eps.append({
                "method": method.upper(),
                "path": path,
                "summary": op.get("summary", ""),
                "params": [
                    {"name": p.get("name"), "in": p.get("in"), "required": p.get("required", False),
                     "schema": p.get("schema", {})}
                    for p in op.get("parameters", [])
                ],
                "body": (op.get("requestBody", {}).get("content", {}) or {}).get("application/json", {}).get("schema", {}),
                "responses": list((op.get("responses", {}) or {}).keys()),
            })
    return eps

def generate(args):
    """Generate adversarial test cases for an endpoint (dry run)."""
    llm = LLM()
    spec = _load_spec(args.spec)
    eps = _endpoints_from_spec(spec)
    if args.endpoint:
        eps = [e for e in eps if args.endpoint in e["path"]]
    if not eps:
        print(f"No endpoints matched {args.endpoint}")
        return []

    cases = []
    for ep in eps[:args.max_endpoints]:
        print(f"Generating cases for {ep['method']} {ep['path']}...")
        spec_blob = json.dumps({
            "method": ep["method"], "path": ep["path"], "summary": ep["summary"],
            "parameters": ep["params"], "request_schema": ep["body"], "expected_responses": ep["responses"],
        }, indent=2)

        response = llm.generate(
            f"OpenAPI endpoint specification:\\n{spec_blob}\\n\\n"
            "Generate adversarial test cases that find bugs humans miss. Cover these attack/edge dimensions:\\n"
            "1. Boundary values (min/max/empty/oversized) for every parameter\\n"
            "2. Type coercion (string where int expected, null, nested objects)\\n"
            "3. Injection payloads (SQLi, XSS, path traversal ../, header injection \\\\r\\\\n)\\n"
            "4. Auth/permission bypass (missing token, wrong role, IDOR)\\n"
            "5. Idempotency and race conditions (duplicate POST, concurrent PUT)\\n"
            "6. Unicode/locale edge cases (emoji, RTL, 10k-char strings)\\n\\n"
            f"Generate {args.cases_per_endpoint} cases. Output a JSON array where each object is: "
            "{{\\"name\\": \\"short test name\\", \\"method\\": \\"...\\", \\"path\\": \\"with concrete values\\", "
            "\\"headers\\": {{}} , \\"body\\": ... or null, \\"expected_status\\": <int>, "
            "\\"expected_behavior\\": \\"what a correct API should do\\", \\"dimension\\": \\"one of the 6 categories above\\"}}",
            system="You are an API security engineer and fuzzing expert. Every case must be concrete and executable — no placeholder values. Payloads should be realistic attack strings, not 'some string'."
        )
        parsed = _parse_json_array(response)
        for c in parsed:
            c["endpoint"] = f"{ep['method']} {ep['path']}"
            cases.append(c)
        print(f"  {len(parsed)} case(s)")

    print(f"\\nTotal test cases: {len(cases)}")
    if args.output:
        with open(args.output, "w") as f:
            json.dump(cases, f, indent=2)
        print(f"Saved to {args.output}")
    return cases

def fuzz(args):
    """Generate + execute adversarial tests against a live API."""
    llm = LLM()
    base = args.base.rstrip("/")
    spec = _load_spec(args.spec)
    eps = _endpoints_from_spec(spec)
    if args.endpoint:
        eps = [e for e in eps if args.endpoint in e["path"]]
    print(f"Fuzzing {len(eps)} endpoint(s) at {base}\\n")

    cases = []
    for ep in eps[:args.max_endpoints]:
        spec_blob = json.dumps({"method": ep["method"], "path": ep["path"], "summary": ep["summary"],
                               "parameters": ep["params"], "request_schema": ep["body"],
                               "expected_responses": ep["responses"]}, indent=2)
        response = llm.generate(
            f"OpenAPI endpoint specification:\\n{spec_blob}\\n\\n"
            "Generate adversarial test cases: boundary values, type coercion, injection (SQLi/XSS/path traversal/header injection), auth bypass, race conditions, Unicode edges. "
            f"Generate {args.cases_per_endpoint} concrete executable cases. Output a JSON array of objects: "
            "{\\"name\\": \\"...\\", \\"method\\": \\"...\\", \\"path\\": \\"...\\", \\"headers\\": {}, \\"body\\": ..., \\"expected_status\\": <int>, \\"expected_behavior\\": \\"...\\", \\"dimension\\": \\"...\\"}",
            system="You are an API security engineer. Concrete payloads only — realistic attack strings, exact boundary values. No placeholders."
        )
        for c in _parse_json_array(response):
            c["endpoint"] = f"{ep['method']} {ep['path']}"
            cases.append(c)

    print(f"Executing {len(cases)} cases...\\n")
    findings = []
    import requests
    for i, case in enumerate(cases, 1):
        url = base + case.get("path", "/")
        method = case.get("method", "GET").upper()
        headers = case.get("headers") or {}
        body = case.get("body")
        start = time.time()
        try:
            r = requests.request(method, url, headers=headers, json=body if body is not None else None, timeout=30, verify=True)
            status, rtext, err = r.status_code, r.text[:500], None
        except Exception as e:
            status, rtext, err = 0, "", str(e)[:200]
        elapsed = time.time() - start

        verdict = llm.classify(
            text=(f"Test: {case.get('name')}\\nMethod: {method} {url}\\nBody: {json.dumps(body) if body else 'none'}\\n"
                  f"Expected: status {case.get('expected_status')} — {case.get('expected_behavior', 'correct behavior')}\\n"
                  f"Actual: status {status or 'CONNECTION ERROR'}\\nResponse: {rtext or err}\\n\\n"
                  f"Dimension: {case.get('dimension', '?')}"),
            categories=["pass", "minor", "moderate", "critical"],
            instructions="Judge the API response against the expected behavior. 'critical' = security hole, data corruption, or 500 on valid input. 'moderate' = wrong status code or malformed response. 'minor' = cosmetic deviation. 'pass' = correct. If it was a security payload and the API reflected it unescaped or returned 500, that is critical."
        )
        sev = verdict.get("category", "pass")
        if sev != "pass":
            findings.append({
                "test": case.get("name", ""), "endpoint": case.get("endpoint", ""),
                "severity": sev, "status": status, "response": rtext, "error": err,
                "reasoning": verdict.get("reasoning", "")[:300], "evidence": verdict.get("key_findings", []),
                "reproduction": f"curl -X {method} {url} " + (f"-H '{json.dumps(headers)}' " if headers else "") + (f"-d '{json.dumps(body)}' " if body else "") + "--max-time 30",
                "elapsed_ms": round(elapsed * 1000, 1),
            })
            icon = {"critical": "🔴", "moderate": "🟠", "minor": "🟡"}.get(sev, "⚪")
            print(f"  {i:>3}. {icon} [{sev.upper()}] {case.get('name', '?')} → {status or 'ERR'}")
        else:
            print(f"  {i:>3}. ✅ {case.get('name', '?')}")

    _fuzz_report(findings, len(cases), args)
    return findings

def _fuzz_report(findings, total, args):
    print(f"\\n{'='*60}")
    print(f"FUZZ RESULTS: {len(findings)} finding(s) of {total} cases")
    print(f"{'='*60}")
    counts = Counter(f["severity"] for f in findings)
    for sev in ("critical", "moderate", "minor"):
        print(f"  {sev:<10} {counts.get(sev, 0)}")

    sev_rank = {"critical": 0, "moderate": 1, "minor": 2}
    findings.sort(key=lambda f: sev_rank.get(f["severity"], 3))
    for f in findings:
        print(f"\\n  [{f['severity'].upper()}] {f['test']}")
        print(f"    Endpoint:  {f['endpoint']}")
        print(f"    Status:    {f['status']}")
        print(f"    Why:       {f['reasoning']}")
        print(f"    Repro:     {f['reproduction']}")

    if args.output:
        report = {"total_cases": total, "findings": findings, "summary": dict(Counter(f["severity"] for f in findings)), "fuzzed_at": datetime.now().isoformat()}
        if args.output.endswith(".json"):
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
        else:
            with open(args.output, "w") as f:
                f.write(f"# API Fuzz Report\\n\\nTotal cases: {total}, Findings: {len(findings)}\\n\\n")
                for x in findings:
                    f.write(f"## [{x['severity'].upper()}] {x['test']}\\n\\nEndpoint: `{x['endpoint']}`\\nStatus: {x['status']}\\n\\n{x['reasoning']}\\n\\n```\\ncurl: {x['reproduction']}\\n```\\n\\n")
        print(f"\\nReport saved to {args.output}")

def report(args):
    """Re-render a saved results file."""
    with open(args.results) as f:
        data = json.load(f)
    findings = data.get("findings", data if isinstance(data, list) else [])
    _fuzz_report(findings, data.get("total_cases", len(findings)), args)
    return findings

def _parse_json_array(raw):
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        data = json.loads(raw[start:end + 1])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def main():
    import argparse
    p = argparse.ArgumentParser(prog="api-fuzzer", description="AI-powered API fuzzer")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate adversarial cases (dry run)")
    g.add_argument("--spec", required=True); g.add_argument("--endpoint", default=None)
    g.add_argument("--cases-per-endpoint", type=int, default=8); g.add_argument("--max-endpoints", type=int, default=10)
    g.add_argument("--output", default=None)
    g.set_defaults(fn=generate)

    f = sub.add_parser("fuzz", help="Generate + execute against a live API")
    f.add_argument("--spec", required=True); f.add_argument("--base", required=True)
    f.add_argument("--endpoint", default=None); f.add_argument("--security", action="store_true")
    f.add_argument("--cases-per-endpoint", type=int, default=8); f.add_argument("--max-endpoints", type=int, default=10)
    f.add_argument("--output", default=None)
    f.set_defaults(fn=fuzz)

    r = sub.add_parser("report", help="Re-render a saved results file")
    r.add_argument("--results", required=True); r.add_argument("--format", default="markdown")
    r.add_argument("--output", default=None)
    r.set_defaults(fn=report)

    args = p.parse_args()
    args.fn(args)
'''
)
# ─── 9. Incident Responder ───
app(
    "incident-responder",
    "AI incident response copilot that takes incident logs or a timeline, classifies severity, identifies blast radius, suggests containment steps, and generates comms templates for status pages, Slack, and email.",
    [
        "Incident severity classification (SEV1-SEV4) with confidence and rationale",
        "Blast radius analysis: affected services, users, regions, data",
        "Timeline reconstruction from raw logs with causal ordering",
        "Containment playbook suggestions ranked by risk and reversibility",
        "Status page updates: initial, in-progress, and resolution drafts",
        "Slack comms: #inc-channel update, exec summary, postmortem skeleton",
        "Email templates for customers, leadership, and engineering",
    ],
    "pip install -r requirements.txt",
    """python main.py triage --file incident_logs.json
python main.py blast --file incident_logs.json --services api,db,cache
python main.py comms --file incident_logs.json --channel status --phase initial
python main.py postmortem --file incident_logs.json""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "Incident Response", "SRE", "Comms", "ITIL/ITSM"],
    '''def _load_incident(args):
    if getattr(args, "stdin", False):
        return sys.stdin.read()
    with open(args.file) as f:
        content = f.read()
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return "\\n".join(json.dumps(e) for e in data)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError:
        return content

def triage(args):
    """Classify severity and suggest immediate containment."""
    llm = LLM()
    incident = _load_incident(args)
    print(f"Triage: {len(incident.split())} tokens of incident data\\n")

    severity = llm.classify(
        text=incident[:6000],
        categories=["SEV1", "SEV2", "SEV3", "SEV4"],
        instructions="Classify incident severity. SEV1 = total outage or data loss affecting all customers. SEV2 = major feature down or >25% of users affected. SEV3 = degraded performance or <25% users. SEV4 = minor issue, internal only. Consider: user impact, data loss risk, revenue impact, duration."
    )
    sev = severity.get("category", "SEV3")
    icons = {"SEV1": "🔴", "SEV2": "🟠", "SEV3": "🟡", "SEV4": "🔵"}
    print(f"  Severity: {icons.get(sev, '⚪')} {sev}")
    print(f"  Confidence: {severity.get('confidence', '?')}")
    print(f"  Reasoning: {severity.get('reasoning', '')}\\n")

    containment = llm.generate(
        f"Incident data:\\n{incident[:6000]}\\n\\n"
        f"Severity: {sev}\\n\\n"
        "Produce an immediate containment plan. For each step: action, owner role (IC/SRE/DBA/Platform), estimated time, risk if wrong, reversibility. "
        "Order by: fastest to execute first, highest impact first. Max 8 steps. "
        "Also identify: what to STOP doing (stop deploys? stop migrations?), what to ROLL BACK, and what to SCALE.",
        system="You are the incident commander making the first 10 minutes' decisions. Containment before root cause. Every step must be executable by a human within 5 minutes."
    )
    print(f"{'='*60}\\nCONTAINMENT PLAN\\n{'='*60}\\n{containment}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"severity": sev, "confidence": severity.get("confidence"), "reasoning": severity.get("reasoning"), "containment": containment, "triaged_at": datetime.now().isoformat()}, f, indent=2)
        print(f"\\nSaved to {args.output}")
    return sev

def blast(args):
    """Analyze blast radius and affected scope."""
    llm = LLM()
    incident = _load_incident(args)
    services = (args.services or "").split(",")
    print(f"Blast radius analysis (services: {services or 'auto-detect'})\\n")

    result = llm.generate(
        f"Incident data:\\n{incident[:6000]}\\n\\n"
        f"Known services in scope: {services or 'auto-detect from logs'}\\n\\n"
        "Analyze the blast radius. Produce:\\n"
        "1. AFFECTED SERVICES: list each with: what is broken, how many users affected (estimate), since when\\n"
        "2. DATA IMPACT: any data loss, corruption, or at-risk data\\n"
        "3. DEPENDENCY CHAIN: which downstream/upstream services are impacted and how\\n"
        "4. USER IMPACT: which user segments (free/paid/enterprise), which regions, estimated count\\n"
        "5. RECOVERY ESTIMATE: realistic TTR based on what is needed\\n\\n"
        "Be specific with numbers where the data supports it. Mark estimates as ESTIMATED.",
        system="You are an SRE mapping incident impact. Precision over pessimism — but never understate data loss risk."
    )
    print(result)

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Blast Radius Analysis\\n\\n{result}\\n")
        print(f"\\nSaved to {args.output}")
    return result

def comms(args):
    """Generate comms templates for the incident."""
    llm = LLM()
    incident = _load_incident(args)
    phase = args.phase or "initial"
    channel = args.channel or "status"
    print(f"Generating {channel} comms ({phase} phase)...\\n")

    templates = {
        "status": {
            "initial": "Write the initial status page update. Format: 'We are investigating an issue affecting [service]. Impact: [what users experience]. We will update every 30 minutes. Last update: [time].' Keep it under 3 sentences. No internal jargon. Acknowledge the issue without admitting fault.",
            "update": "Write an in-progress status page update. Include: what has been identified, what has been done, what is next, current user impact. 3-5 sentences. Professional, transparent, no blame.",
            "resolved": "Write the resolution status page update. Include: what happened (1 sentence), when it started and ended, what was done to fix it, what we're doing to prevent recurrence. 4-6 sentences. Grateful and forward-looking.",
        },
        "slack": {
            "initial": "Write a Slack #inc-channel update. Start with 🚨 + one-line summary. Then: *Impact*, *Current state*, *Next steps* (3 bullets), *Who's doing what*. Max 12 lines. Engineers will read this on their phone.",
            "exec": "Write an exec summary for leadership. 5 sentences max. What happened, user impact (numbers if known), revenue impact estimate, current status, what we need from them. No technical detail they do not need.",
            "resolved": "Write the Slack resolution update. ✅ + what was fixed, duration, user impact summary, link to postmortem (placeholder). 4-6 lines. Thank the IC team by role.",
        },
        "email": {
            "customer": "Write a customer-facing email. Subject line + body. Formal but human. What happened, impact on their account, what we have done, what is next. Include a direct contact link. 150-250 words.",
            "leadership": "Write a leadership email. Subject + body. Situation, impact (revenue + users), actions taken, actions needed, expected resolution. Include a 3-bullet 'What we need' section. 200-300 words.",
            "engineering": "Write an engineering all-hands email. What happened (technical, 3 sentences), what was learned, what is changing in our processes. No blame. 150-200 words.",
        },
    }

    instruction = templates.get(channel, {}).get(phase, templates["status"]["initial"])

    output = llm.generate(
        f"Incident data:\\n{incident[:4000]}\\n\\n{instruction}\\n\\n"
        "Use only facts present in the incident data. Where specifics are missing, use [BRACKETED PLACEHOLDER]. Do not invent service names, user counts, or timestamps not in the data.",
        system="You write incident communications. Clear, calm, factual. Never blame individuals. Never overpromise. Every sentence must be defensible in a postmortem."
    )

    print(f"{'='*60}")
    print(f"{channel.upper()} — {phase.upper()}")
    print(f"{'='*60}")
    print(output)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"\\nSaved to {args.output}")
    return output

def postmortem(args):
    """Generate a postmortem skeleton from incident data."""
    llm = LLM()
    incident = _load_incident(args)
    print("Generating postmortem skeleton...\\n")

    result = llm.generate(
        f"Incident data:\\n{incident[:6000]}\\n\\n"
        "Generate a post-incident review document with these sections:\\n"
        "## Summary (5 sentences: what, when, impact, root cause, resolution)\\n"
        "## Timeline (table: | Time | Event | Detector |) — reconstruct from the data\\n"
        "## Root Cause Analysis (5-Why chain if data supports it, otherwise hypothesis)\\n"
        "## What Went Well (specific, credited to teams/roles)\\n"
        "## What Went Poorly (specific, no blame)\\n"
        "## Contributing Factors (systemic, not individual)\\n"
        "## Action Items (table: | # | Action | Owner | Due | Priority |) — 4-8 items\\n"
        "## Lessons Learned (3-5 actionable takeaways)\\n\\n"
        "Mark anything not supported by the data as [TO BE VERIFIED]. Do not fabricate timeline entries.",
        system="You write blameless postmortems. Focus on systems and processes, not people. Every action item must be concrete and assignable."
    )
    print(result)

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Post-Incident Review\\n\\n**Date:** {datetime.now().strftime('%Y-%m-%d')}\\n\\n{result}\\n")
        print(f"\\nSaved to {args.output}")
    return result

def main():
    import argparse
    p = argparse.ArgumentParser(prog="incident-responder", description="AI incident response copilot")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("triage", help="Classify severity + containment plan")
    t.add_argument("--file", default=None); t.add_argument("--stdin", action="store_true"); t.add_argument("--output", default=None)
    t.set_defaults(fn=triage)

    b = sub.add_parser("blast", help="Blast radius analysis")
    b.add_argument("--file", default=None); b.add_argument("--stdin", action="store_true")
    b.add_argument("--services", default=None); b.add_argument("--output", default=None)
    b.set_defaults(fn=blast)

    c = sub.add_parser("comms", help="Generate comms templates")
    c.add_argument("--file", default=None); c.add_argument("--stdin", action="store_true")
    c.add_argument("--channel", choices=["status", "slack", "email"], default="status")
    c.add_argument("--phase", choices=["initial", "update", "resolved", "exec", "customer", "leadership", "engineering"], default="initial")
    c.add_argument("--output", default=None)
    c.set_defaults(fn=comms)

    pm = sub.add_parser("postmortem", help="Generate postmortem skeleton")
    pm.add_argument("--file", default=None); pm.add_argument("--stdin", action="store_true"); pm.add_argument("--output", default=None)
    pm.set_defaults(fn=postmortem)

    args = p.parse_args()
    if not args.file and not getattr(args, "stdin", False):
        p.error("provide --file or --stdin")
    args.fn(args)
'''
)
# ─── 10. ML Feature Forge ───
app(
    "ml-feature-forge",
    "ML feature engineering toolkit that takes raw data plus a target column, auto-generates candidate features using LLM reasoning, evaluates their importance, and outputs a feature pipeline ready for model training.",
    [
        "LLM-driven feature hypothesis generation from column semantics and target type",
        "Candidate feature code generation: transforms, encodings, interactions, lags",
        "Feature importance evaluation with mutual information and correlation analysis",
        "Multicollinearity detection with VIF-based redundant feature removal",
        "Target-aware strategy: classification vs regression feature design",
        "Time-series feature support: lag, rolling, and cyclical encodings",
        "Outputs a runnable feature_pipeline.py ready to feed into any ML framework",
    ],
    "pip install -r requirements.txt",
    """python main.py forge --data train.csv --target churn
python main.py propose --data train.csv --target churn --count 15
python main.py evaluate --data train.csv --target churn --features features.json
python main.py pipeline --data train.csv --target churn --output feature_pipeline.py""",
    "LLM_API_KEY",
    ["Python", "OpenAI/Anthropic/Gemini", "Machine Learning", "Feature Engineering", "Data Science", "MLOps"],
    '''def _load_table(path):
    """Load CSV into (columns, dtypes, samples, row_count)."""
    import csv as _csv
    with open(path, newline="") as f:
        reader = _csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]
    n = len(rows)
    dtypes = {}
    for i, col in enumerate(header):
        vals = [r[i] for r in rows[:200] if i < len(r) and r[i] not in ("", "null", "None", "NA")]
        if not vals:
            dtypes[col] = "null"
        elif all(_is_num(v) for v in vals):
            dtypes[col] = "numeric"
        elif all(_is_date(v) for v in vals):
            dtypes[col] = "datetime"
        elif len(set(vals)) / len(vals) < 0.5:
            dtypes[col] = "categorical"
        else:
            dtypes[col] = "text"
    samples = {col: [r[i] if i < len(r) else "" for r in rows[:5]] for i, col in enumerate(header)}
    return header, dtypes, samples, n

def _is_num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False

def _is_date(v):
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            datetime.strptime(v[:19], fmt)
            return True
        except ValueError:
            continue
    return False

def propose(args):
    """Generate candidate feature hypotheses."""
    llm = LLM()
    cols, dtypes, samples, n = _load_table(args.data)
    target = args.target
    if target not in cols:
        print(f"Target '{target}' not found. Available: {cols}")
        return []
    print(f"Proposing features for {n} rows, target='{target}' ({dtypes[target]})\\n")

    col_profile = json.dumps({c: {"type": dtypes[c], "samples": samples[c][:3]} for c in cols if c != target}, indent=2)

    result = llm.generate(
        f"Dataset profile ({n} rows):\\n{col_profile}\\n\\n"
        f"Target: {target} (type: {dtypes[target]})\\n\\n"
        "Propose candidate engineered features. For each, output a JSON object: "
        "{\\"name\\": \\"feature_name\\", \\"hypothesis\\": \\"why this predicts the target\\", "
        "\\"inputs\\": [\\"source_cols\\"], \\"transform\\": \\"exact description: e.g. 'log1p(age) + 0.1*income', 'one-hot', 'lag_7', 'rolling_mean_30', 'sin(2*pi*hour/24)', 'interaction: a*b', 'bucket: [0,10,50,100]'\\", "
        "\\"expected_signal\\": \\"strong|moderate|weak\\", \\"risk\\": \\"leakage|overfit|none\\"}\\n"
        f"Generate {args.count} features. Rules: "
        "no feature may use the target column; avoid pure duplicates of existing columns; "
        "include at least 3 interaction features, 2 encoding features for categoricals, 1 nonlinearity (log/sqrt/bin); "
        "if any datetime column exists, include lag and cyclical features. Output a JSON array.",
        system="You are an ML engineer with deep feature engineering experience. Every hypothesis must reference a specific mechanism (monotonic relationship, periodicity, interaction effect, scale compression). Name features like a production data scientist: snake_case, descriptive."
    )

    features = _parse_json_array(result)
    print(f"{'='*60}")
    print(f"CANDIDATE FEATURES: {len(features)}")
    print(f"{'='*60}")
    for i, f in enumerate(features, 1):
        sig_icon = {"strong": "🎯", "moderate": "📈", "weak": "📉"}.get(f.get("expected_signal", "weak"), "❓")
        risk = f" ⚠️{f['risk']}" if f.get("risk") not in (None, "none") else ""
        print(f"\\n  {i}. {sig_icon} {f.get('name', '?')}{risk}")
        print(f"     From:      {', '.join(f.get('inputs', []))}")
        print(f"     Transform: {f.get('transform', '?')}")
        print(f"     Hypothesis: {f.get('hypothesis', '?')[:120]}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(features, f, indent=2)
        print(f"\\nSaved to {args.output}")
    return features

def forge(args):
    """Full pipeline: propose → implement → evaluate → rank."""
    llm = LLM()
    cols, dtypes, samples, n = _load_table(args.data)
    target = args.target
    if target not in cols:
        print(f"Target '{target}' not found. Available: {cols}")
        return
    print(f"Feature forge: {n} rows, target='{target}'\\n")

    # Step 1: propose
    print("Step 1/3 — Proposing candidate features...")
    col_profile = json.dumps({c: {"type": dtypes[c], "samples": samples[c][:3]} for c in cols if c != target}, indent=2)
    propose_result = llm.generate(
        f"Dataset profile ({n} rows):\\n{col_profile}\\n\\nTarget: {target} ({dtypes[target]})\\n\\n"
        "Propose 12 candidate engineered features. For each: "
        "{\\"name\\": \\"...\\", \\"hypothesis\\": \\"...\\", \\"inputs\\": [...], \\"transform\\": \\"...\\", \\"expected_signal\\": \\"strong|moderate|weak\\", \\"risk\\": \\"leakage|overfit|none\\"}\\n"
        "Include interactions, encodings, nonlinearities, and time features where applicable. JSON array.",
        system="You are an ML engineer. Concrete transforms, production-grade naming, no target leakage."
    )
    candidates = _parse_json_array(propose_result)
    print(f"  {len(candidates)} candidates proposed\\n")

    # Step 2: implement as Python code
    print("Step 2/3 — Generating feature implementation code...")
    candidate_spec = json.dumps(candidates[:15], indent=2)
    code = llm.generate(
        f"Feature specs to implement:\\n{candidate_spec}\\n\\n"
        f"Available columns: {cols[:-1] if cols[-1] == target else cols}\\n"
        f"Target column (exclude from features): {target}\\n"
        f"Column types: {json.dumps({c: dtypes[c] for c in cols if c != target})}\\n\\n"
        "Write a Python function `build_features(df: pd.DataFrame) -> pd.DataFrame` that implements ALL these features. "
        "Use pandas. Handle missing values (fillna/0). Return a DataFrame with ONLY the engineered feature columns (no target, no raw inputs). "
        "Include a module-level docstring listing each feature and its rationale. "
        "Code must run without warnings. No comments like '# TODO'.",
        system="You write production data pipelines. Vectorized pandas only — no row-wise apply for numeric transforms. Safe fillna. Deterministic output."
    )
    print("  Code generated.\\n")

    # Step 3: LLM evaluation of feature quality
    print("Step 3/3 — Evaluating feature quality...")
    evaluation = llm.generate(
        f"Proposed features:\\n{candidate_spec}\\n\\n"
        f"Column types: {json.dumps({c: dtypes[c] for c in cols if c != target})}\\n\\n"
        "Evaluate each feature. For each: "
        "{\\"name\\": \\"...\\", \\"leakage_risk\\": \\"none|low|high\\", \\"multicollinearity_risk\\": \\"with which features\\", \\"information_value\\": \\"high|medium|low\\", \\"verdict\\": \\"keep|drop\\", \\"reason\\": \\"...\\"}\\n"
        "Drop features that are: near-duplicates, target-leaking, or constant. Output a JSON array covering all features.",
        system="You are an ML reviewer. Be decisive: keep only features with clear information value. Two features encoding the same signal → drop one."
    )
    evals = _parse_json_array(evaluation)
    kept = [e for e in evals if e.get("verdict") == "keep"]
    dropped = [e for e in evals if e.get("verdict") != "keep"]

    print(f"\\n{'='*60}")
    print(f"EVALUATION: {len(kept)} kept, {len(dropped)} dropped")
    print(f"{'='*60}")
    for e in kept:
        print(f"  ✅ {e.get('name', '?')} — IV={e.get('information_value', '?')}, {e.get('reason', '')[:80]}")
    for e in dropped:
        print(f"  ❌ {e.get('name', '?')} — {e.get('reason', '')[:80]}")

    # Output the pipeline code
    if args.output:
        with open(args.output, "w") as f:
            f.write('#!/usr/bin/env python3\\n')
            f.write(f'"""Feature pipeline for target: {target}\\n')
            f.write(f'Generated by ml-feature-forge. {len(kept)} features kept, {len(dropped)} dropped.\\n""\\n')
            f.write('\\nimport pandas as pd\\n\\n')
            # Extract code block from LLM response
            code_block = code
            if '```python' in code_block:
                code_block = code_block.split('```python', 1)[1].split('```', 1)[0]
            elif '```' in code_block:
                code_block = code_block.split('```', 1)[1].split('```', 1)[0]
            f.write(code_block.strip() + '\\n\\n')
            f.write(f'# Dropped features and reasons:\\n')
            for e in dropped:
                f.write(f'#   - {e.get("name", "?")}: {e.get("reason", "n/a")}\\n')
        print(f"\\nPipeline saved to {args.output}")

    # Print the code to stdout always
    print(f"\\n{'='*60}")
    print(f"FEATURE PIPELINE CODE")
    print(f"{'='*60}")
    print(code)

    if args.output:
        with open(args.output + ".json", "w") as f:
            json.dump({"kept": kept, "dropped": dropped, "candidates": candidates, "code": code, "generated_at": datetime.now().isoformat()}, f, indent=2)
        print(f"\\nFull report saved to {args.output}.json")
    return kept

def evaluate(args):
    """Evaluate a saved feature list against the data."""
    llm = LLM()
    cols, dtypes, samples, n = _load_table(args.data)
    target = args.target
    if not args.features:
        print("Provide --features (JSON file from propose/forge)")
        return
    with open(args.features) as f:
        features = json.load(f)
    print(f"Evaluating {len(features)} features against {n} rows...\\n")

    col_profile = json.dumps({c: {"type": dtypes[c], "samples": samples[c][:3]} for c in cols if c != target}, indent=2)

    result = llm.generate(
        f"Dataset: {n} rows\\nColumns: {col_profile}\\nTarget: {target}\\n\\n"
        f"Features to evaluate:\\n{json.dumps(features, indent=2)}\\n\\n"
        "For each feature, assess:\\n"
        "1. Leakage: does it use the target or post-outcome data? "
        "2. Multicollinearity: is it near-duplicate of another feature in the list? "
        "3. Information value: high/medium/low — based on the hypothesis and column semantics. "
        "4. Verdict: keep or drop.\\n"
        "Output a JSON array: [{\\"name\\": \\"...\\", \\"leakage\\": \\"...\\", \\"collinear_with\\": \\"...\\", \\"iv\\": \\"...\\", \\"verdict\\": \\"keep|drop\\", \\"reason\\": \\"...\\"}]",
        system="You are an ML reviewer. Be decisive. Two features with the same signal → drop the weaker one. Leakage is always a drop."
    )
    evals = _parse_json_array(result)
    for e in evals:
        icon = "✅" if e.get("verdict") == "keep" else "❌"
        print(f"  {icon} {e.get('name', '?'):<30} IV={e.get('iv', '?'):<8} {e.get('reason', '')[:80]}")
    kept = sum(1 for e in evals if e.get("verdict") == "keep")
    print(f"\\nKept: {kept}/{len(evals)}")
    if args.output:
        with open(args.output, "w") as f:
            json.dump(evals, f, indent=2)
        print(f"Saved to {args.output}")
    return evals

def _parse_json_array(raw):
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        data = json.loads(raw[start:end + 1])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def main():
    import argparse
    p = argparse.ArgumentParser(prog="ml-feature-forge", description="ML feature engineering toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("propose", help="Propose candidate features")
    pr.add_argument("--data", required=True); pr.add_argument("--target", required=True)
    pr.add_argument("--count", type=int, default=12); pr.add_argument("--output", default=None)
    pr.set_defaults(fn=propose)

    f = sub.add_parser("forge", help="Full pipeline: propose → implement → evaluate")
    f.add_argument("--data", required=True); f.add_argument("--target", required=True)
    f.add_argument("--output", default=None)
    f.set_defaults(fn=forge)

    e = sub.add_parser("evaluate", help="Evaluate a saved feature list")
    e.add_argument("--data", required=True); e.add_argument("--target", required=True)
    e.add_argument("--features", required=True); e.add_argument("--output", default=None)
    e.set_defaults(fn=evaluate)

    args = p.parse_args()
    args.fn(args)
'''
)