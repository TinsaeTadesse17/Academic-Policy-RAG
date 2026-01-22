# University Policy & Student Handbook QA (RAG)

This project implements a clean Retrieval-Augmented Generation (RAG) system that answers questions using official university policy documents. It scrapes PDFs, builds a vector index, and serves answers with citations via a FastAPI endpoint.


## Team Members          Student ID
Abel Begashaw            ATR/8919/13
Beleir Mesay             UGR/8657/14
Biruk Maru               UGR/4775/13
Fikreyohannes Abera      UGR/8889/14
Tinsae Tadesse           UGR/3556/14

## Quick Start

1) Create and activate a virtual environment.
2) Install dependencies:

```
pip install -r requirements.txt
```

3) Copy environment variables:

```
copy config.env.sample .env
```

4) Start Qdrant (Docker):

```
docker run -p 6333:6333 qdrant/qdrant
```

5) Add seed URLs to `data/seed_urls.txt`.
6) Scrape PDFs:

```
python scripts/scrape_pdfs.py
```

7) Build index:

```
python scripts/build_index.py
```

8) Run API:

```
uvicorn app.main:app --reload
```

9) Ask:

```
POST http://localhost:8000/ask
{ "question": "What is the academic probation policy?" }
```

## Evaluation

Create `data/eval_questions.json` with a list of questions, then run:

```
python scripts/eval_rag.py
```

## Project Layout

```
app/          # FastAPI service
data/         # raw and processed data
scripts/      # scraping, indexing, evaluation
src/          # ingestion, retrieval, generation
```
