import time
from stt_alllangs import SpeechRecognizer
from tts_alllangs import TTS
from commands_alllangs import CommandHandler
from utils import safe_print

class NovaAssistant:
    def __init__(self, config):
        self.config = config
        self.name = config.get("assistant_name","Nova")
        self.wake_words = [w.lower() for w in config.get("wake_words",["nova"])]
        self.lang_map = config.get("language_map", {})
        self.lang_key = config.get("default_language","english")
        self.current_stt_code = self.lang_map.get(self.lang_key, {}).get("stt","en-IN")
        self.current_gtts_key = self.lang_map.get(self.lang_key, {}).get("gtts","en")
        self.stt = SpeechRecognizer(self.current_stt_code)
        self.tts = TTS(config.get("use_gtts",True), config.get("gtts_temp_path","data/tts_temp.mp3"), default_lang=self.lang_key, lang_map=self.lang_map)
        self.commands = CommandHandler(self.tts, self)
        self.running = False

    def set_language(self, lang_name):
        lang_name = lang_name.lower()
        if lang_name not in self.lang_map:
            safe_print(f"Language {lang_name} not supported.")
            return False
        self.lang_key = lang_name
        self.current_stt_code = self.lang_map[lang_name]["stt"]
        self.current_gtts_key = self.lang_map[lang_name]["gtts"]
        self.stt.set_language(self.current_stt_code)
        self.tts.set_language(lang_name)
        safe_print(f"Language set to {lang_name} (STT {self.current_stt_code}, TTS {self.current_gtts_key})")
        return True

    def _is_wake(self, text):
        if not text:
            return False
        t = text.lower().strip()
        for w in self.wake_words:
            if t.startswith(w) or (" " + w + " ") in (" " + t + " "):
                return True
        return False

    def run(self):
        self.running = True
        self.tts.speak("Hello! I am Nova. Ready when you are.")
        while self.running:
            try:
                safe_print("Listening for wake word...")
                text = self.stt.listen_for_phrase(timeout=8, phrase_time_limit=6)
                safe_print(f"Pre-wake recognition: {text}")
                if self._is_wake(text or ""):
                    self.tts.speak("Yes?")
                    cmd_text = self.stt.listen_for_phrase(timeout=6, phrase_time_limit=12)
                    safe_print(f"Command recognized: {cmd_text}")
                    if cmd_text:
                        response = self.commands.handle(cmd_text)
                        if response:
                            self.tts.speak(response)
                        if self.commands.shutdown_requested:
                            self.tts.speak("Shutting down. Goodbye!")
                            self.shutdown()
                            break
                time.sleep(0.2)
            except Exception as e:
                safe_print(f"Error in main loop: {e}")
                time.sleep(1)

    def shutdown(self):
        self.running = False
        try:
            self.tts.shutdown()
            self.stt.shutdown()
        except Exception:
            pass