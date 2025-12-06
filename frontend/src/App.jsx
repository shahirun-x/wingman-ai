import { useState, useEffect, useRef } from 'react';
import './App.css';
import { sendMessage } from './api';
import { Send, Sparkles, Volume2 } from 'lucide-react'; // Added Volume2 Icon
import { motion } from 'framer-motion';

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: "Hi baby! ❤️ I missed you. How was your day?" }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // --- NEW FUNCTION: PLAY AUDIO ---
  const playAudio = (base64String) => {
    if (!base64String) return;
    const audio = new Audio(`data:audio/mp3;base64,${base64String}`);
    audio.play();
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // 1. Add User Message
    const userMsg = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    // 2. Get Response
    const data = await sendMessage(userMsg.text);
    
    // 3. Add Bot Message
    if (data) {
      const botMsg = { 
        sender: 'bot', 
        text: data.response, 
        mood: data.action,
        image: data.image_url,
        audio: data.audio_data // <--- Capture the audio
      };
      setMessages(prev => [...prev, botMsg]);
      
      // OPTIONAL: Auto-play the first time? 
      // playAudio(data.audio_data); 
    }
    setIsTyping(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <Sparkles size={24} color="#fff" />
        <span>Lala ❤️</span>
      </div>

      <div className="messages-list">
        {messages.map((msg, index) => (
          <motion.div 
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bubble ${msg.sender === 'user' ? 'user-bubble' : 'bot-bubble'}`}
          >
            {/* The Text */}
            <div>{msg.text}</div>

            {/* The Image (if any) */}
            {msg.image && (
              <img 
                src={msg.image} 
                alt="My Selfie" 
                style={{ marginTop: '10px', borderRadius: '15px', width: '100%', border: '2px solid white' }} 
                onLoad={scrollToBottom}
              />
            )}

            {/* The Voice Button (if audio exists) */}
            {msg.audio && (
              <button 
                onClick={() => playAudio(msg.audio)}
                style={{
                  marginTop: '8px',
                  background: 'rgba(255, 105, 180, 0.2)',
                  border: 'none',
                  borderRadius: '20px',
                  padding: '5px 10px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  color: '#ff69b4',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  fontWeight: 'bold'
                }}
              >
                <Volume2 size={14} /> Play Voice
              </button>
            )}
          </motion.div>
        ))}
        
        {isTyping && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bubble bot-bubble">
            typing... 💭
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

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