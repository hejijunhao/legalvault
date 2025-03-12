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
    
    # Test initial query
    print("Testing initial query...")
    result = await search.start_search("What are the key elements of a valid contract?")
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Thread ID: {result['thread_id']}")
    print(f"Text: {result['text'][:200]}...")
    print(f"Citations: {result['citations']}")
    
    # Add a delay before the follow-up query to avoid rate limiting
    print("\nWaiting 3 seconds before follow-up query...")
    await asyncio.sleep(3)
    
    # Test follow-up query
    print("Testing follow-up query...")
    # Create a messages array with the previous conversation
    # Note: Perplexity might expect a specific format for messages
    previous_messages = [
        {
            "role": "system",
            "content": "Provide a concise, accurate, and legally relevant response to the query, prioritizing authoritative sources such as case law, statutes, and reputable legal commentary, tailored to the needs of a practicing lawyer."
        },
        {
            "role": "user",
            "content": "What are the key elements of a valid contract?"
        },
        {
            "role": "assistant",
            "content": result['text']
        }
    ]
    
    print(f"Using previous_messages with {len(previous_messages)} messages")
    
    try:
        follow_up = await search.continue_search(
            "How does consideration differ between common law and civil law systems?",
            previous_messages=previous_messages
        )
        
        if "error" in follow_up:
            print(f"Error: {follow_up['error']}")
            return
        
        print(f"Thread ID: {follow_up['thread_id']}")
        print(f"Text: {follow_up['text'][:200]}...")
        print(f"Citations: {follow_up['citations']}")
    except Exception as e:
        print(f"Exception during follow-up query: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_search())