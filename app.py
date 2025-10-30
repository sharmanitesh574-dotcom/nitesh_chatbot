# ==========================================
# Nitesh's Final Streamlit Chatbot (UTF-8 Safe)
# ==========================================
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
import sys

# ==========================================
# Force UTF-8 Encoding at Runtime
# ==========================================
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ==========================================
# Load Environment Variables
# ==========================================
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
api_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
referrer = os.getenv("OPENROUTER_REFERRER", "https://share.streamlit.io")
title = os.getenv("OPENROUTER_TITLE", "Nitesh's AI Chatbot")

if not api_key:
    st.error("❌ OPENROUTER_API_KEY not found in .env file.")
    st.stop()

# ==========================================
# Streamlit App Configuration
# ==========================================
st.set_page_config(
    page_title="Nitesh's AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Nitesh's Multi-Model Chatbot (OpenRouter)")

# ==========================================
# Chat Persistence
# ==========================================
CHAT_FILE = "chat_history.json"

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": "You are a friendly and helpful assistant."}]

def save_chat(messages):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

# ==========================================
# Model Selection
# ==========================================
model_map = {
    "GPT-4o (OpenAI)": "openai/gpt-4o",
    "Claude 3.5 Sonnet (Anthropic)": "anthropic/claude-3.5-sonnet",
    "Gemini 1.5 Pro (Google)": "google/gemini-1.5-pro",
    "Mistral Large (Mistral)": "mistralai/mistral-large",
}

selected_model_name = st.selectbox("🧠 Choose a Model", list(model_map.keys()))
selected_model = model_map[selected_model_name]

# ==========================================
# Display Chat History
# ==========================================
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🧑‍💻 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# ==========================================
# User Input and API Call
# ==========================================
user_input = st.chat_input("Type your message...")

if user_input:
    # Ensure clean UTF-8 user text
    user_input = user_input.encode("utf-8", "ignore").decode("utf-8")
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"**🧑‍💻 You:** {user_input}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json; charset=utf-8",
        "HTTP-Referer": referrer,
        "X-Title": title,
    }

    payload = {
        "model": selected_model,
        "messages": st.session_state.messages,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.encoding = "utf-8"
        data = response.json()

        if "choices" in data:
            bot_reply = data["choices"][0]["message"]["content"]
            bot_reply = bot_reply.encode("utf-8", "ignore").decode("utf-8")
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.markdown(f"**🤖 Bot:** {bot_reply}")
            save_chat(st.session_state.messages)
        else:
            st.error(f"⚠️ Unexpected response: {data}")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ==========================================
# Clear Chat Option
# ==========================================
if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = [{"role": "system", "content": "You are a friendly and helpful assistant."}]
    save_chat(st.session_state.messages)
    st.experimental_rerun()
