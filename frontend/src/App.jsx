import React, { useState, useEffect, useRef } from 'react';
import { Upload, MessageSquare, Send, FileText, Database, Settings, Loader2, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

// Simple logger that forwards to backend
const logToBackend = async (level, message) => {
  try {
    await fetch('/api/v1/client-log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ level, message })
    });
  } catch (e) {
    console.error('Failed to send log to backend:', e);
  }
};

const overrideConsole = () => {
  const originalError = console.error;
  const originalWarn = console.warn;
  const originalInfo = console.info;

  console.error = (...args) => {
    originalError(...args);
    logToBackend('error', args.join(' '));
  };
  console.warn = (...args) => {
    originalWarn(...args);
    logToBackend('warning', args.join(' '));
  };
  console.info = (...args) => {
    originalInfo(...args);
    logToBackend('info', args.join(' '));
  };
};

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am the Project Intelligence Assistant. Upload some project documents (PDF, CSV, Excel) and ask me questions.' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const messagesEndRef = useRef(null);
  
  // Setup logging once
  useEffect(() => {
    overrideConsole();
    console.info("Frontend application started.");
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      console.info(`Sending chat query: ${input}`);
      // In Vite, /api is proxied to backend via vite.config.js
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input, chat_history: messages })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response,
        sources: data.sources
      }]);
    } catch (error) {
      console.error(`Chat error: ${error.message}`);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Sorry, I encountered an error: ${error.message}` 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus({ type: 'info', msg: `Uploading ${file.name}...` });
    console.info(`Initiating upload for: ${file.name}`);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload failed with status ${response.status}`);
      }

      setUploadStatus({ type: 'success', msg: `${file.name} uploaded and indexed successfully!` });
      console.info(`Upload successful: ${file.name}`);
      setTimeout(() => setUploadStatus(null), 3000);
    } catch (error) {
      console.error(`Upload error: ${error.message}`);
      setUploadStatus({ type: 'error', msg: `Error: ${error.message}` });
    } finally {
      setIsUploading(false);
      e.target.value = null; // Reset input
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-200 overflow-hidden font-sans">
      
      {/* Sidebar */}
      <div className="w-80 bg-[#1e293b] border-r border-slate-700/50 flex flex-col glassmorphism shadow-2xl z-10 relative">
        <div className="p-6 border-b border-slate-700/50 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Database className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">Project Intelligence</h1>
            <p className="text-xs text-slate-400 font-medium">AI Assistant</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          
          <div>
            <h2 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-3 flex items-center gap-2">
              <Settings className="w-3 h-3" /> System Status
            </h2>
            <div className="bg-[#0f172a]/50 p-4 rounded-xl border border-slate-700/50 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Multi-Agent System</span>
                <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div> Online
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Vector Store</span>
                <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div> Local
                </span>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-3 flex items-center gap-2">
              <Upload className="w-3 h-3" /> Document Ingestion
            </h2>
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative flex flex-col items-center justify-center border-2 border-dashed border-slate-600/60 rounded-xl p-6 bg-[#1e293b] hover:bg-[#253347] transition-all cursor-pointer">
                <input 
                  type="file" 
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  accept=".pdf,.csv,.xlsx"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                />
                {isUploading ? (
                  <Loader2 className="w-8 h-8 text-blue-400 animate-spin mb-2" />
                ) : (
                  <Upload className="w-8 h-8 text-slate-400 mb-2 group-hover:text-blue-400 transition-colors" />
                )}
                <p className="text-sm font-medium text-center text-slate-300">
                  {isUploading ? 'Processing...' : 'Upload PDF, CSV, Excel'}
                </p>
                <p className="text-xs text-slate-500 mt-1 text-center">Drag & drop or click</p>
              </div>
            </div>

            {uploadStatus && (
              <div className={`mt-3 p-3 rounded-lg text-sm flex items-start gap-2 animate-in fade-in slide-in-from-top-2 ${
                uploadStatus.type === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                uploadStatus.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                'bg-blue-500/10 text-blue-400 border border-blue-500/20'
              }`}>
                {uploadStatus.type === 'error' && <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />}
                <span>{uploadStatus.msg}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative z-0">
        
        {/* Abstract Background Design */}
        <div className="absolute top-0 left-0 w-full h-96 bg-blue-600/5 blur-[120px] rounded-full pointer-events-none transform -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-indigo-600/5 blur-[120px] rounded-full pointer-events-none transform translate-y-1/4"></div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 relative z-10 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
              <div className={`max-w-3xl flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                
                {/* Avatar */}
                <div className={`w-10 h-10 shrink-0 rounded-2xl flex items-center justify-center shadow-lg ${
                  msg.role === 'user' 
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-600 shadow-blue-500/20' 
                    : 'bg-slate-800 border border-slate-700 shadow-slate-900/50'
                }`}>
                  {msg.role === 'user' ? (
                    <MessageSquare className="w-5 h-5 text-white" />
                  ) : (
                    <Database className="w-5 h-5 text-blue-400" />
                  )}
                </div>

                {/* Message Bubble */}
                <div className={`flex flex-col gap-2 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`px-6 py-4 rounded-3xl shadow-xl ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-sm' 
                      : 'bg-slate-800/80 backdrop-blur-md border border-slate-700/50 text-slate-200 rounded-tl-sm'
                  }`}>
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>

                  {/* Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-1 px-2">
                      {msg.sources.map((src, i) => (
                        <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 border border-slate-700 rounded-full text-xs text-slate-400 backdrop-blur-sm">
                          <FileText className="w-3 h-3 text-blue-400" />
                          <span>{src.source}</span>
                          {src.page && <span className="text-slate-500">p.{src.page}</span>}
                          {src.row && <span className="text-slate-500">row {src.row}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start animate-in fade-in">
              <div className="flex gap-4">
                <div className="w-10 h-10 shrink-0 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center shadow-lg">
                  <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                </div>
                <div className="px-6 py-4 rounded-3xl rounded-tl-sm bg-slate-800/80 backdrop-blur-md border border-slate-700/50 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce"></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-6 bg-gradient-to-t from-[#0f172a] via-[#0f172a] to-transparent relative z-10">
          <div className="max-w-4xl mx-auto relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-3xl blur opacity-20 group-hover:opacity-30 transition duration-500"></div>
            <div className="relative flex items-end gap-2 bg-[#1e293b] border border-slate-700/50 rounded-3xl p-2 shadow-2xl glassmorphism">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask about project risks, status, or financial data..."
                className="w-full max-h-32 min-h-[56px] bg-transparent text-slate-200 placeholder-slate-500 resize-none outline-none py-4 px-4 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700"
                rows="1"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isTyping}
                className="w-12 h-12 shrink-0 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-2xl flex items-center justify-center transition-all shadow-lg hover:shadow-blue-500/25 mb-1 mr-1"
              >
                <Send className="w-5 h-5 ml-1" />
              </button>
            </div>
          </div>
          <div className="text-center mt-3">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Gamuda Advanced AI Demo • Confidential</p>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;