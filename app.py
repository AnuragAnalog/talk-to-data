import os
import pandas as pd
import streamlit as st

from datetime import datetime
from pandasai import Agent

def display_answer(answer, sidebar=False):
    if isinstance(answer, pd.DataFrame):
        if sidebar:
            st.sidebar.dataframe(answer, height=150)
        else:
            st.dataframe(answer, height=150)
    elif isinstance(answer, str):
        if answer.endswith('.png') or answer.endswith('.jpg'):
            if sidebar:
                st.sidebar.write(f"**Plot:**")
                st.sidebar.image(answer)
            else:
                st.write(f"**Plot:**")
                st.image(answer)
        else:
            if sidebar:
                st.sidebar.success(f"**Answer:** {answer}")
            else:
                st.success(f"**Answer:** {answer}")

def display_chat(chat, sidebar=False):
    if sidebar:
        st.sidebar.info(f"**Question:** {chat['question']}")
        display_answer(chat['answer'], sidebar)
        st.sidebar.write("---")
    else:
        st.info(f"**Question:** {chat['question']}")
        display_answer(chat['answer'])
        st.write("---")

# Main window: Current Chat and Title
st.set_page_config(layout="wide")

# Initialize the session state
if "history" not in st.session_state:
    st.session_state.history = []
if "current_session" not in st.session_state:
    st.session_state.current_session = []

st.title("Talk to your Data")
# if st.sidebar.button("New Chat"):
#     if len(st.session_state.current_session) > 0:
#         st.session_state.history.append(st.session_state.current_session)
#         st.session_state.current_session = []

# Sidebar: API Endpoint Input and Set the API key in the environment variable
st.sidebar.header('API Input')
api_endpoint = st.sidebar.text_input('Enter the API Endpoint')
os.environ["PANDASAI_API_KEY"] = api_endpoint

## Sidebar elements
uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"]) # File upload
is_privacy_enabled = st.sidebar.checkbox("Enable Privacy Mode", value=True) # Enable privacy mode

if uploaded_file is not None:
    # Determine if the file is CSV or Excel
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")

    show_raw_data = st.checkbox('Show raw data', value=True)
    if show_raw_data:
        st.write("### Raw Data")
        st.dataframe(df, height=150)

# Chat history
with st.expander("### Current Session Chat History"):
    with st.container(height=300):
        for chat in st.session_state.current_session:
            display_chat(chat)

# Question input
question = st.text_input("Enter your question")

# You can use the API endpoint to do something with the file or question
if st.button('Generate'):
    if api_endpoint and uploaded_file is not None and question:
        agent = Agent(df, config={"enforce_privacy": is_privacy_enabled})
        answer = agent.chat(question)
        if isinstance(answer, str) and answer.endswith('.png'):
            change_fpath = f"{"".join(answer.split(".")[:-1])}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{answer.split('.')[-1]}"
            os.rename(answer, change_fpath)
            answer = change_fpath
        st.session_state.current_session.append({"question": question, "answer": answer})
        display_chat(st.session_state.current_session[-1])
    else:
        st.error("Please make sure to provide the API endpoint, upload a file, and enter a question.")

# Display the history in sidebar
# if len(st.session_state.history) > 0:
#     st.sidebar.header("Chat History")
#     for chat_session in st.session_state.history:
#         with st.expander(chat_session[0]['question']):
#             with st.container(height=150):
#                 for chat in chat_session:
#                     display_chat(chat, sidebar=True)
