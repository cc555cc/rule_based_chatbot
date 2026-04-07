import { useEffect, useRef, useState } from "react";
import "./App.css";

const QUICK_REPLIES = ["See menu", "Book a table", "Hours", "Delivery"];
const CHAT_API_URL = "/api/chat";

function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function isImageMessage(text) {
  return typeof text === "string" && /\.(png|jpg|jpeg|gif|webp)$/i.test(text);
}

function createBotMessages(reply) {
  const items = Array.isArray(reply) ? reply : [reply];

  return items.map((item) => ({
    text: item,
    sender: "bot",
    time: getTime(),
    isImage: isImageMessage(item),
  }));
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      text: "Good evening. Welcome to Bella Cucina. How can I make your experience special today?",
      sender: "bot",
      time: getTime(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = async (text = input) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { text: trimmed, sender: "user", time: getTime() }]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: trimmed }),
      });

      const data = await response.json();
      setMessages((prev) => [...prev, ...createBotMessages(data.reply)]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          text: "Could not reach the chatbot server.",
          sender: "bot",
          time: getTime(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-header">
        <div className="header-icon">🍷</div>
        <div className="header-text">
          <div className="header-title">Bella Cucina</div>
          <div className="header-subtitle">Restaurant Assistant</div>
        </div>
        <div className="status-dot" title="Online" />
      </div>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.sender}`}>
            <div className="message-bubble">
              {msg.isImage ? <img src={msg.text} alt="Menu" className="chat-image" /> : msg.text}
            </div>
            <div className="message-time">{msg.time}</div>
          </div>
        ))}

        {isTyping && (
          <div className="message-row bot">
            <div className="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="quick-replies">
        {QUICK_REPLIES.map((q) => (
          <button key={q} className="quick-reply-btn" onClick={() => sendMessage(q)}>
            {q}
          </button>
        ))}
      </div>

      <div className="input-area">
        <div className="input-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button className="send-btn" onClick={() => sendMessage()}>
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
