import streamlit as st
import requests
from typing import Optional
import time
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# Backend API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://chatbot-backend:8000")
API_TIMEOUT = 30  # seconds

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .error-message {
        padding: 1rem;
        background-color: #fee;
        border-left: 4px solid #f44;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .success-message {
        padding: 1rem;
        background-color: #efe;
        border-left: 4px solid #4f4;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 0.75rem 1rem;
        background-color: #e3f2fd;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    
    if "api_available" not in st.session_state:
        st.session_state.api_available = None
    
    if "error_count" not in st.session_state:
        st.session_state.error_count = 0

# API functions
def check_api_health() -> bool:
    """Check if backend API is available"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=5
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def send_message(message: str, session_id: Optional[str] = None) -> dict:
    """Send message to backend API"""
    try:
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=API_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. Please try again."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to the chatbot service. Please try again later."
        }
    except requests.exceptions.HTTPError as e:
        error_detail = "An error occurred while processing your request."
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", error_detail)
        except:
            pass
        return {
            "success": False,
            "error": f"Service error: {error_detail}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def clear_conversation():
    """Clear conversation history"""
    st.session_state.messages = []
    st.session_state.session_id = None
    st.session_state.error_count = 0

def export_conversation() -> str:
    """Export conversation as JSON"""
    conversation = {
        "session_id": st.session_state.session_id,
        "timestamp": datetime.now().isoformat(),
        "messages": st.session_state.messages
    }
    return json.dumps(conversation, indent=2)

# UI Components
def render_sidebar():
    """Render sidebar with controls and info"""
    with st.sidebar:
        st.title("🤖 Chatbot Settings")
        
        # API Status
        st.subheader("📡 API Status")
        if st.button("Check Connection", use_container_width=True):
            with st.spinner("Checking..."):
                st.session_state.api_available = check_api_health()
        
        if st.session_state.api_available is True:
            st.markdown("✅ **Connected**")
        elif st.session_state.api_available is False:
            st.markdown("❌ **Disconnected**")
        else:
            st.markdown("⚪ **Unknown**")
        
        st.divider()
        
        # Session Info
        st.subheader("💬 Session Info")
        if st.session_state.session_id:
            st.text_input(
                "Session ID",
                value=st.session_state.session_id,
                disabled=True,
                label_visibility="collapsed"
            )
            st.caption(f"Messages: {len(st.session_state.messages)}")
        else:
            st.caption("No active session")
        
        st.divider()
        
        # Actions
        st.subheader("⚙️ Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                clear_conversation()
                st.rerun()
        
        with col2:
            if st.session_state.messages:
                conversation_json = export_conversation()
                st.download_button(
                    label="💾 Export",
                    data=conversation_json,
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        st.divider()
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **AI Chatbot Interface**
            
            Powered by:
            - AWS Bedrock (Claude 3 Haiku)
            - FastAPI Backend
            - Streamlit Frontend
            
            Features:
            - Persistent conversations
            - Session management
            - Error handling
            - Export functionality
            """)
        
        # Settings
        with st.expander("⚙️ Advanced Settings"):
            st.text_input(
                "API Base URL",
                value=API_BASE_URL,
                disabled=True,
                help="Backend API endpoint"
            )
            st.caption("Configure via environment variables in Kubernetes deployment")

def render_chat_interface():
    """Render main chat interface"""
    # Title
    st.title("💬 AI Chatbot")
    st.caption("Chat with Claude 3 Haiku powered by AWS Bedrock")
    
    # Display welcome message if no messages
    if not st.session_state.messages:
        st.markdown("""
        <div class="info-box">
            👋 Welcome! Start a conversation by typing a message below.
            Your conversation will be saved automatically.
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(message["timestamp"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here...", key="chat_input"):
        # Add user message to chat
        timestamp = datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(timestamp)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt, st.session_state.session_id)
                
                if response["success"]:
                    # Reset error count on success
                    st.session_state.error_count = 0
                    
                    # Extract response data
                    ai_message = response["data"]["response"]
                    st.session_state.session_id = response["data"]["session_id"]
                    
                    # Display and save AI response
                    st.markdown(ai_message)
                    response_timestamp = datetime.now().strftime("%I:%M %p")
                    st.caption(response_timestamp)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_message,
                        "timestamp": response_timestamp
                    })
                    
                else:
                    # Handle error
                    st.session_state.error_count += 1
                    error_msg = response["error"]
                    
                    st.error(f"❌ {error_msg}")
                    
                    # Suggest checking connection after multiple errors
                    if st.session_state.error_count >= 3:
                        st.warning("Multiple errors detected. Please check the API connection in the sidebar.")
                    
                    # Add error to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ Error: {error_msg}",
                        "timestamp": datetime.now().strftime("%I:%M %p"),
                        "is_error": True
                    })
        
        # Rerun to update the UI
        st.rerun()

def render_error_banner():
    """Render error banner if API is down"""
    if st.session_state.api_available is False:
        st.markdown("""
        <div class="error-message">
            ⚠️ <strong>Service Unavailable</strong><br>
            The chatbot service is currently unavailable. Please try again later or contact support.
        </div>
        """, unsafe_allow_html=True)

# Main application
def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Check API health on first load
    if st.session_state.api_available is None:
        st.session_state.api_available = check_api_health()
    
    # Render error banner if needed
    render_error_banner()
    
    # Render main chat interface
    render_chat_interface()
    
    # Footer
    st.divider()
    st.caption("💡 Tip: Use the sidebar to manage your conversation and check connection status.")

if __name__ == "__main__":
    main()