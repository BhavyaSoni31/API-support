__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from streamlit_chat import message
from utils import get_retriever, get_relevent_docs, get_valid_documents, generate_answer, check_hellucincation
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(message)s",
    level=logging.INFO
)

# Function to handle chatbot responses
def chatbot_response(user_input):
    try:
        retriever = get_retriever()
        docs = get_relevent_docs(retriever, user_input)
        valid_docs = get_valid_documents(user_input, docs)
        answer = generate_answer(user_input, valid_docs)
        hellucination_status = check_hellucincation(valid_docs, answer)
        if hellucination_status:
            return f"{answer}"
        else:
            return f"Hellucination detected: {answer}"
    except Exception as ex:
        logging.error(f"Error occurred while processing your query. Error: {ex}")
        return f"Error occurred while processing your query. Try different question."

# Streamlit app setup
st.title("CrustData API support")

# Session state to store messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input form
with st.form(key="chat_form"):
    user_input = st.text_input("You: ", placeholder="Type your message here...")
    submit_button = st.form_submit_button(label="Send")

# Process user input
if submit_button and user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate and append chatbot response
    response = chatbot_response(user_input)
    st.session_state.messages.append({"role": "bot", "content": response})

# Reverse the chat history in pairs (user query followed by bot response)
reversed_pairs = list(zip(st.session_state.messages[::2], st.session_state.messages[1::2]))[::-1]

# Display the reversed pairs
for i, (user_msg, bot_msg) in enumerate(reversed_pairs):
    message(user_msg["content"], is_user=True, key=f"user_{i}")
    message(bot_msg["content"], is_user=False, key=f"bot_{i}")
