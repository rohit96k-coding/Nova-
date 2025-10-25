import json, os
from assistant_alllangs import NovaAssistant

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    config = load_config()
    assistant = NovaAssistant(config)
    print("Nova (all-languages) starting. Say the wake word (e.g. 'nova') or press Ctrl+C to quit.")
    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\nGoodbye — Nova shutting down.")
        assistant.shutdown()

if __name__ == "__main__":
    main()