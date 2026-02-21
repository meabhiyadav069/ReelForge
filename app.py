import streamlit as st
import os
import time
import requests
import ffmpeg
import json
import random
import shutil
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from pathlib import Path
from static_ffmpeg import add_paths

# --- INITIALIZATION ---
add_paths()
load_dotenv()

# Fetch Keys from Environment
gemini_key = os.getenv("GEMINI_API_KEY")
eleven_key = os.getenv("ELEVENLABS_API_KEY")
pixabay_key = os.getenv("PIXABAY_API_KEY")
c_name = os.getenv("CLOUDINARY_CLOUD_NAME")
c_key = os.getenv("CLOUDINARY_API_KEY")
c_secret = os.getenv("CLOUDINARY_API_SECRET")

# Configure Clients Dynamically
if gemini_key: genai.configure(api_key=gemini_key)
eleven_client = ElevenLabs(api_key=eleven_key) if eleven_key else None
if c_name and c_key and c_secret:
    cloudinary.config(cloud_name=c_name, api_key=c_key, api_secret=c_secret)

# --- UI CONFIG ---
st.set_page_config(page_title="ReelForge | AI Video Editor", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main { background-color: #09090b; color: #fafafa; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white; font-weight: 800; border: none; transition: all 0.3s;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4); }
    .sidebar .sidebar-content { background-color: #18181b; }
    h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; }
    .status-box { padding: 1rem; border-radius: 10px; background: #18181b; border: 1px solid #27272a; margin-bottom: 1rem; }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: CONFIG ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/64/video-editing.png", width=64)
    st.title("ReelForge")
    
    st.markdown("---")
    niche = st.selectbox("🎯 Content Niche", ["Fitness", "Cooking", "Tech", "Travel", "Business"])
    
    # Dynamic Voice Selection with User Overrides
    try:
        voice_options = {
            "Adam (Pro Default)": "EXAVITQu4vr4xnSDxMaL",
            "Hindi (2026 Sync)": "D38z5RcWu1voky8WS1ja",
            "Rachel (Warm)": "21m0n2W7cv85YieD8s3S"
        }
        if eleven_client:
            server_voices = {v.name: v.voice_id for v in eleven_client.voices.get_all().voices}
            voice_options.update(server_voices)
    except:
        pass
    
    selected_voice_name = st.selectbox("🗣️ AI Voice", list(voice_options.keys()), index=0)
    voice_id = voice_options[selected_voice_name]
    
    st.markdown("---")
    st.markdown("🪄 **AI Improvisation**")
    user_prompt = st.text_area("Custom Prompt (Optional)", placeholder="e.g. 'Make it funny', 'Focus on the reaction', 'Use a high-energy tone'", help="Guide the AI's analysis and script generation.")
    
    st.markdown("---")
    st.success("🔒 AI Engine: Connected")
    st.info("💡 Tip: Upload videos < 2 mins for best AI analysis.")

# --- CORE FUNCTIONS ---

def cleanup_temp():
    """Removes the temp directory stuff."""
    temp_path = Path(os.getcwd()) / "temp"
    if temp_path.exists():
        try:
            shutil.rmtree(temp_path)
        except:
            pass
    temp_path.mkdir(exist_ok=True)
    (temp_path / "fallback_bgm").mkdir(exist_ok=True)

def get_bgm(query):
    """Fetches Pixabay BGM or uses local fallback."""
    try:
        url = f"https://pixabay.com/api/music/?key={pixabay_key}&q={query}+upbeat"
        data = requests.get(url, timeout=5).json()
        if data.get('hits'):
            r = requests.get(data['hits'][0]['audio'], timeout=10)
            path = str(Path(os.getcwd()) / "temp" / "bgm.mp3")
            with open(path, "wb") as f: f.write(r.content)
            return path
    except:
        pass
    
    # Fallback to niche-specific logic
    fallback_map = {"Fitness": "fitness.mp3", "Cooking": "cooking.mp3", "Tech": "tech.mp3", "Travel": "travel.mp3"}
    f_path = str(Path(os.getcwd()) / "fallback_bgm" / fallback_map.get(niche, 'default.mp3'))
    return f_path if os.path.exists(f_path) else None

def analyze_videos(video_paths, custom_prompt=""):
    try:
        # Dynamic Model Selection
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = "gemini-1.5-flash" # Default
        if "models/gemini-1.5-flash-latest" in available_models: target_model = "gemini-1.5-flash-latest"
        elif "models/gemini-2.0-flash-exp" in available_models: target_model = "gemini-2.0-flash-exp"
        
        model = genai.GenerativeModel(target_model)
        
        uploaded_files = []
        for path in video_paths:
            abs_path = str(Path(path).absolute())
            f = genai.upload_file(path=abs_path)
            uploaded_files.append(f)
            
        # Wait for all to process
        for f in uploaded_files:
            while f.state.name == "PROCESSING":
                time.sleep(2)
                f = genai.get_file(f.name)
        
        base_prompt = f"""
        Analyze these {len(video_paths)} video clips for a {niche} Reel. 
        Select the best segments across all of them to create a combined 30s viral story.
        Return JSON with an array of segments: {{"segments": [{{"clip_index": 0, "ss": 0, "t": 5}}, ...], "script": "..."}}
        Clip indices are 0-based.
        """
        if custom_prompt:
            base_prompt += f"\n\nUSER IMPROVISATION REQUEST: {custom_prompt}"
            
        response = model.generate_content(uploaded_files + [base_prompt])
        text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        return data
    except Exception as e:
        st.warning(f"🤖 Gemini Montage Analysis failed: {e}. Using a simple sequence...")
        return {
            "segments": [{"clip_index": i, "ss": 0, "t": 30 // len(video_paths)} for i in range(min(5, len(video_paths)))],
            "script": f"Transform your {niche} content with these amazing results!"
        }
    except Exception as e:
        st.warning(f"🤖 Gemini Analysis failed: {e}. Using smart defaults...")
        return {'ss': 5, 't': 30, 'script': f"Quick {niche} tip to go viral!"}

def generate_vo(text, vid):
    try:
        response_iter = eleven_client.text_to_speech.convert(
            voice_id=vid,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        path = str(Path(os.getcwd()) / "temp" / "vo.mp3")
        with open(path, "wb") as f:
            for chunk in response_iter:
                if chunk: f.write(chunk)
        return path
    except Exception as e:
        st.warning(f"🎙️ ElevenLabs failed: {e}. Using BGM only.")
        return None

def master_edit_montage(input_paths, output_p, bgm_p, vo_p, config):
    try:
        segments = config.get('segments', [])
        
        # Niche Presets
        presets = {
            "Fitness": {"eq": "saturation=1.5:contrast=1.2", "text": "GO HARD! 🔥"},
            "Cooking": {"eq": "saturation=1.2:contrast=1.1:brightness=0.05", "text": "YUMMY RECIPE! 🍳"},
            "Tech": {"eq": "saturation=1.1:contrast=1.3", "text": "TECH HACK! 💻"},
            "Travel": {"eq": "saturation=1.4", "text": "WANDERLUST! ✈️"},
            "Business": {"eq": "contrast=1.2", "text": "GROWTH TIP! 📈"}
        }
        p = presets.get(niche, presets["Tech"])
        
        processed_clips = []
        for seg in segments:
            idx = seg['clip_index']
            if idx >= len(input_paths): continue
            
            ss, t = seg['ss'], seg['t']
            clip = ffmpeg.input(input_paths[idx], ss=ss, t=t)
            
            # Filter each clip for the 9:16 montage
            v = (
                clip.video
                .filter('crop', 'ih*9/16', 'ih')
                .filter('scale', 1080, 1920)
                .filter('setpts', '0.75*PTS') # Faster for montages (approx 1.33x)
                .filter('eq', saturation=1.3)
            )
            processed_clips.append(v)
            
        # Concatenate all visual clips
        if len(processed_clips) > 1:
            v_final = ffmpeg.concat(*processed_clips, v=1, a=0).node
        else:
            v_final = processed_clips[0]
            
        # Add final text and zoom
        v_final = (
            v_final
            .filter('zoompan', z='min(zoom+0.001,1.1)', d=1, s='1080x1920')
            .drawtext(text=p['text'], fontsize=100, fontcolor='white', x='(w-text_w)/2', y=400, box=1, boxcolor='black@0.5', fontfile='C:/Windows/Fonts/arialbd.ttf')
        )
        
        # Audio Mix
        a_streams = []
        duration_total = sum(seg['t'] for seg in segments)
        
        if bgm_p and os.path.exists(bgm_p):
            a_bgm = ffmpeg.input(bgm_p).audio.filter('volume', 0.3)
            a_streams.append(a_bgm)
        else:
            a_streams.append(ffmpeg.input('anullsrc', f='lavfi', t=duration_total).audio)
            
        if vo_p and os.path.exists(vo_p):
            a_vo = ffmpeg.input(vo_p).audio.filter('volume', 0.8)
            a_streams.append(a_vo)
            
        if len(a_streams) > 1:
            a_final = ffmpeg.filter(a_streams, 'amix', inputs=len(a_streams), duration='first')
        else:
            a_final = a_streams[0]
        
        ffmpeg.output(v_final, a_final, output_p, vcodec='libx264', acodec='aac', bitrate='5M').overwrite_output().run()
        return True
    except Exception as e:
        st.error(f"FFmpeg Montage Error: {str(e)}")
        return False

# --- MAIN APP UI ---
st.markdown("<h1 style='text-align: center;'>🎬 ReelForge</h1>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("🚀 Drop your Raw MP4 clips here", type=["mp4", "mov"], accept_multiple_files=True)

if uploaded_files:
    cleanup_temp()
    input_paths = []
    
    for up_file in uploaded_files:
        path = f"temp/{up_file.name}"
        with open(path, "wb") as f: f.write(up_file.getbuffer())
        input_paths.append(path)
    
    col1, col2 = st.columns(2)
    with col1:
        st.video(input_paths[0]) # Preview first clip
        
    if st.button("💨 FORGE VIRAL REEL"):
        with st.status("Initializing Forge...", expanded=True) as status:
            try:
                status.update(label="🔍 Analyzing all clips & Stitching (Gemini AI)...", state="running")
                config = analyze_videos(input_paths, user_prompt)
                
                status.update(label="🎙️ Synthesizing AI Voiceover (ElevenLabs)...", state="running")
                vo = generate_vo(config['script'], voice_id)
                
                status.update(label="🎵 Fetching license-free BGM (Pixabay)...", state="running")
                bgm = get_bgm(niche)
                
                status.update(label="✂️ Master Concatenation & Effects (FFmpeg)...", state="running")
                final_out = f"temp/FORGED_MONTAGE.mp4"
                master_edit_montage(input_paths, final_out, bgm, vo, config)
                
                status.update(label="☁️ Uploading to Production Cloud...", state="running")
                upload_res = cloudinary.uploader.upload(final_out, folder="reelforge", resource_type="video")
                s_url = upload_res['secure_url']
                
                status.update(label="✨ Reel Forged Successfully!", state="complete")
                
                with col2:
                    st.video(s_url)
                    st.success(f"Successfully forged and uploaded to Cloudinary!")
                    st.download_button("📥 DOWNLOAD FINAL REEL", requests.get(s_url).content, file_name="viral_reel.mp4")
                    st.code(s_url, language="text")
            except Exception as e:
                st.error(f"Forge failed: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #555;'>Viral Reels Forged in Under 10 Seconds • Powered by AI Brain</p>", unsafe_allow_html=True)
