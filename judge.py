"""The judging behind verdicts.jsonl, as the DRACO paper does it (arXiv 2602.11685): one call per criterion, MET or
UNMET, the paper's judge prompt (judge_prompt.txt), thinking low, temperature 0.2, the whole report given, nothing cut.
Needs GEMINI_API_KEY and the benchmark's test.jsonl (huggingface.co/datasets/perplexity-ai/draco) beside this file.
Every reply is saved before it is read; a criterion with a saved reply is never asked again.
    python judge.py OUT.jsonl [--check | --one]"""
import json, os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
import httpx

MODEL = "gemini-3.1-pro-preview"   # the paper's judge, Gemini 3 Pro, is no longer served
OUT = sys.argv[1]
SYSTEM = open("judge_prompt.txt", encoding="utf-8").read().strip()
USER = "<criterion_type>\n{type}\n</criterion_type>\n<criterion>\n{req}\n</criterion>\n{query}\n<response>\n{page}\n</response>"

jobs = []
for n, line in enumerate(open("test.jsonl", encoding="utf-8"), 1):
    row = json.loads(line)
    page = open(f"reports/{n:03d}.md", encoding="utf-8").read()
    for sec in json.loads(row["answer"])["sections"]:
        for c in sec["criteria"]:
            jobs.append({"task": n, "section": sec["id"], "id": c["id"], "weight": c["weight"],
                         "user": USER.format(type="positive" if c["weight"] > 0 else "negative", req=c["requirement"],
                                             query=row["problem"], page=page)})

if "--check" in sys.argv:
    print(MODEL, len(jobs), "criteria,", sum(j["weight"] < 0 for j in jobs), "negative")
    print(jobs[0]["user"][:400]); sys.exit()

def verdict(text):
    m = re.search(r'"criterion_status"\s*:\s*"(MET|UNMET)"', text or "")
    return m.group(1) if m else None

seen = {(d["task"], d["id"]) for d in map(json.loads, open(OUT, encoding="utf-8"))} if os.path.exists(OUT) else set()
todo = [j for j in jobs if (j["task"], j["id"]) not in seen]
if "--one" in sys.argv: todo = todo[:1]
lock = threading.Lock()
client = httpx.Client(timeout=300, headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]})

def ask(j):
    body = {"systemInstruction": {"parts": [{"text": SYSTEM}]}, "contents": [{"role": "user", "parts": [{"text": j["user"]}]}],
            "generationConfig": {"temperature": 0.2, "thinkingConfig": {"thinkingLevel": "low"}}}
    for attempt in range(4):
        r = client.post(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent", json=body)
        if r.status_code not in (429, 500, 503): break
        threading.Event().wait(10 * (attempt + 1))
    if r.status_code != 200:
        with lock: print(f"task {j['task']} {j['id']}: HTTP {r.status_code} {r.text[:200]}", flush=True)
        return
    reply = r.json()
    try:
        text = "".join(p.get("text", "") for p in reply["candidates"][0]["content"]["parts"] if not p.get("thought"))
    except (KeyError, IndexError):
        text = ""
    with lock:
        open(OUT, "a", encoding="utf-8").write(json.dumps({"task": j["task"], "section": j["section"], "id": j["id"],
                                                             "weight": j["weight"], "verdict": verdict(text), "reply": text}) + "\n")

with ThreadPoolExecutor(8) as ex: list(ex.map(ask, todo))
print(len(todo), "criteria asked; a line whose verdict is null needs a look")
