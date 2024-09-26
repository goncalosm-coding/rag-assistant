import sounddevice as sd
import whisper
import scipy.io.wavfile as wav
import streamlit as st
import json
import os
from query_data import query_rag
from dotenv import load_dotenv
from voice_recorder import record_audio, speech_to_text_whisper

load_dotenv()

# Function to load messages from a JSON file
def load_messages(filename):
    if os.path.exists(filename):  # Check if the file exists
        with open(filename, 'r') as file:
            return json.load(file)  # Load messages from the file
    return []  # Return an empty list if the file does not exist

# Function to save messages to a JSON file
def save_messages(messages, filename):
    with open(filename, 'w') as file:
        json.dump(messages, file)  # Write messages to the file

# Function to clear messages
def clear_messages(filename):
    if os.path.exists(filename):  # Check if the file exists
        os.remove(filename)  # Remove the file
    return []  # Return an empty list for messages

# Define the Streamlit interface
st.title("Hermingarda - Your PNA Assistant")

# Initialize session state for OpenAI model and messages
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"  # Set the model you want to use

# Load previous messages from a JSON file
message_file = "messages.json"
if "messages" not in st.session_state:
    st.session_state.messages = load_messages(message_file)  # Load messages at startup

# Display chat messages in the main area
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])  # Render each message in the chat interface

# Input text box for the query
if prompt := st.chat_input("Ask a question based on the medical research documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})  # Add user prompt to messages
    with st.chat_message("user"):
        st.markdown(prompt)  # Render user message in the chat interface

    # Fetch response using the query_rag function, passing the user prompt
    response = query_rag(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})  # Add assistant response to messages

    with st.chat_message("assistant"):
        st.markdown(response)  # Render assistant message in the chat interface

    # Save the updated messages to the JSON file
    save_messages(st.session_state.messages, message_file)

# Sidebar for audio recording and clear chat history
with st.sidebar:  # Single sidebar for both functionalities
    if st.button("Record Audio Query"):
        audio_file = record_audio()  # Record audio for 5 seconds
        transcribed_text = speech_to_text_whisper(audio_file)  # Transcribe audio to text

        # Append the transcribed text as a user prompt
        st.session_state.messages.append({"role": "user", "content": transcribed_text})  # Add user prompt to messages
        
        # Fetch response using the query_rag function, passing the transcribed text
        response = query_rag(transcribed_text)
        st.session_state.messages.append({"role": "assistant", "content": response})  # Add assistant response to messages

        # Save the updated messages to the JSON file
        save_messages(st.session_state.messages, message_file)

        # Render the transcribed message and response immediately in the main chat area
        st.rerun()  # Trigger a rerun to update the UI

    # Clear chat history button in the same sidebar
    if st.button("Clear Chat History"):
        st.session_state.messages = clear_messages(message_file)  # Clear messages from session state and file
        st.success("Chat history cleared!")  # Show a success message

        # Clear displayed messages immediately
        st.session_state.messages = []  # Clear messages from session state
        st.rerun()  # Trigger a rerun to update the UI

# Optional: Add a small space at the bottom for better UX
st.write("")  # Just a placeholder for spacing