from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import speech_recognition as sr
from io import BytesIO
import gtts
from openai import OpenAI
from dotenv import load_dotenv
import os
import subprocess
from flaskwebgui import FlaskUI

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Serve static files from the "public/assets" directory
app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

# Routes
@app.get("/", response_class=FileResponse)
async def main():
    """Serve the main HTML page."""
    return "public/index.html"

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech from an audio file to text."""
    audio_data = await audio.read()
    audio_buffer = BytesIO(audio_data)
    return recognize_speech(audio_buffer)

@app.post("/text-to-speech")
async def text_to_speech(text: str):
    """Convert text to speech."""
    return generate_speech_response(text)

@app.post("/send-to-chatgpt")
async def send_to_chatgpt_route(text: TextModel):
    """Send text to ChatGPT and return the response as speech."""
    response_text = send_to_chatgpt(text.text)
    return generate_speech_response(response_text, filename="response.mp3", chat_response=response_text)

# Utility functions
def recognize_speech(audio_buffer):
    """Recognize speech using Google's speech recognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_buffer) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return {"text": text}
    except sr.UnknownValueError:
        return {"error": "Speech recognition could not understand the audio"}
    except sr.RequestError as e:
        return {"error": f"Could not request results from the speech recognition service: {e}"}

def speak_text(text):
    """Convert text to speech and return an audio buffer."""
    tts = gtts.gTTS(text)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

def send_to_chatgpt(text):
    """Send text to OpenAI's ChatGPT and get a response."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to test a speech to text AI command app."},
            {"role": "user", "content": text}
        ])
    return response.choices[0].message.content

def generate_speech_response(text, filename="output.mp3", chat_response=None):
    """Generate a StreamingResponse for the given text-to-speech conversion."""
    audio_buffer = speak_text(text)
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    if chat_response is not None:
        headers["chat_response"] = chat_response
    return StreamingResponse(audio_buffer, media_type="audio/mpeg", headers=headers)

# Pydantic models for request bodies
class TextModel(BaseModel):
    text: str

# Main entry point for the application
if __name__ == "__main__":
    try:
        subprocess.check_call("cd frontend && npm run build", shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to build frontend: {e}")
        exit(1)
    FlaskUI(app=app, server="fastapi").run()
