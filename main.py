from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import speech_recognition as sr
from pydub import AudioSegment, exceptions as pydub_exceptions
from io import BytesIO
 
app = FastAPI()

app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

@app.get("/", response_class=FileResponse)
async def main():
    return "public/index.html"

def convert_audio(audio_data):
    audio_buffer = BytesIO(audio_data)
    try:
        audio_segment = AudioSegment.from_file(audio_buffer, format="webm")
        converted_audio_buffer = BytesIO()
        audio_segment.export(converted_audio_buffer, format="wav")
        converted_audio_buffer.seek(0)
        return converted_audio_buffer
    except pydub_exceptions.CouldntDecodeError as e:
        print(f"Decoding error: {str(e)}")
        print(f"Received audio data: {audio_data}")
        raise e

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

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    audio_data = await audio.read()
    try:
        converted_audio_data = convert_audio(audio_data)
        text = recognize_speech(converted_audio_data)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}