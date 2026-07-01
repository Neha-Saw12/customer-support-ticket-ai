# Customer Support Ticket AI System

This repository contains a full-stack AI system designed to analyze customer support tickets, answer natural language questions about them, and detect anomalous patterns.

## Project Features
- **Natural Language Data Querying**: Talk to your dataset using natural language to extract insights without writing SQL or Python code.
- **Automated Anomaly Detection**: Identifies unusual tickets using both heuristic rules (e.g., unresolved critical tickets older than 24h) and statistical/Machine Learning methods (Isolation Forest for abnormally long resolution times).
- **Minimal User Interface**: Streamlit-based frontend for easy interaction with the data, asking questions, and displaying detected anomalies.
- **RESTful API Backend**: Scalable FastAPI backend exposing endpoints for all core functionalities.

## Architecture Diagram

```text
+-------------------+        +-----------------------------------+
|                   |        |                                   |
|   Streamlit UI    | <----> |          FastAPI Backend          |
|    (app.py)       |  HTTP  |             (main.py)             |
|                   |        |                                   |
+-------------------+        +-----------------------------------+
                                    |                   |
                              +-----------+       +---------------+
                              | LangChain |       | Scikit-Learn  |
                              | & Ollama  |       | & Pandas      |
                              | (LLM)     |       | (Anomalies)   |
                              +-----------+       +---------------+
                                    |                   |
                             +-----------------------------------+
                             |                                   |
                             |      support_tickets.csv          |
                             |                                   |
                             +-----------------------------------+
```

## Project Folder Structure

```text
.
├── README.md                # Project documentation
├── app.py                   # Streamlit Frontend UI
├── main.py                  # FastAPI Backend entry point
├── requirements.txt         # Python dependencies
├── start.py                 # Single-command execution script
├── support_tickets.csv      # Dataset (ensure it's in the root)
└── src/                     # Core application source code
    ├── api/
    │   └── routes.py        # REST API endpoints definition
    ├── services/
    │   ├── anomaly_detector.py # Isolation Forest and heuristic rules
    │   ├── data_loader.py      # Pandas CSV loading and preprocessing
    │   └── llm_service.py      # LangChain Pandas DataFrame agent
    └── utils/
        └── config.py        # Pydantic configuration settings
```

## REST API Endpoints

### 1. Health Check
- **Endpoint**: `GET /health`
- **Description**: Verifies if the service is running.
- **Response Example**:
  ```json
  {
    "status": "ok",
    "message": "Service is running"
  }
  ```

### 2. Natural Language Query
- **Endpoint**: `POST /query`
- **Description**: Executes a natural language query against the dataset.
- **Request Example**:
  ```json
  {
    "query": "How many tickets are currently open?"
  }
  ```
- **Response Example**:
  ```json
  {
    "query": "How many tickets are currently open?",
    "answer": "There are 15 tickets currently open."
  }
  ```

### 3. Anomaly Detection
- **Endpoint**: `GET /anomalies`
- **Description**: Detects anomalous tickets based on heuristics and ML.
- **Response Example**:
  ```json
  {
    "count": 2,
    "anomalies": [
      {
        "ticket_id": "T123",
        "type": "Heuristic",
        "reason": "Unresolved high-priority ticket older than 24 hours",
        "details": "Priority: Critical, Age: 26.5 hrs"
      },
      {
        "ticket_id": "T456",
        "type": "Statistical",
        "reason": "Abnormally long resolution time",
        "details": "Resolution time: 140 hrs"
      }
    ]
  }
  ```

## Setup Instructions

