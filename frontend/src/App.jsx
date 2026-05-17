import { useState, useRef, useEffect } from 'react'
import { Send, FileText, Bot, User, Loader2, Sparkles, Plus, Trash2 } from 'lucide-react'
import { motion } from 'framer-motion'
import ReactMarkdown from "react-markdown";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

function App() {
  const [messages, setMessages] = useState([
    { id: 1, role: 'ai', content: 'Welcome to Nexus RAG. Upload your knowledge base to begin.' }
  ])
  const [input, setInput] = useState('')
  const [files, setFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [isQuerying, setIsQuerying] = useState(false)
  const fileInputRef = useRef(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleFileUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files)
    if (selectedFiles.length === 0) return

    setIsUploading(true)
    const formData = new FormData()
    selectedFiles.forEach(file => formData.append('files', file))

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        setMessages(prev => [...prev, { id: Date.now(), role: 'ai', content: data.detail }])
        return
      }

      setFiles(prev => [...prev, ...selectedFiles.map(f => f.name)])
      setMessages(prev => [
        ...prev,
        { id: Date.now(), role: 'ai', content: `Success! Indexed ${selectedFiles.length} documents.` }
      ])

    } catch {
      setMessages(prev => [...prev, { id: Date.now(), role: 'ai', content: 'Upload failed.' }])
    } finally {
      setIsUploading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isQuerying) return

    const userMsg = { id: Date.now(), role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsQuerying(true)

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      })

      const data = await response.json()

      setMessages(prev => [
        ...prev,
        {
          id: Date.now(),
          role: 'ai',
          content: data.answer,
          sources: data.sources
        }
      ])

    } catch {
      setMessages(prev => [...prev, { id: Date.now(), role: 'ai', content: 'Error occurred.' }])
    } finally {
      setIsQuerying(false)
    }
  }

  const handleClear = async () => {
    await fetch(`${API_BASE_URL}/clear`, { method: 'POST' })
    setFiles([])
    setMessages(prev => [...prev, { id: Date.now(), role: 'ai', content: 'Knowledge base cleared.' }])
  }

  return (
    <div className="app-container">

      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="logo-section">
          <Sparkles size={28} color="#a855f7" />
          <span>Nexus RAG</span>
        </div>

        <div className="upload-section">
          <p>KNOWLEDGE BASE</p>

          <div className="upload-card" onClick={() => fileInputRef.current?.click()}>
            {isUploading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              >
                <Loader2 size={26} color="#a855f7" />
              </motion.div>
            ) : <Plus size={32} />}

            <span>{isUploading ? 'Indexing...' : 'Add Sources'}</span>

            <input type="file" multiple hidden ref={fileInputRef} onChange={handleFileUpload} />
          </div>

          {files.length > 0 && (
            <button onClick={handleClear} className="clear-btn">
              <Trash2 size={14}/> Clear Knowledge Base
            </button>
          )}
        </div>

        <div className="file-list-section">
          {files.map((file, i) => (
            <div key={i} className="file-item">
              <FileText size={16}/> {file}
            </div>
          ))}
        </div>
      </aside>

      {/* CHAT */}
      <main className="chat-section">
        <div className="messages-container" ref={scrollRef}>
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.role}`}>

              <div style={{ display:'flex', gap:'10px', alignItems:'flex-start' }}>

                {msg.role === 'ai' ? (
                  <div className="bot-icon">
                    <Bot size={18} color="#a855f7"/>
                  </div>
                ) : (
                  <User size={18}/>
                )}

                <div style={{ flex: 1 }}>
                  <div className="role-text">
                    {msg.role === 'ai' ? 'NEXUS SYSTEM' : 'USER'}
                  </div>

                  <ReactMarkdown
                    components={{
                      h3: (props) => (
                        <h3 style={{
                          color: '#a855f7',
                          marginTop: '12px',
                          marginBottom: '6px'
                        }} {...props} />
                      ),
                      p: (props) => (
                        <p style={{ margin: '8px 0' }} {...props} />
                      ),
                      li: (props) => (
                        <li style={{ margin: '5px 0' }} {...props} />
                      )
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="source-text">
                      Source: {msg.sources.join(', ')}
                    </div>
                  )}
                </div>

              </div>
            </div>
          ))}
        </div>

        {/* INPUT */}
        <div className="input-area">
          <input
            className="chat-input"
            value={input}
            onChange={(e)=>setInput(e.target.value)}
            onKeyDown={(e)=> e.key==="Enter" && handleSend()}
            placeholder={
              files.length > 0
                ? "Ask something about your documents..."
                : "Upload documents to get started..."
            }
          />

          <button className="send-btn" onClick={handleSend}>
            {isQuerying ? (
              <Loader2 className="animate-spin" size={20} color="#a855f7"/>
            ) : (
              <Send size={20} color="#a855f7"/>
            )}
          </button>
        </div>
      </main>
    </div>
  )
}

export default App
