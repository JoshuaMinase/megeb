import httpx
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

async def test_groq():
    print("Testing GROQ API connection...")
    print(f"API Key (first 10 chars): {GROQ_API_KEY[:10]}...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': [{'role': 'user', 'content': 'Hello'}],
                    'temperature': 0.7
                }
            )
            print('Status:', resp.status_code)
            if resp.status_code == 200:
                print('SUCCESS: GROQ API is working correctly')
                data = resp.json()
                print('Response:', data.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100])
            else:
                print('ERROR: GROQ API returned status', resp.status_code)
                print('Response:', resp.text[:200])
    except Exception as e:
        print('ERROR: Connection error:', str(e))

if __name__ == "__main__":
    asyncio.run(test_groq())