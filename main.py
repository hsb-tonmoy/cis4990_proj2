from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
import os
import subprocess
from flaskwebgui import FlaskUI
import tempfile

load_dotenv()
 
app = FastAPI()

app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.get("/", response_class=FileResponse)
async def main():
    return "public/index.html"


voices = {
    'female': "shimmer",
    'male': "onyx",
}

class SettingsModel(BaseModel):
    voice: str
    expertise: str
    language: str

settings = SettingsModel(voice='female', expertise='default', language='en')

@app.post("/update-settings")
async def update_settings(new_settings: SettingsModel):
    global settings
    settings = new_settings
    print(f"Updated settings: {settings}")

def recognize_speech(audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_data.read())
        temp_file.seek(0)
        temp_file_path = temp_file.name
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=open(temp_file_path, "rb"),
        language=settings.language
    )

    os.unlink(temp_file_path)
    return response.text

def speak_text(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voices[settings.voice],
        response_format="mp3",
        input=text,
    )
    audio_data = response.read()
    audio_buffer = BytesIO(audio_data)
    audio_buffer.seek(0)
    return audio_buffer

def send_to_chatgpt(text):
    prompt = f"You are a helpful assistant with expertise in {settings.expertise}."
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": prompt},
    {"role": "user", "content": text}
    ])
    return response.choices[0].message.content

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    try:
        audio_data = await audio.read()
        audio_buffer = BytesIO(audio_data)
        text = recognize_speech(audio_buffer)
        return {"text": text}
    except Exception as e:
        print(f"Error in speech_to_text: {str(e)}")
        return {"error": "An error occurred during speech recognition. Please try again."}


@app.post("/text-to-speech")
async def text_to_speech(text: str):
    try:
        audio_buffer = speak_text(text)
        return StreamingResponse(audio_buffer, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class TextModel(BaseModel):
    text: str

@app.post("/send-to-chatgpt")
async def send_to_chatgpt_route(text: TextModel):
    try:
        response_text = send_to_chatgpt(text.text)

        audio_buffer = speak_text(response_text)

        return StreamingResponse(
            content=audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename=response.mp3",
                     "chat_response": response_text}
        )
    except Exception as e:
        print(f"Error in send_to_chatgpt: {str(e)}")
        return {"error": "An error occurred while processing the request. Please try again."}


if __name__ == "__main__":
    try:
        subprocess.check_call("cd frontend && npm run build", shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to build frontend: {e}")
        exit(1)
    FlaskUI(app=app, server="fastapi").run()