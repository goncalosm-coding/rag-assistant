import sounddevice as sd
import whisper
import scipy.io.wavfile as wav
import streamlit as st
import json
import os
from query_data import query_rag
from dotenv import load_dotenv
from voice_recorder import record_audio, speech_to_text_whisper
import hashlib

load_dotenv()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to load users and their messages from a single JSON file
def load_user_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

# Function to save users and their messages to a single JSON file
def save_user_data(users, filename):
    with open(filename, 'w') as file:
        json.dump(users, file)

# Function to clear messages for a specific user
def clear_user_messages(username, users):
    if username in users:
        users[username]['messages'] = []  # Clear messages for the user
    return users

# Define the Streamlit interface
st.title(":violet[Hermingarda] - Your PNA Assistant")

# User authentication section
users_file = "users_data.json"
users = load_user_data(users_file)

# Check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Registration and login forms
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])

    # Login tab
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if login_username in users and users[login_username]["password"] == hash_password(login_password):
                st.success(f"Welcome back, {login_username}!")
                st.session_state.logged_in = True
                st.session_state.username = login_username

                # Load messages for the logged-in user
                st.session_state.messages = users[login_username].get("messages", [])

                st.rerun()  # Force rerun to hide login/register after successful login
            else:
                st.error("Invalid username or password.")

    # Register tab
    with tab2:
        st.subheader("Register")
        register_username = st.text_input("Username", key="register_username")
        register_password = st.text_input("Password", type="password", key="register_password")

        if st.button("Register"):
            if register_username in users:
                st.error("Username already exists.")
            else:
                users[register_username] = {"password": hash_password(register_password), "messages": []}
                save_user_data(users, users_file)
                st.success("Registration successful! You can now log in.")

# If logged in, show the chat interface
if st.session_state.logged_in:
    username = st.session_state.username

    # Display chat messages in the main area
    if "messages" not in st.session_state:
        st.session_state.messages = users[username].get("messages", [])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input text box for the query
    if prompt := st.chat_input("Ask a question based on the medical research documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Fetch response using the query_rag function, passing the user prompt
        response = query_rag(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)

        # Save the updated messages to the JSON file
        users[username]["messages"] = st.session_state.messages
        save_user_data(users, users_file)

    # Sidebar for audio recording and clear chat history
    with st.sidebar:
        if st.button("Record Audio Query"):
            audio_file = record_audio()  # Record audio for 5 seconds
            transcribed_text = speech_to_text_whisper(audio_file)

            st.session_state.messages.append({"role": "user", "content": transcribed_text})

            response = query_rag(transcribed_text)
            st.session_state.messages.append({"role": "assistant", "content": response})

            users[username]["messages"] = st.session_state.messages
            save_user_data(users, users_file)

            st.rerun()

        # Clear chat history button
        if st.button("Clear Chat History"):
            st.session_state.messages = clear_user_messages(username, users)[username]['messages']
            save_user_data(users, users_file)
            st.success("Chat history cleared!")
            st.rerun()

    # Optional: Add a logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.messages = []
        st.rerun()

else:
    st.warning("Please log in or register to access the assistant.")

# Optional: Add a small space at the bottom for better UX
st.write("")