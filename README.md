# Customer Support Ticket AI System

A full-stack AI system designed to analyze customer support tickets, answer natural language questions about them, and detect anomalous patterns.

## Project Features
- **Natural Language Querying**: Extract insights from ticket data using plain English.
- **Anomaly Detection**: Identifies unusual tickets using heuristic rules and Isolation Forest (ML).
- **Streamlit UI**: Minimal frontend for easy data interaction and visualization.
- **FastAPI Backend**: Scalable REST API for core operations.

## Architecture Diagram
```text
[ Streamlit UI ] <---> [ FastAPI Backend ]
                             |
                     +-------+-------+
                     |               |
                [ LangChain  ]  [ Scikit-Learn ]
                [  & Ollama  ]  [   & Pandas   ]
                     |               |
                     +-------+-------+
                             |
                   [ support_tickets.csv ]
```

## Folder Structure
```text
.
├── app.py                   # Streamlit Frontend
├── main.py                  # FastAPI Backend entry point
├── requirements.txt         # Dependencies
├── start.py                 # Single-command runner
├── support_tickets.csv      # Dataset
└── src/                     # Core logic (routes, services, config)
```

## Tech Stack
- **Python**: Core logic.
- **FastAPI & Streamlit**: API and UI frameworks.
- **LangChain & Pandas**: Natural language to data operations.
- **Scikit-Learn**: Anomaly detection.
- **Ollama (`llama3.2`)**: Local LLM for zero-cost, private processing.

## Dataset Overview
Expects `support_tickets.csv` in the root directory containing columns like `ticket_id`, `created_at`, `priority`, `status`, `category`, and `resolution_time_hrs`. The system parses timestamps and optimizes categorical data on load.

## Installation & Setup

1. Install [Ollama](https://ollama.com/) and pull the model: `ollama run llama3.2`
2. Ensure Python 3.9+ is installed.
3. Install dependencies: `pip install -r requirements.txt`
4. Place `support_tickets.csv` in the root folder.

**Single-Command Execution:**
Start both the backend and frontend simultaneously:
```bash
python start.py
```
- API Docs: `http://localhost:8000/docs`
- UI: `http://localhost:8501`

## REST API Endpoints
**1. Health Check (`GET /health`)**
```json
{ "status": "ok", "message": "Service is running" }
```

**2. Natural Language Query (`POST /query`)**
- **Req:** `{"query": "How many open tickets?"}`
- **Res:** `{"query": "How many open tickets?", "answer": "There are 15 open tickets."}`

**3. Anomaly Detection (`GET /anomalies`)**
- **Res:**
```json
{
  "count": 1,
  "anomalies": [{
    "ticket_id": "T123",
    "type": "Heuristic",
    "reason": "Unresolved high-priority ticket older than 24 hours",
    "details": "Priority: Critical, Age: 26.5 hrs"
  }]
}
```

## Example Queries
- *"How many tickets are currently open?"*
- *"Which agent resolved the most tickets?"*
- *"Show all Critical tickets not resolved within 12 hours."*
- *"Average customer rating for Technical tickets?"*
- *"Are there anomalies this week?"*

## Error Handling
- **Global Try-Except Blocks**: All FastAPI endpoints are wrapped to prevent silent crashes.
- **HTTP 500 Responses**: Internal errors are returned explicitly to the client with details.
- **Parsing Fallbacks**: LangChain is configured (`handle_parsing_errors=True`) to recover from LLM formatting mistakes.

## Assumptions
- Dataset `support_tickets.csv` exists in the project root.
- Ollama is running locally on port `11434` with `llama3.2` available.
- "Now" for heuristic anomalies is inferred from the max `created_at` timestamp in the dataset.

## Scalability Considerations
- **Memory Bound**: Data is fully loaded into RAM via Pandas, limiting dataset size.
- **Concurrency**: Local LLMs handle concurrent requests slower than cloud alternatives.
- **Compute Overhead**: Machine learning anomaly detection scales linearly with rows, requiring optimizations for massive datasets.

## Known Limitations
- **Code Execution Risks**: LangChain Pandas agent uses `eval()` internally; production requires sandboxing.
- **Model Hallucinations**: Small models (3B) occasionally generate invalid Pandas code; use larger models for improved reliability.

## Future Improvements
- **Database Integration**: Migrate from CSV/Pandas to PostgreSQL + LangChain SQL Agent.
- **Dockerization**: Add Docker support for consistent deployment.
- **Security**: Implement JWT authentication for API endpoints.
- **Enhanced UI**: Migrate to React/Next.js for advanced visualization.
