import time
import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []

# A count to record the index of dialog
if 'count' not in st.session_state:
    st.session_state.count = 0

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_files = st.sidebar.file_uploader(
    label="Upload", type=["pdf"], accept_multiple_files=True
)

if prompt := st.chat_input("What is up?"):
# Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.count += 1

    # Sleep one second here to simulate the process of assistant.
    time.sleep(1)
    with st.chat_message('assistant'):
        assistant = f'Good at {st.session_state.count}'
        st.markdown(assistant)
    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant})