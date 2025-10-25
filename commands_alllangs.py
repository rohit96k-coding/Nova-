import re, webbrowser, datetime, wikipedia, pywhatkit, os, json
from langdetect import detect, DetectorFactory
from utils import safe_print

DetectorFactory.seed = 0

# Minimal translations for fixed responses; for other replies we will attempt to speak in detected language
TRANSLATIONS = {
    "greeting": {"english":"Hello! I'm Nova — your friendly assistant. How can I help?", "hindi":"नमस्ते! मैं नोवा हूँ — आपकी मदद के लिए तैयार हूँ।", "marathi":"नमस्कार! मी नोवा आहे — मी कशी मदत करू?" },
    "yes": {"english":"Yes?", "hindi":"जी बताइए?", "marathi":"हो, सांगा?" },
    "shutdown": {"english":"Shutting down. Bye!", "hindi":"शटडाउन कर रहा हूँ। अलविदा!", "marathi":"शटडाऊन होत आहे. निघतो!" },
    "unknown": {"english":"Sorry, I didn't understand. Could you rephrase?", "hindi":"माफ़ कीजिए, मैं समझ नहीं पाया। क्या आप दोहरा सकते हैं?", "marathi":"माफ करा, मला समजले नाही. पुन्हा सांगा."}
}

def detect_lang(text):
    try:
        lang = detect(text)
        if lang.startswith("hi"): return "hindi"
        if lang.startswith("mr"): return "marathi"
        if lang.startswith("en"): return "english"
        if lang.startswith("es"): return "spanish"
        if lang.startswith("fr"): return "french"
        if lang.startswith("de"): return "german"
        if lang.startswith("pt"): return "portuguese"
        if lang.startswith("ru"): return "russian"
        if lang.startswith("zh"): return "chinese"
        if lang.startswith("ja"): return "japanese"
        if lang.startswith("ko"): return "korean"
        if lang.startswith("ar"): return "arabic"
        if lang.startswith("bn"): return "bengali"
        if lang.startswith("ur"): return "urdu"
        if lang.startswith("pa"): return "punjabi"
        if lang.startswith("ta"): return "tamil"
        if lang.startswith("te"): return "telugu"
        if lang.startswith("kn"): return "kannada"
        return "english"
    except Exception:
        return "english"

