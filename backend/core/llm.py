from langchain.llms import HuggingFaceHub
from langchain.callbacks import BaseCallbacks
from dotenv import load_dotenv
import os

load_dotenv()

def init_llm():
    return HuggingFaceHub(
        huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN"),
        repo_id="google/flan-t5-base"  # or your preferred model
    )