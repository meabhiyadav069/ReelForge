import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

try:
    voices = client.voices.get_all()
    print("Available Voices:")
    for voice in voices.voices:
        print(f"Name: {voice.name}, ID: {voice.voice_id}")
except Exception as e:
    print(f"Error fetching voices: {e}")
