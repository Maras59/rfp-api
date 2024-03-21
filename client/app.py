"""
To run the dashboard, use the following command in the terminal:
`streamlit run app.py`
"""
import requests
import streamlit as st

st.title("RFP Question Answering Interface")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Please submit a question"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


def add_assistant_message(text: str):
    st.session_state.messages.append({"role": "assistant", "content": text})


url = "http://localhost:8000/inference/"

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    payload = {"question": prompt}
    response = requests.post(url, json=payload)
    answers = response.json()
    if not answers:
        message = "I'm sorry, I don't have an answer to that question."
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.chat_message("assistant").write(message)
    for answer in answers:
        add_assistant_message(answer["answer"])
        st.chat_message("assistant").write(answer["answer"])
        break
