from langchain.callbacks import BaseCallbacks
from datetime import datetime


class WorkflowTracker(BaseCallbacks):
    def __init__(self):
        self.steps = []

    def on_llm_start(self, *args, **kwargs):
        self.steps.append({
            "type": "LLM",
            "status": "started",
            "timestamp": str(datetime.now())
        })

    def on_llm_end(self, *args, **kwargs):
        self.steps.append({
            "type": "LLM",
            "status": "completed",
            "timestamp": str(datetime.now())
        })