## CIS4990 Project: Simple Voice Assistant with The OpenAI API

### Team Members:

- Hasibuzzaman Tonmoy
- Cameron Johnson
- Don Ho
- Keith Krizka

### Project Description:

This project is a simple voice assistant that uses the OpenAI API to generate responses to user input. The voice assistant is able to answer questions, provide information, and perform simple tasks. The project uses Tkinter for the GUI, GTTS (Google Text-to-Speech) for text-to-speech conversion, and SpeechRecognition for speech-to-text conversion. The OpenAI API is used to generate responses to user input.

### Instructions:

Make sure you have Python 3.9 or later installed on your system. You also need Node.js 18 or later and NPM installed on your system to run the UI.

1. Install the required packages using the following commands sequentially:

```
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

**Note:** If you are using a virtual environment, make sure to activate it before running the above commands. If any of the Python packages fail to build, run the following command:

```
pip install wheel --no-cache-dir
```

2. Create a new file named `.env` in the root directory of the project and add the following lines to it:

```
OPENAI_API_KEY="your_openai_api_key"
```

_Don't forget to replace `your_openai_api_key` with your actual OpenAI API key._

3. Run the program using the following command:

```
python main.py
```