### Prerequisites
1. Install [Ollama](https://ollama.com/) and pull the required model:
   ```bash
   ollama run llama3.2
   ```
2. Install Python 3.9+.

### Installation
1. Clone this repository or extract the files.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure `support_tickets.csv` is in the root directory.

### Running the System (Single-Command Execution)
You can start both the FastAPI backend and Streamlit frontend using a single command:
```bash
python start.py
```
This script runs both services simultaneously in the same terminal and gracefully handles shutdown (Ctrl+C).

- **API Docs (Swagger)**: `http://localhost:8000/docs`
- **Streamlit UI**: `http://localhost:8501`

*Alternatively, you can run them manually in separate terminals:*
- Backend: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Frontend: `streamlit run app.py`

## Technologies Used
- **Python**: Core programming language.
- **FastAPI**: Backend REST API framework.
- **Streamlit**: Minimal UI frontend.
- **LangChain & Pandas**: For translating natural language queries to data operations.
- **Scikit-Learn**: For Isolation Forest anomaly detection.

## Model Details (Ollama + llama3.2)
- **Local LLM**: Uses `llama3.2` running via Ollama locally on port `11434`.
- **Zero Cost & Privacy**: Since the model runs locally, no data is sent to external APIs (like OpenAI), ensuring data privacy and zero usage costs.
- **Agent Configuration**: Uses LangChain's `create_pandas_dataframe_agent` with temperature set to `0` for deterministic outputs.

## Dataset Overview
The system expects a CSV file named `support_tickets.csv` in the root directory. The dataset should contain records of customer support tickets with columns including `ticket_id`, `created_at`, `priority` (e.g., High, Critical), `status` (e.g., Open, Escalated, Closed), `category`, and `resolution_time_hrs`. 
During loading, categorical columns are optimized, and timestamps are parsed into datetime objects.

## Example Queries and Expected Output (Indicative)
- **"How many tickets are currently open?"**
  - *Output*: "There are X tickets currently open."
- **"Which agent resolved the most tickets this month?"**
  - *Output*: "Agent AGT-04 resolved the most tickets."
- **"What is the average customer rating for Technical category tickets?"**
  - *Output*: "The average customer rating for Technical tickets is 3.5."

## Error Handling
- The FastAPI application uses global exception handling blocks (`try...except`) in route definitions.
- If an internal process fails (e.g., the LLM cannot parse the query, or pandas encounters an error), the error is logged internally, and an HTTP `500 Internal Server Error` is raised containing the specific error details in the response body.
- The LLM service is configured with `handle_parsing_errors=True` to help the agent recover from its own output formatting mistakes.

## Assumptions
- The dataset file is named `support_tickets.csv` and is located in the project's root folder.
- For the heuristic anomaly detection (unresolved tickets > 24 hours old), the system assumes "now" is the maximum `created_at` timestamp in the dataset to simulate real-time operations on static data.
- Ollama is running and accessible at `http://localhost:11434`.

## Scalability Considerations
- **Memory Consumption**: Currently, the entire dataset is loaded into RAM using Pandas. For production systems with millions of rows, this approach becomes a bottleneck.
- **Concurrent Requests**: The local LLM (Ollama) may struggle to process multiple concurrent natural language queries rapidly compared to cloud-hosted endpoints.

## Known Limitations
- **LLM Code Execution Risks**: The LangChain Pandas agent uses `eval()`/`exec()` internally. It is configured with `allow_dangerous_code=True`. This is acceptable for a local sandbox prototype, but in a true production environment, queries should run in a heavily sandboxed environment or use a text-to-SQL approach on a read-only database.
- **Model Hallucinations**: Local models with smaller parameter counts (like `llama3.2` 3B) can sometimes write invalid Pandas code resulting in query errors. Using larger models (e.g., `llama3.1:8b`) increases reliability.
- **Memory Limits**: As mentioned, the entire dataset is loaded into RAM.

## Future Improvements
- **Database Integration**: Replace the static CSV and Pandas agent with a robust SQL database (e.g., PostgreSQL) and LangChain's SQL Agent for better performance and scalability.
- **Dockerization**: Containerize both the frontend and backend using Docker and `docker-compose` for easier deployment.
- **Authentication**: Add JWT-based authentication to the FastAPI endpoints to secure data access.
- **Enhanced UI**: Migrate from Streamlit to a fully custom React/Next.js frontend for advanced visualization capabilities.
