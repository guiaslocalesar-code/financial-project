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
async def run_workflow_get(background_tasks: BackgroundTasks):
    """
    Trigger the migration workflow asynchronously for both Posts and Stories.
    Returns immediately while the tasks run in the background.
    """
    logger.info("Metricool workflow requested via GET (Posts & Stories).")
    
    # Trigger Posts
    background_tasks.add_task(workflow_logic.run_workflow, sheet_name="planificacion_data", publication_type="POST")
    # Trigger Stories
    background_tasks.add_task(workflow_logic.run_workflow, sheet_name=config.STORIES_SHEET_NAME, publication_type="STORY")
    
    return {"message": "Workflows for Posts and Stories started in background."}

@app.post("/run")
async def run_workflow_post(background_tasks: BackgroundTasks):
    """Same as GET /run but for POST requests from Scheduler."""
    logger.info("Metricool workflow requested via POST (Posts & Stories).")
    
    # Trigger Posts
    background_tasks.add_task(workflow_logic.run_workflow, sheet_name="planificacion_data", publication_type="POST")
    # Trigger Stories
    background_tasks.add_task(workflow_logic.run_workflow, sheet_name=config.STORIES_SHEET_NAME, publication_type="STORY")
    
    return {"message": "Workflows for Posts and Stories started in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
