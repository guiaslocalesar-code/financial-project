import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from app.core.workflow_logic import workflow_logic
from app.config import logger

app = FastAPI(title="Metricool Publisher GCP")

# Setup cloud logging if enabled
try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
except Exception:
    logger.info("Using standard local logging.")

@app.get("/")
async def root():
    return {"message": "Metricool Publisher API is active"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/run")
async def run_workflow(background_tasks: BackgroundTasks):
    """
    Trigger the migration workflow asynchronously.
    Returns immediately while the task runs in the background.
    """
    logger.info("Metricool workflow requested.")
    # In Cloud Run, requests have a timeout. 
    # For many items, it's safer to run in background.
    background_tasks.add_task(workflow_logic.run_migration)
    return {"message": "Workflow started in background."}

@app.post("/run")
async def run_workflow_post(background_tasks: BackgroundTasks):
    """Same as GET /run but for POST requests from Scheduler."""
    background_tasks.add_task(workflow_logic.run_migration)
    return {"message": "Workflow started in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
