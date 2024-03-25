from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import speech_recognition as sr
import io
from pydub import AudioSegment
 
app = FastAPI()

# Define our static folder, where will be our svelte build later
app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

# Simply the root will return our Svelte build
@app.get("/", response_class=FileResponse)
async def main():
    return "public/index.html"

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    # Load the audio file
    audio_data = await audio.read()
    
    # Save the uploaded audio file temporarily
    with open("temp_audio.ogg", "wb") as file:
        file.write(audio_data)
    
    # Convert OGG to WAV using pydub
    audio_segment = AudioSegment.from_file("temp_audio.ogg", format="ogg")
    audio_segment.export("temp_audio.wav", format="wav")
    
    # Create a speech recognition object
    recognizer = sr.Recognizer()
    
    # Load the converted WAV file
    with sr.AudioFile("temp_audio.wav") as source:
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