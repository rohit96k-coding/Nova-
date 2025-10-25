# Nova — All-Languages Multilingual Voice Assistant

This version of Nova supports many languages (English, Hindi, Marathi, Spanish, French, German, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Bengali, Urdu, Punjabi, Tamil, Telugu, Kannada and more) for listening and speaking.

Key features:
- Automatic language detection and switching.
- Ability to switch language by saying: "language <language name>" (e.g., "language spanish").
- Handles advanced intents: create website scaffold, send WhatsApp, web search, play YouTube, take notes, and attempt problem solving.
- Uses gTTS for TTS (supports the many languages above). Fallback to pyttsx3 if gTTS not available.

Run:
1. Unzip the package.
2. Create & activate virtualenv.
3. `pip install -r requirements.txt`
4. `python main.py`

Notes:
- gTTS and Google STT require internet.
- For offline STT, request VOSK version.
- For WhatsApp messaging, pywhatkit opens WhatsApp Web (you must be logged in).

