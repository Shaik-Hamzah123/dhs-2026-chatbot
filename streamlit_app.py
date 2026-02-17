import streamlit as st
import asyncio
from agent import run_conversation
import base64
from PIL import Image
import io
import time

# Set page config for a premium look
st.set_page_config(
    page_title="DHS 2026 AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium aesthetics
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9;
    }
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 10px !important;
        backdrop-filter: blur(10px);
    }
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }
    .stSidebar {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    h1 {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to convert image to base64
def get_image_base64(image_file):
    if image_file is not None:
        img = Image.open(image_file)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
    return None

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Settings")
    
    st.markdown("---")
    mem0_user_id = st.text_input("User ID", value="user_skh", help="Unique identifier for the user.")
    mem0_session_id = st.text_input("Session ID", value="session_001", help="Current chat session identifier.")
    signed_in = st.toggle("User Signed In", value=True)
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"], help="Upload an image for the AI to analyze.")
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main UI
st.title("🤖 DHS 2026 AI Assistant")
st.markdown("*Your intelligent companion for everything Data Hack Summit 2026.*")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Helper function for fake streaming
def stream_text(text, delay=0.03):
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)

# React to user input
if prompt := st.chat_input("Ask me anything about DHS 2026..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare inputs
    image_data = get_image_base64(uploaded_file)
    
    with st.spinner("Thinking..."):
        try:
            # Run conversation
            response = asyncio.run(run_conversation(
                user_input=prompt,
                mem0_user_id=mem0_user_id,
                mem0_session_id=mem0_session_id,
                signed_in=signed_in,
                image_data=image_data
            ))
            
            # Display assistant response in chat message container with streaming
            with st.chat_message("assistant"):
                full_response = st.write_stream(stream_text(response))
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": "I'm sorry, I encountered an error. Please check the logs."})
