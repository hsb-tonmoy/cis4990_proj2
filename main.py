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

load_dotenv()
 
app = FastAPI()

app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

@app.get("/", response_class=FileResponse)
async def main():
    return "public/index.html"

def recognize_speech(audio_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        raise sr.UnknownValueError("Speech recognition could not understand the audio")
    except sr.RequestError as e:
        raise sr.RequestError(f"Could not request results from the speech recognition service: {e}")

def speak_text(text):
    tts = gtts.gTTS(text)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

def send_to_chatgpt(text):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(model="gpt-4",
    messages=[
    {"role": "system", "content": "You are a helpful assistant designed to test a speech to text AI command app."},
    {"role": "user", "content": text}
    ])
    return response.choices[0].message.content

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    audio_data = await audio.read()
    audio_buffer = BytesIO(audio_data)
    try:
        text = recognize_speech(audio_buffer)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}

@app.post("/text-to-speech")
async def text_to_speech(text: str):
    try:
        audio_buffer = speak_text(text)
        return StreamingResponse(audio_buffer, media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}
    
class TextModel(BaseModel):
    text: str

@app.post("/send-to-chatgpt")
async def send_to_chatgpt_route(text: TextModel):
    try:
        # Send text to ChatGPT and get response
        response_text = send_to_chatgpt(text.text)

        # Convert response text to speech
        audio_buffer = speak_text(response_text)

        # Return audio and text response
        return StreamingResponse(
            content=audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename=response.mp3",
                     "chat_response": response_text}
        )
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    try:
        subprocess.check_call("cd frontend && npm run build", shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to build frontend: {e}")
        exit(1)
    FlaskUI(app=app, server="fastapi").run()