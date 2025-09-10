import streamlit as st
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app, get_app
import firebase_admin

# ====== CONFIG ======
USERS = {
    "akash": "akash123",
    "admin": "admin123"
}

# ====== FIREBASE SETUP ======
cred = credentials.Certificate("akash-d7c13-firebase-adminsdk-fbsvc-d358f0d9a8.json")

# Initialize Firebase only if not already initialized
try:
    app = get_app()
except ValueError:
    app = initialize_app(cred)

db = firestore.client()
messages_ref = db.collection("messages")

# ====== FUNCTIONS ======
def send_message(sender, message):
    """Send a new message to Firestore."""
    messages_ref.add({
        "sender": sender,
        "message": message,
        "response": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def respond_message(doc_id, response):
    """Send a response to a message in Firestore."""
    messages_ref.document(doc_id).update({
        "response": response
    })

def get_messages():
    """Fetch all messages ordered by timestamp."""
    docs = messages_ref.order_by("timestamp").stream()
    msgs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        msgs.append(data)
    return msgs


# ====== MAIN APP ======
st.title("💙 Akash & Priyaa's Portal")

# --- SESSION STATE FOR LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""

# --- LOGIN FORM ---
st.sidebar.header("Login")

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login = st.sidebar.button("Login")

    if login:
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("❌ Invalid username or password!")

else:
    username = st.session_state.user
    st.sidebar.success(f"Logged in as {username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()

    # --- Fetch Messages ---
    messages = get_messages()

    # ----- Akash Portal -----
    if username == "akash":
        st.subheader("💌 Send Your Feelings")

        if "feeling" not in st.session_state:
            st.session_state.feeling = ""

        st.session_state.feeling = st.text_area(
            "Type your feelings here...",
            value=st.session_state.feeling
        )

        if st.button("Send"):
            if st.session_state.feeling.strip():
                send_message("akash", st.session_state.feeling)
                st.success("Message sent!")
                st.session_state.feeling = ""  # Clear text area
                st.rerun()
            else:
                st.warning("Please type something first.")

        st.subheader("📜 Previous Conversations")
        for msg in messages:
            if msg["sender"] == "akash":
                st.markdown(f"<p style='color:blue'><b>You:</b> {msg['message']}</p>", unsafe_allow_html=True)
                if msg["response"]:
                    st.markdown(f"<p style='color:green'><b>Response:</b> {msg['response']}</p>", unsafe_allow_html=True)
                st.markdown(f"*Sent at: {msg['timestamp']}*")
                st.write("---")

    # ----- Admin Portal -----
    elif username == "admin":
        st.subheader("📜 All Messages from Akash")
        for msg in messages:
            if msg["sender"] == "akash":
                st.markdown(f"<p style='color:blue'><b>Akash:</b> {msg['message']}</p>", unsafe_allow_html=True)
                if msg["response"]:
                    st.markdown(f"<p style='color:green'><b>Your Response:</b> {msg['response']}</p>", unsafe_allow_html=True)
                else:
                    reply = st.text_area(f"Reply to this message", key=msg["id"])
                    if st.button("Send Reply", key=f"btn_{msg['id']}"):
                        if reply.strip():
                            respond_message(msg["id"], reply)
                            st.success("Response sent!")
                            st.rerun()
                st.markdown(f"*Sent at: {msg['timestamp']}*")
                st.write("---")