class CommandHandler:
    def __init__(self, tts, assistant):
        self.tts = tts
        self.assistant = assistant
        self.shutdown_requested = False

    def translate(self, key, lang_name):
        return TRANSLATIONS.get(key, {}).get(lang_name, TRANSLATIONS.get(key, {}).get("english",""))

    def handle(self, text):
        raw = text.strip()
        lang = detect_lang(raw)
        safe_print(f"Detected language: {lang}")
        if lang != self.assistant.lang_key:
            self.assistant.set_language(lang)

        txt = raw.lower()

        # language switch by phrase like "language spanish" or "speak french"
        mlang = re.search(r'\b(language|speak)\s+(\w+)\b', txt)
        if mlang:
            langname = mlang.group(2)
            ok = self.assistant.set_language(langname)
            if ok:
                return f"Language set to {langname}."
            else:
                return f"Language {langname} not supported."

        if re.search(r'create .*website|make .*website|build .*website|website for', txt):
            return self._handle_create_website(raw)

        if re.search(r'whatsapp|send .*whatsapp|message .*whatsapp|send message', txt):
            return self._handle_whatsapp(raw)

        if re.search(r'solve|help me with|fix my|problem', txt):
            return self._handle_solve_problem(raw)

        if any(x in txt for x in ["time", "what time", "कितने बजे", "वेळ", "hora", "temps"]):
            now = datetime.datetime.now()
            responses = {"english":f"The time is {now.strftime('%I:%M %p')}", "hindi":f"समय है {now.strftime('%I:%M %p')}", "marathi":f"वेळ आहे {now.strftime('%I:%M %p')}"}
            return responses.get(self.assistant.lang_key, responses["english"])

        if txt.startswith("play") or ("play" in txt and "youtube" in txt):
            song = re.sub(r'play|on youtube|youtube', '', txt).strip()
            if not song:
                return "What should I play?"
            try:
                pywhatkit.playonyt(song)
                return f"Playing {song} on YouTube"
            except Exception as e:
                safe_print("pywhatkit error:", e)
                return "Couldn't open YouTube."

        if txt.startswith("search") or "search" in txt or "खोज" in txt:
            q = re.sub(r'search for|search|खोज|शोधा', '', txt, flags=re.I).strip()
            if not q:
                return "What should I search for?"
            webbrowser.open(f"https://www.google.com/search?q={q.replace(' ','+')}")
            return f"Searching Google for {q}"

        if "note" in txt or "remember" in txt or "नोट" in txt:
            note = re.sub(r'note|remember|नोट|नोट करा|स्मरण', '', txt, flags=re.I).strip()
            if not note:
                return "What should I note?"
            try:
                with open("data/notes.txt","a",encoding="utf-8") as f:
                    f.write(f"{datetime.datetime.now().isoformat()} - {note}\n")
                return "Okay, noted."
            except Exception as e:
                safe_print("Note save error:", e)
                return "Couldn't save the note."

        if txt.startswith("who is") or txt.startswith("what is") or "wikipedia" in txt:
            subj = re.sub(r'who is|what is|wikipedia', '', txt, flags=re.I).strip()
            if not subj:
                return "What do you want me to look up?"
            try:
                summary = wikipedia.summary(subj, sentences=2)
                return summary
            except Exception as e:
                safe_print("Wikipedia error:", e)
                webbrowser.open(f"https://www.google.com/search?q={subj.replace(' ','+')}")
                return f"I searched the web for {subj}."

        if any(x in txt for x in ["shutdown","quit","exit","stop listening","goodbye","बंद"]):
            self.shutdown_requested = True
            return self.translate("shutdown", self.assistant.lang_key)

        return self.translate("unknown", self.assistant.lang_key)

    def _handle_create_website(self, text):
        desc = text
        m = re.search(r'website (?:that|which|for)? (.*)', text, flags=re.I)
        if m:
            desc = m.group(1).strip()
        outdir = os.path.join("output","website")
        os.makedirs(outdir, exist_ok=True)
        index_html = f"""<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>My Nova Website</title>
  <link rel='stylesheet' href='styles.css'>
</head>
<body>
  <header><h1>My Nova Website</h1></header>
  <main>
    <p>{desc}</p>
    <section id='contact'>
      <h2>Contact</h2>
      <form>
        <input placeholder='Your name' required><br>
        <input placeholder='Your email' required><br>
        <textarea placeholder='Message'></textarea><br>
        <button type='submit'>Send</button>
      </form>
    </section>
  </main>
  <footer>Generated by Nova</footer>
  <script src='app.js'></script>
</body>
</html>"""
        css = """body { font-family: Arial, sans-serif; margin: 20px; padding:0; background:#f9f9f9; color:#333 }
header { background:#005f73; color:white; padding: 10px 20px; border-radius:6px }
main { margin-top:20px }
#contact { background:white; padding:15px; border-radius:6px; box-shadow:0 0 6px rgba(0,0,0,0.06) }
form input, form textarea { width:100%; padding:8px; margin:6px 0 }"""
        js = """console.log('Nova site loaded');"""
        with open(os.path.join(outdir,"index.html"),"w",encoding="utf-8") as f:
            f.write(index_html)
        with open(os.path.join(outdir,"styles.css"),"w",encoding="utf-8") as f:
            f.write(css)
        with open(os.path.join(outdir,"app.js"),"w",encoding="utf-8") as f:
            f.write(js)
        return f"I created a website scaffold under {outdir}. Open index.html to view it."

    def _handle_whatsapp(self, text):
        num_match = re.search(r'\+?\d{10,15}', text)
        if num_match:
            number = num_match.group(0)
            m2 = re.search(r'(?:say|message|text) (.*)', text, flags=re.I)
            msg = m2.group(1).strip() if m2 else "Hi"
            try:
                pywhatkit.sendwhatmsg_instantly(number, msg, wait_time=10, tab_close=True)
                return f"Sent WhatsApp message to {number}."
            except Exception as e:
                safe_print("pywhatkit error:", e)
                return "Failed to send WhatsApp message. Make sure WhatsApp Web is logged in."
        else:
            return "Please include a phone number like +911234567890 in the command."

    def _handle_solve_problem(self, text):
        subj = re.sub(r'(solve|help me with|fix my|problem)', '', text, flags=re.I).strip()
        if not subj:
            return "Tell me the problem in one sentence and I'll try to help."
        try:
            summary = wikipedia.summary(subj, sentences=3)
            return summary
        except Exception as e:
            safe_print("wikipedia error:", e)
            webbrowser.open(f"https://www.google.com/search?q={subj.replace(' ','+')}")
            return f"I couldn't find a concise answer; I searched the web for {subj}."