import os
import sys
import io
import json
import requests
import streamlit as st
from dotenv import load_dotenv

# ==========================================
# 🔧 Force UTF-8 globally (fix for latin-1 error)
# ==========================================
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')

# ==========================================
# 🔐 Load Environment Variables
# ==========================================
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
api_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
referrer = os.getenv("OPENROUTER_REFERRER", "https://share.streamlit.io")
title = os.getenv("OPENROUTER_TITLE", "Nitesh’s AI Chatbot")

if not api_key:
    st.error("❌ OPENROUTER_API_KEY not found in .env file.")
    st.stop()

# ==========================================
# ⚙️ Streamlit App Configuration
# ==========================================
st.set_page_config(page_title="Nitesh's AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Nitesh’s Multi-Model Chatbot (OpenRouter)")

# ==========================================
# 💾 Chat Persistence
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
# 🧠 Model Selection
# ==========================================
model_map = {
    "GPT-4o (OpenAI)": "openai/gpt-4o",
    "Claude 3.5 Sonnet (Anthropic)": "anthropic/claude-3.5-sonnet",
    "Gemini 1.5 Pro (Google)": "google/gemini-1.5-pro",
    "Mistral Large (Mistral)": "mistralai/mistral-large",
}

selected_model_name = st.selectbox("🧩 Choose a Model", list(model_map.keys()))
selected_model = model_map[selected_model_name]

# ==========================================
# 💬 Display Chat History
# ==========================================
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🧑‍💻 You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# ==========================================
# ⌨️ User Input + API Call
# ==========================================
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"**🧑‍💻 You:** {user_input}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Referer": referrer,   # ✅ Correct header name
        "X-Title": title,
    }

    payload = {
        "model": selected_model,
        "messages": st.session_state.messages,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        data = response.json()

        if response.status_code == 401:
            st.error("🔑 Unauthorized: Check your API key or Referer domain on OpenRouter.")
        elif "choices" in data:
            bot_reply = data["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.markdown(f"**🤖 Bot:** {bot_reply}")
            save_chat(st.session_state.messages)
        else:
            st.error(f"⚠️ Unexpected response: {json.dumps(data, indent=2)}")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ==========================================
# 🧹 Clear Chat Option
# ==========================================
if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = [{"role": "system", "content": "You are a friendly and helpful assistant."}]
    save_chat(st.session_state.messages)
    st.experimental_rerun()
