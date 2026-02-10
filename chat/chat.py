import streamlit as st
import requests

from config.config import BASE_URL
USER_ID = "test"


def query(prompt="Hi!!", session_id=None):
    url = f"{BASE_URL['dev']}/api/query"
    payload = {
                "query": prompt,
                "chat_history": [
                                    ""
                                ],
                "session_id": session_id,
                "user_id": USER_ID
                }
    resp = requests.post(url=url, json=payload)
    return resp.json()

def chat(session_state=None):
    if "messages" not in st.session_state:
        session_state.messages = []

    chat_box = st.empty()

    def render_chat():
        with chat_box.container():
            for msg in session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
    prompt = st.chat_input("Ask you question from avilable source")
    if prompt:
        session_state.messages.append({"role":"user", "content":prompt})
        render_chat()
        resp = query(prompt=prompt, session_id=session_state.session_id)
        session_state.messages.append({"role":"ai", "content":resp['answer']})
        render_chat()
        print(session_state)
