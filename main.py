from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="Customer Support Ticket AI System",
    description="AI-powered API to query customer support tickets and detect anomalies.",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
