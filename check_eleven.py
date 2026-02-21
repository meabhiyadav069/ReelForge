import elevenlabs
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

print(f"ElevenLabs version: {elevenlabs.__version__ if hasattr(elevenlabs, '__version__') else 'unknown'}")
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
print(f"Methods in ElevenLabs client: {dir(client)}")
