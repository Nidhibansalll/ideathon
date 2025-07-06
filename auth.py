import streamlit as st
import pandas as pd
import hashlib

USERS_FILE = "users.csv"

# Hashing passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load users
def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Username", "Password", "Role"])

# Save users
def save_users(users_df):
    users_df.to_csv(USERS_FILE, index=False)

# Login logic
def login_user(username, password):
    users = load_users()
    hashed = hash_password(password)
    user = users[(users["Username"] == username) & (users["Password"] == hashed)]
    if not user.empty:
        return user.iloc[0]["Role"]
    return None

# Register new user
def register_user(username, password, role):
    users = load_users()
    if username in users["Username"].values:
        return False
    new_user = pd.DataFrame([[username, hash_password(password), role]], columns=["Username", "Password", "Role"])
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True
