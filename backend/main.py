from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.database import supabase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/virtual-paralegals")
async def list_paralegals():
    response = supabase.table('virtual_paralegals').select("*").execute()
    return response.data

@app.post("/virtual-paralegals")
async def create_paralegal(name: str):
    response = supabase.table('virtual_paralegals').insert({"name": name}).execute()
    return response.data