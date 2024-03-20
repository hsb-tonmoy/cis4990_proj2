import os
from dotenv import load_dotenv
import customtkinter
import speech_recognition as sr
import gtts
from openai import OpenAI
import playsound
import threading
from PIL import Image

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")


class VoiceAssistantApp(customtkinter.CTk):
  def __init__(self):
    super().__init__()
    
    self.geometry("400x360")
    self.title("Voice Assistant")

    image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))

    customtkinter.CTkLabel(self, text="Press the button and start speaking", fg_color="transparent", justify=customtkinter.CENTER).pack(pady=10, padx=10)
    self.mic_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "mic.png")), size=(48, 48))
    self.stop_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "stop.png")), size=(48, 48))
    self.mic_button = customtkinter.CTkButton(self, image=self.mic_image, text="", fg_color="transparent", hover=False, corner_radius=500, width=48, height=48,  command=self.process_voice_command)
    self.mic_button.pack(pady=10, padx=10)
    self.listening_text = customtkinter.CTkLabel(self, text="", fg_color="transparent")
    self.listening_text.pack(pady=10, padx=10)
    self.user_input = customtkinter.CTkLabel(self, text="Your Response:", fg_color="transparent")
    self.user_input.pack(pady=10, padx=10)
    
    self.response_text = customtkinter.CTkLabel(self, text="", fg_color="transparent")
    self.response_text.pack(pady=10, padx=10)


  def recognize_speech(self):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        self.listening_text.configure(text="Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        return text
    except Exception as e:
        print(e)
        return ""
    
  @staticmethod
  def send_to_chatgpt(text):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": "You are a helpful assistant designed to test a speech to text AI command app."},
    {"role": "user", "content": text}
  ],
    max_tokens=150)
    return response.choices[0].message.content
  
  @staticmethod
  def text_to_speech(text):
    tts = gtts.gTTS(text, lang='en')
    tts.save("response.mp3")
    playsound.playsound("response.mp3")

  def process_voice_command(self):
      self.mic_button.configure(image=self.stop_image)
      self.update_idletasks()  # Force update of the GUI
      threading.Thread(target=self.recognize_and_process_speech).start()
  
  def recognize_and_process_speech(self):
    recognized_text = self.recognize_speech()
    self.listening_text.configure(text="")
    self.user_input.configure(text= "Your Response: " + recognized_text)
    response = self.send_to_chatgpt(recognized_text)
    self.response_text.configure(text=response)
    threading.Thread(target=self.text_to_speech, args=(response,)).start()



if __name__ == "__main__":
  app = VoiceAssistantApp()
  app.mainloop()
