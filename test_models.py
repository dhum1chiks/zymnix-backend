"""
Quick script to test which Groq models are currently available.
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Try different model names
models_to_try = [
    "gemma2-9b-it",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-groq-70b-8192-tool-use-preview",
]

for model in models_to_try:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        print(f"✅ {model} - WORKS")
        print(f"   Model used: {completion.model}")
        break
    except Exception as e:
        print(f"❌ {model} - FAILED: {str(e)[:100]}")
