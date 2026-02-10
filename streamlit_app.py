import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Add backend to path to import logic
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from processor import DocProcessor
from rag_engine import RAGEngine
from summarizer import Summarizer

load_dotenv()

# Page Config
st.set_page_config(
    page_title="GlobalDoc AI - Professional Document Analyst",
    page_icon="📄",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #2563eb;
        color: white;
    }
    .stSelectbox {
        border-radius: 8px;
    }
    .chat-msg {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .user-msg {
        background-color: #e2e8f0;
        text-align: right;
    }
    .bot-msg {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services
@st.cache_resource
def get_services():
    return DocProcessor(), RAGEngine(), Summarizer()

try:
    processor, rag, summarizer = get_services()
except Exception as e:
    st.error(f"Error initializing AI services: {e}")
    st.stop()

# Session State
if 'current_text' not in st.session_state:
    st.session_state.current_text = None
if 'metadata' not in st.session_state:
    st.session_state.metadata = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    summary_mode = st.selectbox(
        "Summary Mode",
        ["Short Summary", "Detailed Summary", "Bullet Points", "Explain Like I’m 5"],
        index=1
    )
    target_lang = st.selectbox(
        "Language",
        ["English", "Spanish", "Hindi", "French", "German", "Chinese"],
        index=0
    )
    
    if st.button("Regenerate Summary") and st.session_state.current_text:
        with st.spinner("Updating summary..."):
            st.session_state.summary = summarizer.generate_summary(
                st.session_state.current_text,
                mode=summary_mode,
                target_lang=target_lang
            )

# Main UI
st.title("🚀 GlobalDoc AI")
st.subheader("Your professional multilingual document assistant.")

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file and (st.session_state.metadata is None or st.session_state.metadata["filename"] != uploaded_file.name):
    with st.spinner("Analyzing document..."):
        # Save temp file
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            results = processor.process_document(temp_path)
            st.session_state.current_text = results["text"]
            st.session_state.metadata = {
                "filename": uploaded_file.name,
                "detected_language": results["language"],
                "num_chunks": results["num_chunks"]
            }
            
            # Initialize RAG
            rag.initialize_vector_store(results["chunks"])
            
            # Initial Summary
            st.session_state.summary = summarizer.generate_summary(
                st.session_state.current_text,
                mode=summary_mode,
                target_lang=target_lang
            )
            
            # Initial chat greeting
            st.session_state.chat_history = [
                {"role": "assistant", "content": f"Hello! I've analyzed '{uploaded_file.name}'. I detected that it's primarily in {results['language'].upper()}. How can I help you understand it better?"}
            ]
            
        except Exception as e:
            st.error(f"Error processing document: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

# Dashboard Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Document Summary")
    if st.session_state.summary:
        st.markdown(st.session_state.summary)
        
        # Metadata display
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Detected Language", st.session_state.metadata["detected_language"].upper())
        m2.metric("Chunks Processed", st.session_state.metadata["num_chunks"])
    else:
        st.info("Upload a document to see the analysis.")

with col2:
    st.header("💬 Smart Analyst Chat")
    
    # Chat display
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the document..."):
        if not st.session_state.current_text:
            st.warning("Please upload a document first.")
        else:
            # Display user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = rag.get_answer(prompt)
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

st.markdown("---")
st.caption("Powered by GlobalDoc AI & Gemini 1.5 Flash")
