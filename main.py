import streamlit as st
import requests
from config.config import BASE_URL
from chat.chat import chat

USER_ID = "test"

def get_session_id():
    try:
        url = f"{BASE_URL['dev']}/api/session"
        payload = {"user_id": USER_ID}
        resp = requests.post(url=url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()["session_id"]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create session: {str(e)}")
        return None
    except KeyError:
        st.error("Invalid session response from server")
        return None

# Initialize session state
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])
    if st.button("Upload and Ingest"):
        if uploaded_file:
            try:
                file = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                resp = requests.post(f"{BASE_URL['dev']}/api/upload_and_ingest", files=file, timeout=30)
                resp.raise_for_status()
                st.success(f"Upload successful: {resp.status_code}")
                st.json(resp.json())
            except requests.exceptions.RequestException as e:
                st.error(f"Upload failed: {str(e)}")
        else:
            st.warning("Please upload a file first")

# Show chat or new chat button
if not st.session_state.chat_active:
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.chat_active = True
            try:
                with st.popover("Available sources"):
                    resp = requests.get(f"{BASE_URL['dev']}/api/get_all_src", timeout=10)
                    resp.raise_for_status()
                    available_srcs = resp.json().get('source', [])
                    if available_srcs:
                        for source in available_srcs:
                            st.markdown(source)
                    else:
                        st.info("No sources available yet")
                
                session_id = get_session_id()
                if session_id:
                    st.session_state.session_id = session_id
                    st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Error loading sources: {str(e)}")
    with col2:
        pass
else:
    # Chat is active - show end button and chat interface
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Chat Active")
    with col2:
        if st.button("🔄 End Chat"):
            st.session_state.chat_active = False
            st.session_state.messages = []
            st.rerun()
    
    # Display the chat
    chat(session_state=st.session_state)
