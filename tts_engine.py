import asyncio
import edge_tts
import os
import tempfile
import uuid
import playsound

VOICE = "en-US-AriaNeural"
RATE = "+0%"

async def speak_async(text: str):
    # Use a unique temporary file to avoid conflicts
    temp_file = os.path.join(tempfile.gettempdir(), f"jarvis_tts_{uuid.uuid4().hex}.mp3")
    try:
        communicate = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
        await communicate.save(temp_file)
        playsound.playsound(temp_file)
    finally:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception:
            pass  # ignore rare Windows file-lock race

def speak(text: str):
    print(f"🗣️ Jarvis: {text}")
    asyncio.run(speak_async(text))