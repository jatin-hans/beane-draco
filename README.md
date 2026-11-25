# Beane Harness on DRACO

**69.4 on all 100 tasks of [DRACO](https://arxiv.org/abs/2602.11685)**, Perplexity's deep research benchmark, with
**73.3% of its 3,934 criteria passed**. Every report, every verdict and the scripts that produced the numbers are in this
repository.

Beane Harness is a multi-agent deep research system built and maintained by Jatin Hans. It is on the official DeepResearch Bench
leaderboards: 60.5 on DeepResearch Bench II, where it entered at #1 and is the only independent entry on the board, and 56.1
on DeepResearch Bench, in the top three: [jatinhans.com/lab/researcher](https://jatinhans.com/lab/researcher/).

## Result

| | |
|---|---|
| Score, mean over 100 tasks | **69.4** |
| Criteria passed | **73.3%** of 3,934 |
| Median task | 71.1 |
| Lowest and highest task | 26.9, 94.9 |
| Penalty criteria triggered | 107 of 415 |
| Tasks failed or retried | 0 |
| Cost per task | $12.58 |
| Time per task | about 25 minutes |

One run per task, the question as its only input, all 100 tasks, no task rerun or replaced.

### Beside published results

| System | Score | Pass rate | Judge | Reported by |
|---|---|---|---|---|
| Valyu DeepResearch | 72.7 | | Gemini 3 Pro, as reported | Valyu |
| CoChat | 71.1 | | Gemini 3.1 Pro | CoChat |
| Perplexity Deep Research (Opus 4.6) | 70.5 | 72.8% | Gemini 3 Pro | DRACO paper |
| **Beane Harness** | **69.4** | **73.3%** | Gemini 3.1 Pro | this repository |
| OpenRouter Fusion | 69.0 | | Gemini 3.1 Pro | OpenRouter |
| Perplexity Deep Research (Opus 4.5) | 67.2 | | Gemini 3 Pro | DRACO paper |
| Claude Opus 4.6 with search tools | 59.8 | | Gemini 3 Pro | DRACO paper |
| Gemini Deep Research | 59.0 | | Gemini 3 Pro | DRACO paper |
| OpenAI o3 Deep Research | 52.1 | | Gemini 3 Pro | DRACO paper |

Gemini 3 Pro, the paper's judge, was retired in March 2026; Gemini 3.1 Pro is its successor under the same settings.

### By domain

| Domain | Tasks | Score |
|---|---|---|
| Academic | 12 | 81.6 |
| Law | 6 | 81.3 |
| Medicine | 6 | 72.0 |
| General Knowledge | 9 | 68.5 |
| Finance | 20 | 68.5 |
| Technology | 10 | 67.5 |
| Shopping/Product Comparison | 16 | 65.8 |
| Personalized Assistant | 6 | 65.7 |
| Needle in a Haystack | 6 | 62.7 |
| UX Design | 9 | 61.4 |

### By rubric section

| Section | Score | Criteria passed |
|---|---|---|
| Factual accuracy | 69.7 | 69.2% |
| Breadth and depth of analysis | 69.0 | 73.6% |
| Presentation quality | 69.0 | 80.2% |
| Citation quality | 68.5 | 82.1% |

The four sections sit within 1.2 points of each other: the system is not carried by presentation.

## What is here

| File | What it holds |
|---|---|
| `reports/001.md` to `reports/100.md` | The report for each task, exactly as judged, in the dataset's row order |
| `verdicts.jsonl` | All 3,934 verdicts: task, section, criterion id, weight, MET or UNMET, and the judge's explanation |
| `tasks.csv` | Each task's dataset id, domain, score and criteria passed |
| `score.py` | Recomputes every number above from `verdicts.jsonl` (standard library only) |
| `judge.py`, `judge_prompt.txt` | The judging script and the paper's judge prompt |

```
python score.py
```

## Protocol

- **Tasks:** all 100 from [perplexity-ai/draco](https://huggingface.co/datasets/perplexity-ai/draco). The system saw only each task's question.
- **Judge:** the paper's method. One call per criterion, the paper's judge prompt, thinking low, temperature 0.2, the
  whole report given with nothing cut, each criterion judged MET or UNMET.
- **Score:** per task, the weight of criteria judged MET (penalties subtract) over the weight of the positive criteria,
  held to 0 to 100; then the mean over tasks. Pass rate counts a positive criterion that is MET and a penalty that is UNMET.
- **Judgings:** one. The paper averages five and reports a spread of about 0.3 between them.

To judge again: put the dataset's `test.jsonl` beside `judge.py`, set `GEMINI_API_KEY`, run `python judge.py out.jsonl`.

## Credit

DRACO, its tasks, rubrics and judge prompt are the work of its authors at Perplexity (arXiv 2602.11685). The code here is
under the MIT license.
