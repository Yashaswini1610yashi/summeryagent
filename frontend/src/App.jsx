import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, MessageSquare, FileText, Globe, Send, Loader2, Sparkles, ChevronRight, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

function App() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [summary, setSummary] = useState(null);
    const [chat, setChat] = useState([]);
    const [question, setQuestion] = useState('');
    const [mode, setMode] = useState('Detailed Summary');
    const [language, setLanguage] = useState('English');
    const [metadata, setMetadata] = useState(null);

    const fileInputRef = useRef();

    const handleUpload = async (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        setFile(selectedFile);
        setLoading(true);

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const res = await axios.post(`${API_BASE}/upload`, formData);
            setSummary(res.data.summary);
            setMetadata(res.data.metadata);
            setChat([{ type: 'bot', text: `Hello! I've analyzed "${selectedFile.name}". How can I help you understand it better?` }]);
        } catch (err) {
            console.error(err);
            alert('Error uploading file. Make sure the backend is running and valid.');
        } finally {
            setLoading(false);
        }
    };

    const handleSummarize = async () => {
        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE}/summarize`, { mode, language });
            setSummary(res.data.summary);
        } catch (err) {
            alert('Error regenerating summary.');
        } finally {
            setLoading(false);
        }
    };

    const handleAsk = async (e) => {
        e.preventDefault();
        if (!question.trim()) return;

        const userMessage = { type: 'user', text: question };
        setChat(prev => [...prev, userMessage]);
        setQuestion('');

        try {
            const res = await axios.post(`${API_BASE}/chat`, { question });
            setChat(prev => [...prev, { type: 'bot', text: res.data.answer }]);
        } catch (err) {
            setChat(prev => [...prev, { type: 'bot', text: 'Sorry, I encountered an error processing your query.' }]);
        }
    };

    return (
        <div className="app-container">
            <main className="main-content">
                <header style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Sparkles className="accent" size={32} />
                        <h1 className="gradient-text">GlobalDoc AI</h1>
                    </div>
                    <p>Your professional multilingual document assistant.</p>
                </header>

                {!summary && !loading && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="upload-zone glass-card"
                        onClick={() => fileInputRef.current.click()}
                    >
                        <div style={{ background: 'rgba(37, 99, 235, 0.1)', padding: '1.5rem', borderRadius: '50%' }}>
                            <Upload size={48} color="#2563eb" />
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <h2>Upload Document</h2>
                            <p>Drag and drop your PDF here or click to browse</p>
                            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                                <span style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem', background: 'var(--bg-input)', borderRadius: '4px' }}>PDF only</span>
                                <span style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem', background: 'var(--bg-input)', borderRadius: '4px' }}>Any Language</span>
                            </div>
                        </div>
                        <input
                            type="file"
                            ref={fileInputRef}
                            hidden
                            accept=".pdf"
                            onChange={handleUpload}
                        />
                    </motion.div>
                )}

                {loading && (
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
                        <Loader2 className="animate-spin" size={48} color="#2563eb" />
                        <h2 style={{ color: 'var(--accent)' }}>Analyzing Document...</h2>
                        <p>Extracting text, detecting language, and generating insights.</p>
                    </div>
                )}

                <AnimatePresence>
                    {summary && !loading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="animate-fade-in"
                        >
                            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <FileText color="var(--accent)" />
                                        <h2 style={{ margin: 0 }}>Document Summary</h2>
                                    </div>
                                    <div style={{ display: 'flex', gap: '1rem' }}>
                                        <select value={mode} onChange={(e) => setMode(e.target.value)} style={{ width: 'auto' }}>
                                            <option>Short Summary</option>
                                            <option>Detailed Summary</option>
                                            <option>Bullet Points</option>
                                            <option>Explain Like I’m 5</option>
                                        </select>
                                        <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ width: 'auto' }}>
                                            <option>English</option>
                                            <option>Spanish</option>
                                            <option>Hindi</option>
                                            <option>French</option>
                                            <option>German</option>
                                            <option>Chinese</option>
                                        </select>
                                        <button onClick={handleSummarize} className="btn-primary">
                                            Apply
                                        </button>
                                    </div>
                                </div>

                                <div className="summary-content" style={{ whiteSpace: 'pre-wrap', color: 'var(--text-main)' }}>
                                    {summary}
                                </div>

                                <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                                        <Globe size={16} color="var(--text-muted)" />
                                        <span style={{ color: 'var(--text-muted)' }}>Detected: </span>
                                        <span style={{ color: 'var(--success)', fontWeight: 600 }}>{metadata?.detected_language?.toUpperCase() || 'UNKNOWN'}</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                                        <CheckCircle2 size={16} color="var(--success)" />
                                        <span style={{ color: 'var(--text-muted)' }}>Chunks Processed: </span>
                                        <span style={{ fontWeight: 600 }}>{metadata?.num_chunks}</span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

            <aside className="sidebar">
                <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <MessageSquare size={20} color="var(--accent)" />
                    <h3 style={{ margin: 0 }}>Smart Analyst Chat</h3>
                </div>

                <div className="chat-messages">
                    {chat.map((msg, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: msg.type === 'user' ? 20 : -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`message ${msg.type}`}
                        >
                            {msg.text}
                        </motion.div>
                    ))}
                    {chat.length === 0 && (
                        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                            <Sparkles size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                            <p>Upload a document to start chatting with the professional analyst.</p>
                        </div>
                    )}
                </div>

                <form className="chat-input" onSubmit={handleAsk}>
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder={summary ? "Ask about the document..." : "Upload a PDF first"}
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            disabled={!summary || loading}
                        />
                        <button type="submit" className="btn-primary" disabled={!summary || loading} style={{ padding: '0.75rem' }}>
                            <Send size={20} />
                        </button>
                    </div>
                </form>
            </aside>
        </div>
    );
}

export default App;
