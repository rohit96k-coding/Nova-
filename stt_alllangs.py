import speech_recognition as sr
from utils import safe_print

class SpeechRecognizer:
    def __init__(self, language_code="en-IN"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language_code = language_code
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        safe_print("Adjusting microphone for ambient noise... (1s)")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def set_language(self, language_code):
        self.language_code = language_code
        safe_print(f"STT language set to {language_code}")

    def listen_for_phrase(self, timeout=None, phrase_time_limit=None):
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                return None
        try:
            text = self.recognizer.recognize_google(audio, language=self.language_code)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            safe_print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

    def shutdown(self):
        pass