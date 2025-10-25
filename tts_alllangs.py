import os, time
from gtts import gTTS
from playsound import playsound
import pyttsx3
from utils import safe_print

class TTS:
    def __init__(self, use_gtts=True, temp_path="data/tts_temp.mp3", default_lang="english", lang_map=None):
        self.use_gtts = use_gtts
        self.temp_path = temp_path
        self.lang = default_lang
        self.lang_map = lang_map or {}
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 150)
            safe_print("pyttsx3 ready")
        except Exception as e:
            safe_print("pyttsx3 init failed:", e)
            self.engine = None

    def set_language(self, lang_name):
        self.lang = lang_name

    def _gtts_speak(self, text):
        try:
            gcode = self.lang_map.get(self.lang, {}).get("gtts", "en")
            tts = gTTS(text=text, lang=gcode)
            dirpath = os.path.dirname(self.temp_path)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            tts.save(self.temp_path)
            playsound(self.temp_path)
            time.sleep(0.2)
            return True
        except Exception as e:
            safe_print("gTTS error:", e)
            return False

    def _pyttsx3_speak(self, text):
        if not self.engine:
            return False
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            safe_print("pyttsx3 speak error:", e)
            return False

    def speak(self, text, block=True):
        if not text:
            return
        safe_print(f"Nova ({self.lang}) -> {text}")
        if self.use_gtts:
            ok = self._gtts_speak(text)
            if ok:
                return
        self._pyttsx3_speak(text)

    def shutdown(self):
        try:
            if self.engine:
                self.engine.stop()
        except Exception:
            pass