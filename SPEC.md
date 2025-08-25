# Mini Search Engine with Ranked Retrieval — Finalized Project Spec (v2.0)

## 0) Why this project

This project reinforces IR fundamentals (tokenization → inverted index → BM25 → evaluation) while staying small enough to be shippable in a few weeks. It balances learning depth with realistic constraints.

---

## 1) Problem statement

Given a corpus of ~50k–100k documents (titles + bodies), build a small text search engine that supports keyword queries and returns a ranked top-k list in <100 ms/query on a laptop. Provide a CLI and an HTTP API. Include an evaluator for precision@k and nDCG@k.

---

## 2) Scope (In / Out)

**In (v1):**

- UTF-8 text ingestion; whitespace + punctuation tokenization; lowercasing; unicode normalization (NFKC).
- Configurable stopword removal; minimum token length; alnum filter.
- Inverted index: doc_id, tf, d-gapped storage; positions optional (off by default).
- Ranking: BM25 (k1, b) with doc length normalization; optional field boosts (title/body).
- Query processing: OR semantics (default) with configurable `min_should_match`; heap-based top-k.
- Interfaces: CLI + FastAPI.
- Evaluation: precision@k, nDCG@k; golden tests.
- Benchmarks: latency (p50, p95) and index size.

**Out (v1):**

- Distributed indexing
- Stemming/lemmatization
- Embeddings
- Learning-to-rank
- Incremental updates

---

## 3) Dataset choices

- **Stack Overflow (subset)** — rich technical intent, requires HTML sanitization.  
- **arXiv abstracts** — clean JSONL, domain-specific.  
- **Wikipedia (subset)** — broad coverage, but heavier preprocessing + licensing work.  

**Decision:** Start with Stack Overflow or arXiv depending on ease of ingestion. Provide a tiny ≤500-doc dev set and a 10k–20k stage set for iteration speed.

---

## 4) Architecture & data structures

### **Modules**

- `core/`: tokenizer, normalizer, analyzer config.
- `index/`: builder, postings, lexicon, docstore.
- `query/`: parser, BM25 scorer, ranker, explain().
- `api/`: FastAPI service; `cli/`: Typer commands.

### **Inverted index layout**

- Lexicon: term → df, pointer.
- Postings: sorted doc_id gaps + tf (int). VByte compression applied to doc_id gaps.
- Docstore: JSONL (id, title, body, length). Mmap optional.
- Tie-break: deterministic by doc_id.

---

## 5) Ranking: BM25

**Formula:**

```bash
Score(q, d) = Σ terms t in q:
IDF(t) * ((tf_{t,d} * (k1 + 1)) / (tf_{t,d} + k1 * (1 - b + b * |d|/avgdl)))
```

- Defaults: k1 = 1.2, b = 0.75  
- IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5) + 1)  
- Optional field boosts: `w_title`, `w_body`  
- OR semantics with configurable `min_should_match`  
- `--explain` shows per-term contributions

---

## 6) Algorithms & complexity

- **Index build:** one pass → tokenize → postings buffers → sort by doc_id → compress → flush.  
- **Top-k search:** accumulate scores in hashmap keyed by doc_id; size-k min-heap; complexity O(Σ df(t)).  
- **Performance contract:** p50 ≤ 30 ms, p95 ≤ 100 ms for k ≤ 10 on 50k–100k docs.

---

## 7) Interfaces

### **CLI (Typer)**

- `build-index --corpus data.jsonl --out index_dir`
- `search "neural nets" --k 10 --explain`
- `bench --queries queries.txt --k 10`
- `eval --qrels qrels.tsv --queries queries.tsv --k 10`

### **HTTP (FastAPI)**

- `POST /search` → body: `{ "query": "...", "k": 10 }`
- `GET /doc/{id}` → return JSON doc

---

## 8) Evaluation

- Metrics: precision@k, nDCG@k.  
- Ground truth: `qrels.tsv` with labeled queries (manual or heuristic labeling).  
- Golden tests: deterministic ranked ids for a small dev set.

---

## 9) Tech stack & environment

- **Language:** Python 3.12 (fallback 3.11)  
- **CLI:** Typer  
- **HTTP API:** FastAPI + Uvicorn  
- **Testing:** pytest, pytest-benchmark, optional hypothesis  
- **Style:** ruff + pre-commit hooks  
- **Packaging:** uv (or pip-tools) for locked deps  
- **CI:** GitHub Actions (lint, tests, bench smoke)  
- **Perf helpers:** only introduce numpy or Rust/Cython if profiling shows bottlenecks  
- **Serialization:** struct + VByte compression for postings; JSONL docstore  

---

## 10) Reproducibility

- Deterministic tie-break (doc_id).  
- Fix seeds where applicable.  
- Record env (CPU, RAM, OS, Python) in `bench/manifest.json`.  
- Pin corpus snapshot checksum in `data/README.md`.  

---

## 11) Milestones & deliverables

- **M0 – Data & tokenizer (0.5–1 day):** ingest corpus, tokenize/normalize, unit tests.  
- **M1 – Index + BM25 + top-k (1–2 days):** inverted index, ranker, CLI search.  
- **M2 – Deep dive (choose one, 1 day):** ranking quality (field boosts), efficiency (WAND), or evaluation (manual labels).  
- **M3 – Optional polish (0.5–1 day):** phrase search, explain(), HTTP API.  

**Deliverables:** working CLI + API, golden tests, eval metrics, DEMOS.md.

---

## 12) Risks & mitigations

- **Hot terms slow queries:** mitigate with `min_should_match` and postings cap.  
- **Large index size:** VByte compression; mmap docstore.  
- **Nondeterminism:** tie-break by doc_id; lock deps.  

---

## 13) Definition of Done

- 100k-doc corpus search returns k ≤ 20 results in <100 ms p95.  
- Golden tests pass deterministically.  
- Precision@k and nDCG@k reported for labeled queries.  
- README and DEMOS.md provide copy-pasteable usage examples.  

---

## 14) Complexity gates (learning vs performance)

Adopt a conscious upgrade path:

- VByte gaps: always in (low cost, high value).  
- Phrase search / positions: only if needed by real queries.  
- Block-Max WAND: only if p95 exceeds contract on frequent terms.  
- Rust scorer: only if profiling shows ≥30% time in scoring loop.  
- Stemming/lemmatization: only if eval shows recall issues.  

This ensures performance work follows measured pain, not guesswork.

---

## 15) Config defaults (config.toml)

```toml
[kv]
k1 = 1.2
b = 0.75
stopwords = true
positions = false
min_should_match = 1
w_title = 1.4
w_body  = 1.0
tie_breaker = "doc_id"
min_token_len = 2
seed = 0
```

## 16) Repo skeleton

```pgsql
mini-search/
  pyproject.toml
  README.md
  SPEC.md
  DEMOS.md
  src/mini_search/
    core/ (tokenize.py, normalize.py, analyzer.py)
    index/ (builder.py, postings.py, storage.py, docstore.py)
    query/ (parser.py, bm25.py, ranker.py, explain.py)
    api/ (http.py, cli.py)
  tests/
    test_tokenize.py
    test_bm25.py
    test_index_roundtrip.py
    golden/
      queries.tsv
      expected.json
  scripts/
    build_corpus.py
    make_dev_corpus.py
    bench_latency.py
```
