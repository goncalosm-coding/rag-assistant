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

def load_user_data(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        return {}  # Return empty dictionary if the file doesn't exist or is empty

    with open(file_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            # If the file is not a valid JSON, return an empty dictionary
            return {}

# Function to save users and their messages to a single JSON file
def save_user_data(users, filename):
    with open(filename, 'w') as file:
        json.dump(users, file, indent=4)

# Function to clear messages for a specific user
def clear_user_messages(username, users):
    if username in users:
        users[username]['messages'] = []  # Clear messages for the user
    return users

# Function to forward messages with a watermark and icon
def forward_message(user_prompt, assistant_response, recipient, users, sender):
    if recipient in users:
        if users[recipient].get("receive_forwarded_messages", True):  # Check preference
            users[recipient]["messages"].append({
                "role": "user",
                "content": f"🔄 [Forwarded from {sender}]: {user_prompt}"  # Icon added
            })
            users[recipient]["messages"].append({
                "role": "assistant",
                "content": f"🔄 [Forwarded from {sender}]: {assistant_response}"  # Icon added
            })
            save_user_data(users, "users_data.json")
            return True
        else:
            return False  # User opted out of receiving forwarded messages
    return False

# Define the Streamlit interface
st.title(":violet[Hermingarda] - Your PNA Assistant")

# User authentication section
users_file = "users_data.json"
users = load_user_data(users_file)

# Check if user is logged in from the persisted JSON file
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# Check if any user is logged in from the file, and update session state
for user, data in users.items():
    if data.get("logged_in"):
        st.session_state.logged_in = True
        st.session_state.username = user
        st.session_state.messages = data.get("messages", [])
        break

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

                # Update the logged_in state in the JSON file
                users[login_username]["logged_in"] = True
                save_user_data(users, users_file)

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
                users[register_username] = {
                    "password": hash_password(register_password),
                    "messages": [],
                    "receive_forwarded_messages": True,  # Default preference
                    "logged_in": False  # User is not logged in by default
                }
                save_user_data(users, users_file)
                st.success("Registration successful! You can now log in.")

# If logged in, show the chat interface
if st.session_state.logged_in:
    username = st.session_state.username

    # Display chat messages in the main area
    if "messages" not in st.session_state:
        st.session_state.messages = users[username].get("messages", [])

    for idx, message in enumerate(st.session_state.messages):  # Use index for unique keys
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input text box for the query (main area)
    prompt = st.chat_input("Ask a question based on the medical research documents...")

    if prompt:
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

    # Sidebar for functionalities
    with st.sidebar:
        # User preferences
        st.subheader("User Preferences")
        receive_forwarded = st.checkbox("Receive Messages",
                                        value=users[username].get("receive_forwarded_messages"))
        users[username]["receive_forwarded_messages"] = receive_forwarded
        
        # Save Preferences button
        if st.button("Save Preferences"):
            save_user_data(users, users_file)  # Save preferences
            st.success("Preferences saved successfully!")

        # Add a separator line
        st.markdown("---")  # Horizontal line for separation

        # Show forward option if there are messages
        if len(st.session_state.messages) >= 2:
            last_user_message = st.session_state.messages[-2]["content"]
            last_assistant_message = st.session_state.messages[-1]["content"]

            recipient = st.selectbox("Forward to:", options=list(users.keys()), key="forward_recipient")
            if st.button("Forward", key="forward_button"):  # Unique key
                if forward_message(last_user_message, last_assistant_message, recipient, users, username):
                    st.success(f"Message forwarded to {recipient}!")
                else:
                    st.warning(f"{recipient} has opted out of receiving forwarded messages.")

        # Audio recording option
        if st.button("Record Audio"):
            audio_file = record_audio()
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

        # Ensure logout button stays at the bottom
        st.markdown("---")  # Another separator line
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.messages = []

            # Update the logged_in state in the JSON file
            users[username]["logged_in"] = False
            save_user_data(users, users_file)

            st.rerun()

else:
    st.warning("Please log in or register to access the assistant.")

# Optional: Add a small space at the bottom for better UX
st.write("")