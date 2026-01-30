import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agent7_qa_rag import qa_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_qa_rotation():
    print("Testing QA System with Key Rotation...")
    
    # Mock context documents
    context_docs = [
        {
            'document': "Reliance Industries reported a net profit of ₹19,299 crore for Q3 FY24, up 11% YoY. Revenue stood at ₹2.28 lakh crore.",
            'metadata': {'source': 'test_doc_1'},
            'similarity_score': 0.9
        }
    ]
    
    query = "What was Reliance's net profit in Q3 FY24?"
    print(f"\nQuery: {query}")
    
    # Call generate_answer
    # Note: generate_answer is synchronous in the class, but we are running in async context
    # The method itself doesn't use await for gemini call (it uses synchronous client), so we can call it directly
    result = qa_system.generate_answer(query, context_docs)
    
    print("\nResult:")
    print(f"Success: {result.get('success')}")
    print(f"Answer: {result.get('answer')}")
    print(f"Sentiment: {result.get('sentiment')}")
    
    if result.get('success') and "19,299" in result.get('answer'):
        print("\nSUCCESS: QA System generated correct answer.")
    else:
        print("\nFAILURE: QA System failed to generate correct answer.")

if __name__ == "__main__":
    asyncio.run(test_qa_rotation())
