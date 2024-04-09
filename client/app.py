import textwrap as tw
from traceback import print_exc

import requests
import streamlit as st

st.set_page_config(page_icon=":robot:", page_title="RFP Question Answering Interface")

st.title("RFP Question Answering Interface")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Please submit a question"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


def add_assistant_message(text: str) -> None:
    st.session_state.messages.append({"role": "assistant", "content": text})
    st.chat_message("assistant").write(text)


def add_copyable_answer(text: str) -> None:
    st.code(
        "\n".join(
            tw.wrap(
                text,
                width=80,
            )
        )
    )


def process_command(command: str):
    if command == "/ticket":
        add_assistant_message("Creating a ticket...")
        payload = {"description": st.session_state["question"]}
        response = requests.post("http://django-web:8000/ticket/", json=payload)
        response.raise_for_status()
    elif command == "/more":
        answers = st.session_state.get("answers", [])
        if len(answers) < 2:
            add_assistant_message("I'm sorry, I don't have any more answers.")
            return
        add_assistant_message(f"Here are all {len(answers)} possible answers:")
        for answer in answers:
            st.code(
                "\n".join(
                    tw.wrap(
                        answer["answer"],
                        width=80,
                    )
                )
            )
        add_assistant_message(
            "If none of the results were suitable, please reply with `/ticket` to "
            "automatically create a ticket. Alternatively, you can create a ticket manually by filling out the form in the sidebar."
        )


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    if prompt.startswith("/"):
        process_command(prompt)
        st.stop()

    st.session_state["question"] = prompt
    add_assistant_message("Searching...")
    payload = {"question": prompt}
    response = requests.post("http://django-web:8000/inference/", json=payload)
    response.raise_for_status()
    answers = st.session_state["answers"] = response.json()

    if not answers:
        add_assistant_message("I'm sorry, I don't have an answer to that question.")
        add_assistant_message("A ticket has been created for this question to be answered.")
        st.stop()

    add_assistant_message("This is the top answer to your question:")
    add_copyable_answer(answers[0]["answer"])

    try:
        question_payload = {"question_text": prompt, "answer_id": answers[0]["answer_id"]}
        response = requests.post("http://django-web:8000/insert_question/", json=question_payload)
        response.raise_for_status()
        if response.json().get("error"):
            raise Exception(response.json()["error"])
        st.session_state["question_id"] = response.json()["id"]
    except Exception:
        print_exc()

    if len(answers) > 1:
        add_assistant_message(
            f"I found {len(answers)} possible answers. If you would like to see more, please reply with `/more`."
        )
