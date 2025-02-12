# tests/llm/test_langchain.py

import pytest
from core.llm import llm
from langchain_core.messages import HumanMessage

def test_llm_response():
    messages = [HumanMessage(content="Hello, how are you?")]
    response = llm.invoke(messages)
    assert response.content.strip() != "", "Response should not be empty"
    print("LLM response:", response.content)