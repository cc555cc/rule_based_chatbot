import { useState, useEffect, useRef } from "react";
import "./App.css";

const MENU = {
  Breakfast: [
    { name: "Eggs Benedict", price: "$4.99" },
    { name: "Waffle Fresh Berries", price: "$3.99" },
    { name: "Porridge With Cherries", price: "$6.99" },
    { name: "Poached Egg Sandwiches", price: "$5.99" },
    { name: "Banana & Blackberry Toast", price: "$4.99" },
  ],
  Mains: [
    { name: "Lasagna", price: "$4.99" },
    { name: "Beef Stew", price: "$3.99" },
    { name: "Salmon Steak", price: "$6.99" },
    { name: "Spaghetti", price: "$5.99" },
    { name: "Green Pea Soup", price: "$4.99" },
  ],
};

const QUICK_REPLIES = ["See menu", "Book a table", "Hours", "Delivery"];

function MenuCard() {
  return (
    <div className="menu-card">
      <div className="menu-card-header">
        <span>🍽 Our Menu</span>
      </div>
      {Object.entries(MENU).map(([section, items]) => (
        <div className="menu-section" key={section}>
          <div className="menu-section-title">{section}</div>
          {items.map((item) => (
            <div className="menu-item" key={item.name}>
              <span className="menu-item-name">{item.name}</span>
              <span className="menu-item-price">{item.price}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function getBotReply(input) {
  const lower = input.toLowerCase();

  if (lower.includes("menu") || lower.includes("food") || lower.includes("dish") || lower.includes("serve")) {
    return { text: "Here's what we're serving today — fresh ingredients, made with care.", showMenu: true };
  }
  if (lower.includes("hour") || lower.includes("open") || lower.includes("close")) {
    return { text: "We're open daily from 9 AM to 9 PM. We'd love to see you anytime!" };
  }

  const bookMatch = input.match(/book.*?(\d+)\s*(?:people|person|guests?)?.*?(?:for\s+)?([A-Z][a-z]+).*?(\w+day|\d+[\/\-]\d+).*?(\d+(?::\d+)?\s*(?:am|pm))/i);
  if (lower.includes("book") || lower.includes("reserv") || lower.includes("table")) {
    if (bookMatch) {
      const [, count, name, day, time] = bookMatch;
      return { text: `We have reserved a table of ${count} under ${name} on ${day} at ${time}. See you then! 🥂` };
    }
    return { text: "I'd be happy to book a table! Please share your name, number of guests, preferred day, and time." };
  }

  const deliveryMatch = input.match(/delivery.*?([A-Z][a-z]+).*?(\d+\s+\w+\s+\w+).*?with\s+([\w\s]+)/i);
  if (lower.includes("delivery") || lower.includes("deliver")) {
    if (deliveryMatch) {
      const [, name, address, item] = deliveryMatch;
      const menuItem = Object.values(MENU).flat().find(m => m.name.toLowerCase().includes(item.toLowerCase().trim()));
      const price = menuItem ? menuItem.price : "$5.99";
      return { text: `We've scheduled a delivery for ${name} to ${address} with ${item.trim()}. Total: ${price} 🛵` };
    }
    return { text: "For delivery, please share the recipient's name, address, and what you'd like to order!" };
  }

  if (lower.includes("hello") || lower.includes("hi") || lower.includes("hey")) {
    return { text: "Welcome! It's wonderful to have you here. Can I help you explore our menu, book a table, or arrange a delivery?" };
  }

  return { text: null, learned: input };
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
  const [learnedMsg, setLearnedMsg] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    if (learnedMsg) {
      const t = setTimeout(() => setLearnedMsg(""), 4000);
      return () => clearTimeout(t);
    }
  }, [learnedMsg]);

  const sendMessage = (text = input) => {
    if (!text.trim()) return;

    const userMsg = { text, sender: "user", time: getTime() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    const reply = getBotReply(text);

    setTimeout(() => {
      setIsTyping(false);
      if (reply.learned) {
        setLearnedMsg(reply.learned);
        setMessages((prev) => [
          ...prev,
          {
            text: "I haven't learned that response yet — but I'm noting it for next time!",
            sender: "bot",
            time: getTime(),
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            text: reply.text,
            sender: "bot",
            time: getTime(),
            showMenu: reply.showMenu,
          },
        ]);
      }
    }, 900);
  };

  return (
    <div className="chat-wrapper">
      {/* Header */}
      <div className="chat-header">
        <div className="header-icon">🍷</div>
        <div className="header-text">
          <div className="header-title">Bella Cucina</div>
          <div className="header-subtitle">Restaurant Assistant</div>
        </div>
        <div className="status-dot" title="Online" />
      </div>

      {/* Messages */}
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.sender}`}>
            <div className="message-bubble">
              {msg.text}
              {msg.showMenu && <MenuCard />}
            </div>
            <div className="message-time">{msg.time}</div>
          </div>
        ))}

        {isTyping && (
          <div className="message-row bot">
            <div className="typing-indicator">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Quick replies */}
      <div className="quick-replies">
        {QUICK_REPLIES.map((q) => (
          <button key={q} className="quick-reply-btn" onClick={() => sendMessage(q)}>
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
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

      {/* Learning toast */}
      {learnedMsg && (
        <div className="learning-toast">
          <strong>New input logged</strong>
          "{learnedMsg}"
        </div>
      )}
    </div>
  );
}
