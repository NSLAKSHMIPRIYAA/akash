import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ====== CONFIG ======
USERS = {
    "akash": "akash123",   # Akash's login
    "admin": "admin123"    # Your login
}

DATA_FILE = "grievances.csv"

# ====== FUNCTIONS ======
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["id", "user", "message", "response", "status", "timestamp"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ====== MAIN ======
st.title("💙 Akash & Priyaa's Grievance Portal")

# Login form
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login = st.sidebar.button("Login")

if login:
    if username in USERS and USERS[username] == password:
        st.success(f"Welcome, {username}!")

        df = load_data()

        # ----- Akash's Portal -----
        if username == "akash":
            st.subheader("Submit a Grievance")
            grievance = st.text_area("Write your grievance here:")
            if st.button("Submit"):
                if grievance.strip():
                    new_id = len(df) + 1
                    new_entry = {
                        "id": new_id,
                        "user": "akash",
                        "message": grievance,
                        "response": "",
                        "status": "Pending",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(df)
                    st.success("Grievance submitted successfully!")
                else:
                    st.warning("Please enter a grievance before submitting.")

            st.subheader("Your Grievances & Responses")
            akash_data = df[df["user"] == "akash"]
            if not akash_data.empty:
                for _, row in akash_data.iterrows():
                    st.markdown(f"**Message:** {row['message']}")
                    st.markdown(f"📌 Status: {row['status']}")
                    if row['response']:
                        st.markdown(f"💌 Response: {row['response']}")
                    st.write("---")
            else:
                st.info("No grievances yet.")

        # ----- Admin's Portal -----
        elif username == "admin":
            st.subheader("All Grievances")
            if not df.empty:
                for idx, row in df.iterrows():
                    st.markdown(f"**From Akash:** {row['message']}")
                    st.markdown(f"📌 Status: {row['status']}")
                    if row['response']:
                        st.markdown(f"💌 Your Response: {row['response']}")
                    else:
                        reply = st.text_area(f"Reply to grievance #{row['id']}", key=f"reply_{row['id']}")
                        if st.button(f"Send Reply #{row['id']}", key=f"btn_{row['id']}"):
                            df.at[idx, "response"] = reply
                            df.at[idx, "status"] = "Responded"
                            save_data(df)
                            st.success("Response sent!")
                    st.write("---")
            else:
                st.info("No grievances submitted yet.")

    else:
        st.error("Invalid username or password!")

