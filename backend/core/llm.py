# core/llm.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(model_name="gpt-3.5-turbo")