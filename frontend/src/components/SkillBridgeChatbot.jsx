import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Canvas } from '@react-three/fiber'
import { Box, OrbitControls } from '@react-three/drei'
import '../styles/SkillBridgeChatbot.css'

function SkillBridgeChatbot() {
  const [query, setQuery] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory])

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a career-related question.')
      return
    }

    const userMessage = { type: 'query', text: query }
    setChatHistory([...chatHistory, userMessage])
    setLoading(true)
    setError('')
    setQuery('')

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, chat_history: chatHistory }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch response from the server.')
      }

      const data = await response.json()
      if (data.status === 'error') {
        throw new Error(data.error)
      }

      setChatHistory(prev => [
        ...prev,
        { type: 'response', text: data.answer }
      ])
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="relative w-full max-w-4xl p-4 md:p-6 flex flex-col h-screen mx-auto bg-gradient-to-br from-primary via-secondary to-accent overflow-hidden">
      {/* Floating Background Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-glass rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -20, 0],
              opacity: [0.2, 0.8, 0.2],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 5 + Math.random() * 5,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Header with 3D Icon */}
      <header className="relative flex items-center justify-between mb-6 p-4 bg-glass backdrop-blur-xs rounded-xl shadow-lg z-10">
        <div className="flex items-center">
          <div className="w-12 h-12 mr-2">
            <Canvas>
              <ambientLight intensity={0.5} />
              <pointLight position={[10, 10, 10]} />
              <Box args={[1, 1, 1]} rotation={[0.4, 0.4, 0]}>
                <meshStandardMaterial color="#3b82f6" />
              </Box>
              <OrbitControls enableZoom={false} autoRotate />
            </Canvas>
          </div>
          <h1 className="text-2xl font-bold text-white">SkillBridge AI</h1>
        </div>
        <p className="text-sm text-blue-200">Your career mentorship assistant</p>
      </header>

      {/* Chat Container */}
      <div className="relative flex-1 overflow-y-auto mb-4 space-y-4 p-4 bg-glass backdrop-blur-xs rounded-xl shadow-inner z-10">
        {chatHistory.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center py-10"
          >
            <div className="bg-glass backdrop-blur-xs p-6 rounded-xl inline-block">
              <h2 className="text-xl font-bold text-white mb-2">Welcome to SkillBridge AI</h2>
              <p className="text-blue-100">
                Ask questions like:<br />
                "What skills do I need for a data scientist role?"<br />
                "How can I prepare for a cloud engineer interview?"<br />
                "What are the best courses for learning Python?"
              </p>
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {chatHistory.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: message.type === 'query' ? 50 : -50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: message.type === 'query' ? 50 : -50 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.type === 'query' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] p-4 rounded-xl ${
                  message.type === 'query'
                    ? 'bg-secondary/80 text-white rounded-br-none'
                    : 'bg-glass backdrop-blur-xs text-white rounded-bl-none'
                } shadow-lg hover:shadow-xl transition-shadow`}
              >
                {message.text.split('\n').map((line, i) => (
                  <p key={i} className="mb-2 last:mb-0">{line}</p>
                ))}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-glass backdrop-blur-xs text-white p-4 rounded-xl rounded-bl-none max-w-[85%] shadow-lg">
              <div className="flex space-x-2">
                <div className="w-3 h-3 rounded-full bg-accent animate-bounce"></div>
                <div className="w-3 h-3 rounded-full bg-accent animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-3 h-3 rounded-full bg-accent animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </motion.div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 bg-red-500/20 text-red-100 rounded-xl text-center z-10"
        >
          {error}
        </motion.div>
      )}

      {/* Input Area */}
      <div className="relative bg-glass backdrop-blur-xs p-4 rounded-xl shadow-lg z-10">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about career planning or skills..."
            className="w-full p-4 pr-12 bg-gray-800/50 border border-glass rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-accent resize-none"
            rows="2"
            disabled={loading}
          />
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleSubmit}
            disabled={loading || !query.trim()}
            className="absolute right-3 bottom-3 p-2 bg-accent rounded-lg hover:bg-accent/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M13 5l7 7-7 7M5 5l7 7-7 7"
              />
            </svg>
          </motion.button>
        </div>
        <p className="text-xs text-gray-300 mt-2">
          Tip: Ask about job skills, interview prep, or learning resources
        </p>
      </div>
    </div>
  )
}

export default SkillBridgeChatbot