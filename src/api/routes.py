import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.llm_service import llm_service
from src.services.anomaly_detector import anomaly_detector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}

@router.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest):
    try:
        logger.info(f"Received query: {request.query}")
        answer = llm_service.query(request.query)
        logger.info("Query executed successfully.")
        return QueryResponse(query=request.query, answer=answer)
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies")
def get_anomalies():
    try:
        logger.info("Running anomaly detection...")
        anomalies = anomaly_detector.detect_anomalies()
        logger.info(f"Anomaly detection complete. Found {len(anomalies)} anomalies.")
        return {"count": len(anomalies), "anomalies": anomalies}
    except Exception as e:
        logger.error(f"Error during anomaly detection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
