import textwrap as tw

import requests
import streamlit as st

st.set_page_config(page_icon=":robot:", page_title="RFP Question Answering Interface")


# hide anchor popups from title elements
st.markdown(
    """
    <style>
    /* Hide the link button */
    .stApp a:first-child {
        display: none;
    }
    
    .css-15zrgzn {display: none}
    .css-eczf16 {display: none}
    .css-jn99sy {display: none}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("Settings")
    do_text_wrap = st.toggle("Enable text wrapping for the answers", True)

    st.divider()
    st.title("Submit a Ticket to Product Owners")
    ticket_prompt = st.text_area("Enter details here:")
    if st.button("Submit Ticket"):
        payload = {"description": st.session_state["question"]}
        response = requests.post("http://django-web:8000/ticket/", json=payload)
        response.raise_for_status()
        st.success("Ticket submitted successfully!")

st.title("RFP Question Answering Interface")

prompt = st.text_area("Enter your RFP question here:")

results = st.session_state.get("Results")
if st.button("Submit"):
    response = requests.post("http://django-web:8000/inference/", json={"question": prompt})
    response.raise_for_status()

    results = st.session_state["Results"] = response.json()

    if not results:
        st.write("No suitable answer found.")
        st.write("A ticket has been created for this question to be answered by product owners.")
        st.stop()
elif not results:
    st.stop()

st.write("## Possible Answers")
st.write(
    "Select the answer that best answers your question. It is ranked according to the model's confidence. (Top to bottom)"
)
for i, result in enumerate(results):
    if do_text_wrap:
        answer = "\n".join(tw.wrap(result["answer"], width=80))
    else:
        answer = result["answer"]
    answer_id = result["answer_id"]

    col_1, col_2 = st.columns([1, 5])
    with col_1:
        success_button = st.button(
            ":green[Accept Answer]",
            i,
            help="Clicking this button will link your question to this answer in the system.",
        )
    with col_2:
        st.markdown(f"#### Answer ID: {answer_id}")

    st.code(answer, language="plaintext")
    with st.expander("Show Details"):
        st.write(result)

    if success_button:
        st.success("Answer accepted! Your feedback will improve the system performance.")

    st.divider()

if st.button(
    ":red[Reject All Answers and Create Ticket]",
    help="Clicking this button will automatically create a ticket for the product owners to answer this question.",
):
    st.success("A ticket has been created for this question to be answered by product owners.")
