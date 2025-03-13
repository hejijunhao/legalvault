# test_perplexity.py
import asyncio
import os
from uuid import uuid4
from dotenv import load_dotenv
from models.domain.research.search import ResearchSearch

# Load environment variables from .env file
load_dotenv()

async def test_search():
    # Verify API key is available
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        print("Error: PERPLEXITY_API_KEY not found in environment variables.")
        print("Make sure you have added it to your .env file.")
        return
    
    # Create a search instance
    search = ResearchSearch(user_id=uuid4(), enterprise_id=uuid4())
    
    # Define the system prompt for legal research
    system_prompt = "Provide a concise, accurate, and legally relevant response to the query, prioritizing authoritative sources such as case law, statutes, and reputable legal commentary, tailored to the needs of a practicing lawyer."
    
    # Test initial query
    print("Testing initial query...")
    initial_query = "What are the key elements of a valid contract?"
    
    # Create initial messages array with system prompt and user query
    initial_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_query}
    ]
    
    # Call the API with the initial messages
    # Note: We're bypassing start_search to directly test the API call
    payload = {
        "model": "sonar-pro",
        "messages": initial_messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    print(f"Sending initial payload with {len(initial_messages)} messages")
    initial_response = await search._call_perplexity_api(payload)
    
    if "error" in initial_response:
        print(f"Error in initial query: {initial_response['error']}")
        return
    
    # Extract the assistant's response
    assistant_response = initial_response["choices"][0]["message"]["content"]
    print(f"\nInitial response received:")
    print(f"Text: {assistant_response[:200]}...")
    
    # Add a delay before the follow-up query to avoid rate limiting
    print("\nWaiting 3 seconds before follow-up query...")
    await asyncio.sleep(3)
    
    # Test follow-up query
    print("Testing follow-up query...")
    follow_up_query = "How does consideration differ between common law and civil law systems?"
    
    # Create follow-up messages array with the complete conversation history
    follow_up_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_query},
        {"role": "assistant", "content": assistant_response},
        {"role": "user", "content": follow_up_query}
    ]
    
    # Create the follow-up payload
    follow_up_payload = {
        "model": "sonar-pro",
        "messages": follow_up_messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    print(f"Sending follow-up payload with {len(follow_up_messages)} messages")
    print(f"Follow-up query: {follow_up_query}")
    
    try:
        follow_up_response = await search._call_perplexity_api(follow_up_payload)
        
        if "error" in follow_up_response:
            print(f"Error in follow-up query: {follow_up_response['error']}")
            return
        
        # Extract the assistant's response to the follow-up
        follow_up_assistant_response = follow_up_response["choices"][0]["message"]["content"]
        print(f"\nFollow-up response received:")
        print(f"Text: {follow_up_assistant_response[:200]}...")
        
        # Extract citations if available
        if "citations" in follow_up_response:
            print(f"Citations: {follow_up_response['citations']}")
        else:
            print("No citations provided in the response.")
            
    except Exception as e:
        print(f"Exception during follow-up query: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_search())