
from dotenv import load_dotenv
import os
import traceback
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
print(f"API Key found: '{api_key}'") # Print clearly with quotes

if not api_key:
    print("API Key not found!")
    exit(1)

try:
    print("Attempting to initialize ChatGoogleGenerativeAI...")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    print("Invoking model...")
    response = llm.invoke("Hello, simple test.")
    print("API Call Successful!")
    print(response.content)
except Exception:
    print("API Call Failed:")
    traceback.print_exc()
