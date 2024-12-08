from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.llm import init_llm
from services.workflow_tracker import WorkflowTracker

app = FastAPI()

# CORS setup for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = init_llm()


@app.post("/process")
async def process_text(data: dict):
    tracker = WorkflowTracker()

    # Process with LLM
    result = llm(data["text"], callbacks=[tracker])

    return {
        "result": result,
        "steps": tracker.steps
    }