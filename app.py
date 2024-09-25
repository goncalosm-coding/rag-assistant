import streamlit as st
from query_data import query_rag
from dotenv import load_dotenv

load_dotenv()

# Define the Streamlit interface
st.title("Hermingarda - Your PNA Assistant")

# Initialize session state for messages and OpenAI model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"  # Use the model you want to use

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input text box for the query
if prompt := st.chat_input("Ask a question based on the medical research documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare context by gathering previous messages
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    # Fetch response using the query_rag function, passing the user prompt and previous context
    with st.chat_message("assistant"):
        response = query_rag(context + "\nuser: " + prompt)  # Pass the context to the query_rag function
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Optional: Add a small space at the bottom for better UX
st.write("")  # Just a placeholder for spacing