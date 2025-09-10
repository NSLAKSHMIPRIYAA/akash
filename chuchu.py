import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ===== CONFIG =====
USERS = {
    "akash": "akash123",
    "admin": "admin123"
}

# ===== FIREBASE SETUP =====
cred = credentials.Certificate("firebase_credentials.json")  # upload your Firebase JSON
firebase_admin.initialize_app(cred)
db = firestore.client()
messages_ref = db.collection("messages")

# ===== FUNCTIONS =====
def send_message(sender, message):
    messages_ref.add({
        "sender": sender,
        "message": message,
        "response": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def respond_message(doc_id, response):
    messages_ref.document(doc_id).update({
        "response": response
    })

def get_messages():
    docs = messages_ref.order_by("timestamp").stream()
    msgs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        msgs.append(data)
    return msgs

# ===== MAIN APP =====
st.title("💙 Akash & Priyaa's Portal")

# --- Login ---
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login = st.sidebar.button("Login")

if login:
    if username in USERS and USERS[username] == password:
        st.success(f"Welcome, {username}!")
        
        messages = get_messages()
        
        # --- Akash Portal ---
        if username == "akash":
            st.subheader("Send Your Feelings")
            feeling = st.text_area("Type your feelings here...")
            if st.button("Send"):
                if feeling.strip():
                    send_message("akash", feeling)
                    st.success("Sent!")
                else:
                    st.warning("Type something first.")

            st.subheader("Previous Conversations")
            for msg in messages:
                if msg["sender"] == "akash":
                    st.markdown(f"**You:** {msg['message']}")
                    if msg["response"]:
                        st.markdown(f"💌 Response: {msg['response']}")
                    st.markdown(f"*Sent at: {msg['timestamp']}*")
                    st.write("---")
        
        # --- Admin Portal ---
        elif username == "admin":
            st.subheader("All Messages")
            for msg in messages:
                if msg["sender"] == "akash":
                    st.markdown(f"**Akash:** {msg['message']}")
                    if msg["response"]:
                        st.markdown(f"💌 Your Response: {msg['response']}")
                    else:
                        reply = st.text_area(f"Reply to this message", key=msg["id"])
                        if st.button("Send Reply", key=f"btn_{msg['id']}"):
                            if reply.strip():
                                respond_message(msg["id"], reply)
                                st.success("Responded!")
                    st.markdown(f"*Sent at: {msg['timestamp']}*")
                    st.write("---")
    else:
        st.error("Invalid username or password!")
