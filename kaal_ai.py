import streamlit as st
import google.generativeai as genai
import json
import os
import uuid
from datetime import datetime
import time
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# Page Config
st.set_page_config(page_title="Kaal AI - India's Best", page_icon="🧠", layout="wide")

# Inject minimalist background + modern font
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: #212529;
    }

    .block-container {
        padding-top: 4rem;
    }

    .user-message {
        background-color: #d1e7dd;
        color: #0f5132;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        margin-left: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .bot-message {
        background-color: #cfe2ff;
        color: #084298;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        margin-right: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .typing-indicator {
        color: #6c757d;
        font-style: italic;
    }

    /* Hide Streamlit's hamburger and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Configure Gemini API Key
genai.configure(api_key="AIzaSyD60S4qvkQM0cXVmYsZ1Slj5IrdoEpXtso")

# Create Unique User ID for Session
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

USER_ID = st.session_state.user_id
HISTORY_FILE = f"chat_history_{USER_ID}.json"

# Load Chat History
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            all_chats = json.load(f)
            if not isinstance(all_chats, dict):
                all_chats = {}
        except json.JSONDecodeError:
            all_chats = {}
else:
    all_chats = {}

# Today’s Key
today_key = datetime.now().strftime("%Y-%m-%d")
if today_key not in all_chats:
    all_chats[today_key] = []

# Sidebar – Past Conversations + New Chat Button
with st.sidebar:
    st.header("📅 Past Conversations")

    if st.button("🆕 Start New Chat"):
        st.session_state.pop("chat_session", None)
        all_chats[today_key] = []
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(all_chats, f, indent=2, ensure_ascii=False)
        st.success("✨ New chat started!")
        st.rerun()

    for date in sorted(all_chats.keys(), reverse=True):
        with st.expander(date):
            for msg in all_chats[date]:
                st.markdown(f"👤 **You**: {msg['user']}")
                st.markdown(f"🤖 **Kaal AI**: {msg['bot']}")
                st.markdown("---")

# Main UI
st.title("🤖 Kaal AI - Gemini Trained Interface")
st.markdown("🧠 Powered by Google's Gemini AI – developed for futuristic Bharat 🇮🇳")

# Show Today’s Chat
if all_chats[today_key]:
    st.subheader("📌 Today’s Chat")
    for msg in all_chats[today_key]:
        st.markdown(f"<div class='user-message'>👤 **You**: {msg['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bot-message'>🤖 **Kaal AI**: {msg['bot']}</div>", unsafe_allow_html=True)
        st.markdown("---")

# Function to record voice and return as text
def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Say something!")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.success(f"🎤 You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError:
            st.error("Could not request results from Google Speech Recognition service.")
    return None

# Voice Input Button
if st.button("🎤 Voice Input"):
    user_input = voice_input()

# If there's text input from user or voice
if user_input:
    st.markdown(f"<div class='user-message'>👤 **You**: {user_input}</div>", unsafe_allow_html=True)

    history_messages = []
    for msg in all_chats[today_key]:
        history_messages.append({"role": "user", "parts": [msg["user"]]})
        history_messages.append({"role": "model", "parts": [msg["bot"]]})

    if "chat_session" not in st.session_state:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-001")
        st.session_state.chat_session = model.start_chat(history=history_messages)

    try:
        # Typing animation
        st.markdown("<div class='typing-indicator'>🤖 Kaal AI is typing...</div>", unsafe_allow_html=True)
        time.sleep(1)

        # Get AI response
        chat = st.session_state.chat_session
        ai_response = chat.send_message(user_input).text

        # Show response
        st.markdown(f"<div class='bot-message'>🤖 **Kaal AI**: {ai_response}</div>", unsafe_allow_html=True)
        st.markdown("---")

        # Save
        all_chats[today_key].append({"user": user_input, "bot": ai_response})
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(all_chats, f, indent=2, ensure_ascii=False)

        st.rerun()

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
