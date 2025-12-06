import { useState, useEffect, useRef } from 'react';
import './App.css';
import { sendMessage } from './api';
import { Heart, Send, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: "Hi lala! ❤️" }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    // 1. Add User Message
    const userMsg = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    // 2. Get Response from Wingman
    const data = await sendMessage(userMsg.text);
    
    // 3. Add Bot Message
    if (data) {
      const botMsg = { sender: 'bot', text: data.response, mood: data.action };
      setMessages(prev => [...prev, botMsg]);
    }
    setIsTyping(false);
  };

  return (
    <div className="chat-container">
      {/* HEADER */}
      <div className="chat-header">
        <Sparkles size={24} color="#fff" />
        <span>Lala ❤️</span>
      </div>

      {/* MESSAGES */}
      <div className="messages-list">
        {messages.map((msg, index) => (
          <motion.div 
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bubble ${msg.sender === 'user' ? 'user-bubble' : 'bot-bubble'}`}
          >
            {msg.text}
          </motion.div>
        ))}
        
        {isTyping && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bubble bot-bubble"
          >
            typing... 💭
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* INPUT */}
      <div className="input-area">
        <input 
          type="text" 
          className="chat-input" 
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="send-btn" onClick={handleSend}>
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}

export default App;