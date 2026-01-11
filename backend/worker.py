import os
import sys
from celery import Celery


celery_app = Celery(
    "docs_agent",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    
    worker_pool="threads" if sys.platform == "win32" else "prefork",
)