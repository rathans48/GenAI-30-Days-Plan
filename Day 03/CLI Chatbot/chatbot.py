import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from your environment file
load_dotenv(".env")  # Swap to "config.env" if you kept that name

# OpenRouter acts as an OpenAI-compatible gateway
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def stream_free_router(prompt):
    print("\n--- OpenRouter Free Gateway Streaming ---")
    try:
        stream = client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            extra_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "GenAI 30 Day Study Plan",
            }
        )
        
        for chunk in stream:
            # 1. Standard OpenAI layout check
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                content = getattr(delta, 'content', None)
                if content:
                    print(content, end="", flush=True)
                    continue
            
            # 2. OpenRouter fallback layout check
            if hasattr(chunk, 'text'):
                print(chunk.text, end="", flush=True)
                
        print("\n")
    except Exception as e:
        print(f"\nGateway Connection Error: {e}\n")

if __name__ == "__main__":
    print("Welcome to your Fail-Safe GenAI CLI Chatbot!")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_prompt = input("You: ")
        if user_prompt.lower() == 'exit':
            break
            
        stream_free_router(user_prompt)