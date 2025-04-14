import streamlit as st
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Page configuration
st.set_page_config(
    page_title="👗 StyleMate - Fashion Chatbot",
    page_icon="🧥",
    layout="centered"
)

# Background and styling
background_image_url = "https://images.unsplash.com/photo-1521334884684-d80222895322"  # Fashion background
st.markdown(
    f"""
    <style>
        body {{
            background-color: #f0f8ff;
        }}
        .stApp {{
            background-color: #ffffff;
            border-radius: 16px;
            padding: 30px;
            color: #1f3a60;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
            max-width: 800px;
            margin: auto;
        }}
        .stChatMessage {{
            background-color: #e6f2ff;
            padding: 15px 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            color: #1f3a60;
            font-size: 16px;
            line-height: 1.6;
        }}
        .stChatMessage.user {{
            background-color: #d6ecff;
            text-align: right;
        }}
        .stSidebar {{
            background-color: #ffffff;
            border-radius: 16px;
            padding: 20px;
            color: #1f3a60;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        }}
        input, select, button {{
            border-radius: 8px !important;
            border: 1px solid #a7d8ff !important;
            padding: 10px !important;
            background-color: #f9fcff !important;
            color: #1f3a60 !important;
            font-family: 'Segoe UI', sans-serif !important;
        }}
        button:hover {{
            background-color: #e0f3ff !important;
        }}
        .stButton > button {{
            background-color: #cceaff !important;
            border: none !important;
            color: #1f3a60 !important;
        }}
        .stButton > button:hover {{
            background-color: #b2dfff !important;
        }}
    </style>
    """,unsafe_allow_html=True
)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi fashionista! 👋 I’m your style buddy. Ask me anything about clothes, outfits, colors, or dressing for any occasion!"
    }]

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.markdown("[Get API Key](https://openrouter.ai/keys)")

    model_name = st.selectbox(
        "Choose AI Model",
        ("deepseek/deepseek-r1-zero:free", "google/palm-2-chat-bison"),
        index=0
    )

    with st.expander("Advanced Settings"):
        temperature = st.slider("Response Creativity", 0.0, 1.0, 0.8)
        max_retries = st.number_input("Max Retries", 1, 5, 2)

    if st.button("🧼 Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chat cleared! Ready to help you slay your next outfit! 👗"
        }]

# App Title
st.title("🧥 StyleMate - Fashion Chatbot")
st.caption("Get personalized clothing suggestions and style tips!")

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='stChatMessage'>{message['content']}</div>", unsafe_allow_html=True)

# Handle user input
if prompt := st.chat_input("Ask me anything about clothing, fashion, or outfits..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessage'>{prompt}</div>", unsafe_allow_html=True)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 API key required! Please add it in the sidebar.")
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0

        while attempts < max_retries:
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://stylemate-chatbot.streamlit.app",
                        "X-Title": "StyleMate Fashion Assistant"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are a professional fashion stylist chatbot for StyleMate. Follow these STRICT rules:
1. RESPOND ONLY IN PLAIN TEXT
2. NEVER USE JSON, MARKDOWN, OR CODE BLOCKS
3. ONLY answer questions related to fashion, clothing, outfits, and style
4. If the question is unrelated to fashion, say "I'm here only to talk about fashion and style!"
5. Format suggestions using hyphens (-) only
6. Be fun, fashionable, and friendly
7. Add line breaks between points for readability
8. Current date: {time.strftime("%B %d, %Y")}
"""
                            },
                            *st.session_state.messages
                        ],
                        "temperature": temperature
                    },
                    timeout=15
                )

                response.raise_for_status()
                raw_response = response.json()['choices'][0]['message']['content']

                for chunk in raw_response.split():
                