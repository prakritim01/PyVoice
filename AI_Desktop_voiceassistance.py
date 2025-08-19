import asyncio
import edge_tts
import os
import tempfile
import uuid
import playsound
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import pyautogui
import subprocess
import smtplib
import ssl
import openai
from dotenv import load_dotenv
from tts_engine import speak

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------------------
# Email Functionality
# -------------------------------
def sendEmail(to, subject, body):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender, password)
            email_message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender, to, email_message)
        speak("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        speak("I am sorry, I was unable to send the email.")
        return False

# -------------------------------
# Speech Recognition
# -------------------------------
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("🔎 Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"👉 User said: {query}")
            return query
        except sr.WaitTimeoutError:
            speak("I didn’t hear anything. Please say that again.")
            return "none"
        except sr.UnknownValueError:
            speak("Sorry, I could not understand that.")
            return "none"
        except sr.RequestError:
            speak("Speech service is down. Please check your internet.")
            return "none"

# -------------------------------
# Greeting
# -------------------------------
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Jarvis. How can I help you today?")

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    try:
        wishMe()
        while True:
            query = takeCommand().lower()
            if query == "none":
                continue

            # ===== Direct Google Search =====
            if "search google for" in query:
                search_term = query.replace("search google for", "").strip()
                url = f"https://www.google.com/search?q={search_term}"
                speak(f"Searching Google for {search_term}")
                webbrowser.open(url)

            # 🔹 Improved YouTube Search
            elif "open youtube" in query:
                search_term = query.replace("open youtube", "").replace("search", "").strip()
                if search_term:
                    url = f"https://www.youtube.com/results?search_query={search_term}"
                    speak(f"Searching YouTube for {search_term}")
                    webbrowser.open(url)
                else:
                    speak("Opening YouTube...")
                    webbrowser.open("https://www.youtube.com")

            elif "search youtube for" in query:
                search_term = query.replace("search youtube for", "").strip()
                url = f"https://www.youtube.com/results?search_query={search_term}"
                speak(f"Searching YouTube for {search_term}")
                webbrowser.open(url)

            # 🔹 Improved Wikipedia (5 lines)
            elif "wikipedia" in query:
                speak("Searching Wikipedia...")
                q = query.replace("wikipedia", "").replace("search", "").strip()
                try:
                    results = wikipedia.summary(q, sentences=5)
                    speak(f"According to Wikipedia, here’s what I found about {q}")
                    print(results)
                    speak(results)
                except Exception:
                    speak("Sorry, I could not find anything on Wikipedia.")

            # 🔹 Conversational AI Integration
            elif "ask jarvis" in query:
                speak("What do you want to ask?")
                ai_query = takeCommand().lower()

                if ai_query != "none":
                    try:
                        speak("Thinking...")
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant named Jarvis."},
                                {"role": "user", "content": ai_query}
                            ],
                            max_tokens=150
                        )
                        ai_response = response.choices[0].message.content.strip()
                        print(f"🤖 AI Response: {ai_response}")
                        speak(ai_response)
                    except Exception as e:
                        print(f"Error calling OpenAI API: {e}")
                        speak("I'm sorry, I couldn't process that. The AI service may be unavailable.")
            
            # ===== Open websites =====
            elif "open google" in query:
                speak("Opening Google...")
                webbrowser.open("https://www.google.com")

            elif "open stackoverflow" in query:
                speak("Opening Stack Overflow...")
                webbrowser.open("https://stackoverflow.com")

            # ===== Spotify =====
            elif "play my songs" in query or "play music" in query:
                speak("Opening Spotify and playing your songs...")
                spotify_path = os.getenv("SPOTIFY_PATH")
                if spotify_path and os.path.exists(spotify_path):
                    try:
                        os.startfile(spotify_path)
                    except Exception:
                        speak("Sorry, I couldn't open Spotify. Please check the path in your .env file.")
                else:
                    speak("Spotify path not found. Please check your .env file.")

            # ===== Open Applications =====
            elif "open notepad" in query:
                speak("Opening Notepad...")
                try:
                    subprocess.Popen(["notepad.exe"])
                except Exception:
                    speak("I couldn't open Notepad.")

            elif "open calculator" in query:
                speak("Opening Calculator...")
                try:
                    subprocess.Popen(["calc.exe"])
                except Exception:
                    speak("I couldn't open Calculator.")

            elif "open chrome" in query:
                speak("Opening Google Chrome...")
                chrome_path = os.getenv("CHROME_PATH")
                if chrome_path and os.path.exists(chrome_path):
                    try:
                        subprocess.Popen([chrome_path])
                    except Exception:
                        speak("Chrome not found. Please check the path in your .env file.")
                else:
                    speak("Chrome path not found. Please check your .env file.")

            elif "open vscode" in query or "open vs code" in query or "open code" in query:
                speak("Opening Visual Studio Code...")
                vscode_path = os.getenv("VSCODE_PATH")
                if vscode_path and os.path.exists(vscode_path):
                    try:
                        subprocess.Popen([vscode_path])
                    except Exception:
                        speak("VS Code not found. Please check the path in your .env file.")
                else:
                    speak("VS Code path not found. Please check your .env file.")

            # ===== Take Screenshot (fixed) =====
            elif "take screenshot" in query or "screenshot" in query:
                try:
                    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    save_path = os.path.join(os.getcwd(), filename)
                    image = pyautogui.screenshot()
                    image.save(save_path)
                    speak(f"Screenshot saved as {filename}")
                    os.startfile(save_path)
                except Exception as e:
                    print("Screenshot error:", e)
                    speak("I couldn't take a screenshot right now.")

            # ===== Send Email =====
            elif "send an email" in query:
                try:
                    speak("Who do you want to send the email to?")
                    recipient = takeCommand().lower()
                    email_map = {
                        "john": "john.doe@example.com",
                        "dad": "dad_email@gmail.com"
                    }
                    if recipient in email_map:
                        to = email_map[recipient]
                        speak("What is the subject of the email?")
                        subject = takeCommand().lower()
                        speak("What do you want to say?")
                        body = takeCommand().lower()
                        sendEmail(to, subject, body)
                    else:
                        speak("Sorry, I don't know that recipient.")
                except Exception as e:
                    print(f"Email command error: {e}")
                    speak("I couldn't process the email request.")
                    
            # ===== Time =====
            elif "the time" in query or "what's the time" in query:
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                speak(f"Sir, the time is {strTime}")

            # ===== Quit =====
            elif "quit" in query or "exit" in query:
                speak("Goodbye! Have a nice day!")
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user (Ctrl+C)")
        speak("Goodbye, stopping now.")