# 🎬 ReelForge AI v2.0

**ReelForge** is a high-performance AI video editor that transforms raw MP4 clips into viral 9:16 reels in one click. Perfect for hackathons and quick content creation.

## 🚀 Features
- **AI Brain**: Gemini 1.5 Flash identifies optimal viral hooks.
- **Master Pipeline**: 1-pass FFmpeg chain (Crop, 1.1x Speed, Vibrance, Zoom-Pan, Text Burn).
- **Pro Audio**: ElevenLabs Voiceover + Pixabay Royalty-Free BGM mixing.
- **Cloud Powered**: Auto-uploads final exports to Cloudinary.
- **Mobile Ready**: Reactive Streamlit UI with drag/drop support.

## 🛠️ Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Credentials**:
   Create a `.env` file or use the **Sidebar UI** in the app to enter:
   - `GEMINI_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `PIXABAY_API_KEY`
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

## 🎯 Niche Presets
- **Fitness**: Vibrant colors & High Energy.
- **Cooking**: Warm tones & Smooth pacing.
- **Tech**: Futuristic contrast & Sharp cuts.
- **Travel**: Deep saturation & Cinematic zoom.

---
*Built for the Future of Content Creation.*
# ReelForge
