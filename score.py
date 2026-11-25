"""Recomputes every number in the README from verdicts.jsonl: python score.py
A task's score is the weight of its criteria judged MET (penalties count against it) over the weight of its positive
criteria, held to 0-100; the benchmark score is the mean over the 100 tasks (DRACO, arXiv 2602.11685)."""
import csv, json, statistics as st
from collections import defaultdict

domain = {int(r["task"]): r["domain"] for r in csv.DictReader(open("tasks.csv", encoding="utf-8"))}
norm = lambda got, pos: 100 * max(0, min(1, got / pos))
task, sec = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
sec_pass, passed, total, pen = defaultdict(lambda: [0, 0]), 0, 0, [0, 0]
for line in open("verdicts.jsonl", encoding="utf-8"):
    d = json.loads(line); w, met = d["weight"], d["verdict"] == "MET"
    for acc in (task[d["task"]], sec[(d["task"], d["section"])]):
        acc[0] += w * met; acc[1] += max(w, 0)
    ok = (w > 0) == met; passed += ok; total += 1
    sec_pass[d["section"]][0] += ok; sec_pass[d["section"]][1] += 1
    if w < 0: pen[0] += met; pen[1] += 1

score = {n: norm(*a) for n, a in task.items()}
assert len(score) == 100 and total == 3934, (len(score), total)
vals = list(score.values())
print(f"score {st.mean(vals):.1f} over {len(vals)} tasks; median {st.median(vals):.1f}, lowest {min(vals):.1f}, highest {max(vals):.1f}")
print(f"pass rate {100 * passed / total:.1f}% of {total} criteria; penalties triggered {pen[0]} of {pen[1]}")
by_dom = defaultdict(list)
for n, s in score.items(): by_dom[domain[n]].append(s)
print("\nby domain")
for k, v in sorted(by_dom.items(), key=lambda x: -st.mean(x[1])): print(f"  {k:26s} {len(v):3d} tasks  {st.mean(v):.1f}")
by_sec = defaultdict(list)
for (n, s), a in sec.items():
    if a[1]: by_sec[s].append(norm(*a))
print("\nby section (score, pass rate)")
for k, v in by_sec.items(): print(f"  {k:30s} {st.mean(v):.1f}   {100 * sec_pass[k][0] / sec_pass[k][1]:.1f}%")
