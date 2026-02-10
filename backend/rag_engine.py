from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiEmbeddings(Embeddings):
    def __init__(self, model_name="models/gemini-embedding-001"):
        self.model_name = model_name
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

class RAGEngine:
    def __init__(self):
        print("Initializing RAGEngine...")
        try:
            self.embeddings = GeminiEmbeddings(model_name="models/gemini-embedding-001")
            print("Embeddings loaded (Custom GeminiEmbeddings).")
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
            print("LLM loaded.")
        except Exception as e:
            print(f"RAG Init Error: {e}")
            raise e
        self.vector_store = None

    def initialize_vector_store(self, chunks: list[str]):
        """Create a local FAISS vector store from text chunks."""
        self.vector_store = FAISS.from_texts(chunks, self.embeddings)

    def get_answer(self, question: str) -> str:
        """Retrieve relevant context and answer the question using Gemini."""
        if not self.vector_store:
            return "Error: Document not processed yet."

        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        template = """
        You are a professional AI document analyst for "GlobalDoc AI".
        Answer the question ONLY using the provided context from the uploaded document.
        
        Strict Guardrails:
        1. If the answer is not present in the context, respond strictly with: "I could not find this information in the uploaded document."
        2. Do NOT hallucinate or use outside knowledge.
        3. Keep the response clear, professional, and well-structured.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain.invoke(question)
