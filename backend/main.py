from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import traceback
from dotenv import load_dotenv

from processor import DocProcessor
from rag_engine import RAGEngine
from summarizer import Summarizer

load_dotenv()

app = FastAPI(title="GlobalDoc AI API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state (In a production app, use Redis or a DB with session IDs)
# For this scratchpad version, we'll maintain state for the last uploaded doc
class SessionState:
    def __init__(self):
        print("Initializing SessionState...")
        try:
            self.processor = DocProcessor()
            print("Processor OK.")
            self.rag = RAGEngine()
            print("RAG Engine OK.")
            self.summarizer = Summarizer()
            print("Summarizer OK.")
        except Exception as e:
            print(f"Error initializing services: {e}")
            traceback.print_exc()
        self.current_text = ""
        self.document_metadata = {}

state = SessionState()

class ChatRequest(BaseModel):
    question: str

class SummarizeRequest(BaseModel):
    mode: str = "Detailed Summary"
    language: str = "English"

@app.get("/")
async def root():
    return {"message": "GlobalDoc AI API is running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Save file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process document
        results = state.processor.process_document(temp_path)
        state.current_text = results["text"]
        state.document_metadata = {
            "filename": file.filename,
            "detected_language": results["language"],
            "num_chunks": results["num_chunks"]
        }
        
        # Initialize RAG
        state.rag.initialize_vector_store(results["chunks"])
        
        # Generate initial summary
        initial_summary = state.summarizer.generate_summary(state.current_text)
        
        return {
            "metadata": state.document_metadata,
            "summary": initial_summary,
            "status": "success"
        }
    except Exception as e:
        print("UPLOAD ERROR:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/chat")
async def chat_with_doc(request: ChatRequest):
    if not state.current_text:
        raise HTTPException(status_code=400, detail="No document uploaded yet.")
    
    answer = state.rag.get_answer(request.question)
    return {"answer": answer}

@app.post("/summarize")
async def update_summary(request: SummarizeRequest):
    if not state.current_text:
        raise HTTPException(status_code=400, detail="No document uploaded yet.")
    
    summary = state.summarizer.generate_summary(
        state.current_text, 
        mode=request.mode, 
        target_lang=request.language
    )
    return {"summary": summary}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
