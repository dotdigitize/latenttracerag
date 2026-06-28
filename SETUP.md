# Setup

## Linux

```bash
cd ~/ai-portfolio
git clone https://github.com/dotdigitize/latenttracerag.git
cd latenttracerag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.seed_data
python -m pytest
uvicorn backend.server:app --host 127.0.0.1 --port 8010
npm install
npm run dev
```

## Windows

```powershell
git clone https://github.com/dotdigitize/latenttracerag.git
cd latenttracerag
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m backend.seed_data
python -m pytest
uvicorn backend.server:app --host 127.0.0.1 --port 8010
npm install
npm run dev
```

## Ollama

Install Ollama from https://ollama.com, start the local service, then pull the configured models:

```bash
ollama pull gemma4:e4b
ollama pull gemma4:e2b
ollama pull embeddinggemma:latest
```

Ollama is optional. When it is unavailable, LatentTraceRAG uses deterministic local fallbacks and marks `model_unavailable` in traces.
