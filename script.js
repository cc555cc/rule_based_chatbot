const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const messages = document.getElementById("chat-messages");
const CHAT_API_URL = "http://127.0.0.1:8000/api/chat";

function addMessage(text, className) {
  const message = document.createElement("div");
  message.className = `message ${className}`;

  if (typeof text === "string" && /\.(png|jpg|jpeg|gif|webp)$/i.test(text)) {
    const image = document.createElement("img");
    image.src = text;
    image.alt = "Menu";
    image.className = "chat-image";
    message.appendChild(image);
  } else {
    message.textContent = text;
  }

  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const userText = input.value.trim();
  if (!userText) {
    return;
  }

  addMessage(userText, "user-message");
  input.value = "";

  try {
    const response = await fetch(CHAT_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userText }),
    });

    const data = await response.json();
    addMessage(data.reply, "bot-message");
  } catch (error) {
    addMessage("Could not reach the chatbot server.", "bot-message");
  }
});
