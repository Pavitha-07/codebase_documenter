from fastapi import FastAPI
from pydantic import BaseModel
from tasks import analyze_repo_task
from celery.result import AsyncResult

app = FastAPI()

class RepoRequest(BaseModel):
    url: str

@app.post("/analyze")
async def analyze_repo(request: RepoRequest):
    task = analyze_repo_task.delay(request.url)
    
    return {"task_id": task.id, "message": "Analysis started"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else str(task_result.info)
    }
    return response