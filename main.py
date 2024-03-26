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

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    # Load the audio file
    audio_data = await audio.read()

    # Create a BytesIO object from the audio data
    audio_buffer = BytesIO(audio_data)

    try:
        # Convert the audio data to WAV format using pydub
        audio_segment = AudioSegment.from_file(audio_buffer, format="wav")
        converted_audio_buffer = BytesIO()
        audio_segment.export(converted_audio_buffer, format="wav")
        converted_audio_buffer.seek(0)
    except pydub_exceptions.CouldntDecodeError as e:
        # Log the error and the received audio data
        print(f"Decoding error: {str(e)}")
        print(f"Received audio data: {audio_data}")
        return {"error": "Failed to decode audio"}

    # Create a speech recognition object
    recognizer = sr.Recognizer()

    # Load the converted WAV data
    with sr.AudioFile(converted_audio_buffer) as source:
        # Read the audio data
        audio = recognizer.record(source)

    try:
        # Perform speech recognition
        text = recognizer.recognize_google(audio)
        return {"text": text}
    except sr.UnknownValueError:
        return {"error": "Speech recognition could not understand the audio"}
    except sr.RequestError as e:
        return {"error": f"Could not request results from the speech recognition service: {e}"}