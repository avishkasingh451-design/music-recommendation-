import streamlit as st
import cv2
from deepface import DeepFace
import webbrowser
import os

# File to store user data
USER_DATA_FILE = "user_data.txt"

# Function to save user data
def save_user_data(username, password, language, singer):
    with open(USER_DATA_FILE, "a") as file:
        file.write(f"{username},{password},{language},{singer}\n")

# Function to load user data
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    user_data = {}
    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            username, password, language, singer = line.strip().split(",")
            user_data[username] = {"password": password, "language": language, "singer": singer}
    return user_data

# Function to detect emotion from the webcam
def detect_emotion():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Error: Could not open webcam.")
        return None

    st.write("Please look at the webcam and press 'Capture Emotion' below.")
    capture_button = st.button("Capture Emotion")

    if capture_button:
        ret, frame = cap.read()
        if not ret:
            st.error("Error: Could not read frame.")
            return None

        temp_image_path = "temp_frame.jpg"
        cv2.imwrite(temp_image_path, frame)

        try:
            result = DeepFace.analyze(temp_image_path, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            st.success(f"Detected Emotion: {emotion}")
            return emotion
        except Exception as e:
            st.error(f"Error analyzing emotion: {e}")
            return None
        finally:
            cap.release()
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

# Function to recommend music based on emotion and preferences
def recommend_music(emotion, language, singer):
    emotion_to_query = {
        "happy": f"{language} {singer} upbeat songs",
        "sad": f"{language} {singer} sad songs",
        "angry": f"{language} {singer} rock songs",
        "surprise": f"{language} {singer} dance songs",
        "fear": f"{language} {singer} calm songs",
        "disgust": f"{language} {singer} metal songs",
        "neutral": f"{language} {singer} lo-fi songs"
    }
    return emotion_to_query.get(emotion, f"{language} {singer} lo-fi songs")

# Main Streamlit app
def main():
    st.title("🎵 Emotion-Based Music Recommender 🎵")
    user_data = load_user_data()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.header("Register or Login")
        choice = st.sidebar.radio("Choose an option", ["Register", "Login"])

        if choice == "Register":
            st.subheader("Create a New Account")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            language = st.text_input("Preferred Music Language")
            singer = st.text_input("Favorite Singer/Band")
            if st.button("Register"):
                if username in user_data:
                    st.error("Username already exists. Please choose another.")
                else:
                    save_user_data(username, password, language, singer)
                    st.success("Registration successful! Please login.")

        elif choice == "Login":
            st.subheader("Login to Your Account")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if username in user_data and user_data[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.language = user_data[username]["language"]
                    st.session_state.singer = user_data[username]["singer"]
                    st.success("Login successful!")
                else:
                    st.error("Invalid username or password.")
    else:
        st.sidebar.header(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.clear()
            st.experimental_rerun()

        st.subheader("Music Preferences")
        st.write(f"Preferred Language: {st.session_state.language}")
        st.write(f"Favorite Singer/Band: {st.session_state.singer}")

        st.subheader("Detect Your Emotion")
        emotion = detect_emotion()

        if emotion:
            query = recommend_music(emotion, st.session_state.language, st.session_state.singer)
            st.write(f"Opening YouTube with the search query: {query}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

if __name__ == "__main__":
    main()
