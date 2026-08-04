import os
from dotenv import load_dotenv
import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant. "
            "Use previous conversation history while answering."
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ]
)

chain = prompt | llm

if "store" not in st.session_state:
    st.session_state.store = {}

store = st.session_state.store

def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chatbot = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

st.set_page_config(page_title="Memory Bot")

st.title("🤖 Memory Enabled Chatbot")

session_id = st.sidebar.text_input(
    "Session ID",
    value="chat1"
)

if st.sidebar.button("Clear Memory"):
    if session_id in store:
        del store[session_id]

    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user = st.chat_input("Ask anything...")

if user:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":user
        }
    )

    with st.chat_message("user"):
        st.markdown(user)

    response = chatbot.invoke(
        {
            "input":user
        },
        config={
            "configurable":{
                "session_id":session_id
            }
        }
    )

    answer = response.content

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)

history = get_history(session_id)

st.sidebar.divider()
st.sidebar.subheader("Memory")

for m in history.messages:
    st.sidebar.write(type(m).__name__, ":", m.content)
