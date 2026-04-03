"""
Liminal Space — Premium Guided Door Track Generator
Rebuilds all 3 Door tracks with:
- Branded "Liminal Protocol" preparation
- Ambient soundscape (warm pad + filtered noise + subtle harmonics)
- Correct binaural frequencies verified
- Cinematic narration selling the Liminal Space as the destination
"""

import os
import requests
import numpy as np
import soundfile as sf
import subprocess
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, lfilter
import static_ffmpeg
static_ffmpeg.add_paths()

# Config
ELEVENLABS_KEY = "2d2522f3fb48a0cf326c9b72eb1c93366e809f5b350bfd86efc933fda3e21379"
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George — warm British storyteller (used for ad)
SR = 44100
DURATION = 20 * 60  # 20 minutes
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
TEMP_DIR = os.path.join(AUDIO_DIR, "temp_premium")

# ═══════════════════════════════════════════
# BINAURAL BEAT GENERATOR (with ambient layer)
# ═══════════════════════════════════════════

def generate_binaural_with_ambience(base_freq, beat_freq, filename):
    """Generate binaural beat with warm, immersive ambient soundscape."""
    out_path = os.path.join(AUDIO_DIR, filename)
    total = DURATION * SR
    t = np.linspace(0, DURATION, total, endpoint=False)

    # --- Binaural beat (correct Gateway frequencies) ---
    left_freq = base_freq
    right_freq = base_freq + beat_freq
    left = np.sin(2 * np.pi * left_freq * t) * 0.22
    right = np.sin(2 * np.pi * right_freq * t) * 0.22

    # --- Warm pad (additive synthesis, wider stereo) ---
    pad_freqs = [55, 82.5, 110, 165]  # A1 + harmonics (dropped 220 Hz to stay warm)
    pad_amps = [0.08, 0.05, 0.035, 0.015]  # Slightly louder ambient
    pad_left = np.zeros(total)
    pad_right = np.zeros(total)
    for f, a in zip(pad_freqs, pad_amps):
        # Slow LFO modulation for organic movement
        lfo_l = 1.0 + 0.12 * np.sin(2 * np.pi * 0.025 * t + np.random.random() * 6.28)
        lfo_r = 1.0 + 0.12 * np.sin(2 * np.pi * 0.027 * t + np.random.random() * 6.28)
        # Slight detuning between L/R for stereo width
        pad_left += a * np.sin(2 * np.pi * (f * 0.998) * t * lfo_l)
        pad_right += a * np.sin(2 * np.pi * (f * 1.002) * t * lfo_r)

    # --- Deep sub-bass drone (very subtle, adds warmth) ---
    drone_freq = 36.7  # D1 — deep, warm
    drone = np.sin(2 * np.pi * drone_freq * t) * 0.03
    drone_mod = 0.8 + 0.2 * np.sin(2 * np.pi * 0.015 * t)  # Very slow breathing
    drone *= drone_mod

    # --- Filtered pink noise for organic texture ---
    noise_l = np.random.randn(total) * 0.015
    noise_r = np.random.randn(total) * 0.015  # Independent noise per channel
    # Bandpass 60-300 Hz for warm, dark texture (lower than before)
    b_bp, a_bp = butter(2, [60 / (SR/2), 300 / (SR/2)], btype='band')
    noise_l = lfilter(b_bp, a_bp, noise_l)
    noise_r = lfilter(b_bp, a_bp, noise_r)

    # --- Low-pass filter on entire ambient to remove harshness ---
    # Gentle rolloff above 1500 Hz — ensures nothing sounds tinny or shrill
    b_lp, a_lp = butter(2, 1500 / (SR/2), btype='low')

    # --- Fade in/out (45 seconds for smoother experience) ---
    fade_in_len = int(45 * SR)
    fade_out_len = int(45 * SR)
    fade_in = np.linspace(0, 1, fade_in_len)
    fade_out = np.linspace(1, 0, fade_out_len)

    # Combine ambient layers
    ambient_left = pad_left + noise_l + drone
    ambient_right = pad_right + noise_r + drone

    # Apply low-pass to ambient (removes any harsh highs)
    ambient_left = lfilter(b_lp, a_lp, ambient_left)
    ambient_right = lfilter(b_lp, a_lp, ambient_right)

    # Mix binaural + ambient
    left_ch = left + ambient_left
    right_ch = right + ambient_right

    # Apply fades
    left_ch[:fade_in_len] *= fade_in
    right_ch[:fade_in_len] *= fade_in
    left_ch[-fade_out_len:] *= fade_out
    right_ch[-fade_out_len:] *= fade_out

    stereo = np.column_stack([left_ch, right_ch])

    # Normalize
    peak = np.max(np.abs(stereo))
    if peak > 0.9:
        stereo *= 0.9 / peak

    sf.write(out_path, stereo, SR, subtype='PCM_24')
    print(f"  Binaural + ambience: {filename}")
    return out_path


# ═══════════════════════════════════════════
# NARRATION SCRIPTS
# ═══════════════════════════════════════════

# The Liminal Protocol (shared across all Doors)
LIMINAL_PROTOCOL = [
    # Welcome
    (
        "Welcome to the Liminal Protocol. "
        "Over the next twenty minutes, you will be guided to the edge of ordinary consciousness "
        "and beyond it, into the Liminal Space. "
        "A space between spaces. Where physical laws become suggestions. "
        "Where the boundaries of self dissolve. "
        "Where you become limitless.",
        6
    ),
    # Setup
    (
        "Make sure you are lying down comfortably. "
        "Your eyes are closed. Your headphones are on. "
        "There is nothing you need to do. Nowhere you need to be. "
        "For the next twenty minutes, you belong entirely to yourself.",
        6
    ),
    # Energy Conversion Box
    (
        "We begin with the Conversion Box. "
        "Imagine a large, strong container in front of you. "
        "It has a heavy lid. "
        "Now take every thought you're carrying. "
        "Every worry. Every responsibility. Every conversation you're replaying. "
        "Every plan. Every fear. "
        "Place them all inside this box. "
        "One by one. Let each thought leave your mind and enter the box. "
        "Now close the lid. "
        "Everything will be there when you return. But right now, the box holds it.",
        8
    ),
    # Resonant Tuning
    (
        "Now we tune the body. "
        "Take a deep breath in through your nose. Fill your lungs completely.",
        4
    ),
    (
        "And exhale slowly through your mouth, letting out a long, low hum. "
        "Hmmmmm. "
        "Feel the vibration in your chest. In your throat. In your skull.",
        5
    ),
    ("Again. Deep breath in.", 4),
    (
        "And release. Let the vibration move through your entire body. "
        "You are tuning yourself like an instrument.",
        6
    ),
    ("One final breath. The deepest one yet.", 4),
    ("And let everything go.", 8),
    # Affirmation
    (
        "Now repeat silently in your mind: "
        "I am more than my physical body. "
        "I am more than what I can see and touch and hear. "
        "I deeply desire to expand my awareness "
        "beyond the limitations of my physical senses. "
        "I desire to know. To experience. To understand. "
        "I am ready to enter the Liminal Space.",
        8
    ),
    # Body Scan
    (
        "Now bring your awareness to your body. "
        "Feel the weight of your head against the surface beneath you. "
        "Let your jaw relax. Unclench your teeth. "
        "Let your shoulders drop away from your ears. "
        "Feel your arms become heavy. Your hands. Your fingers. "
        "Let them sink.",
        5
    ),
    (
        "Now your torso. Your chest rises and falls. "
        "Your stomach softens. "
        "Your hips release. Your legs grow heavy. "
        "Your feet relax. "
        "Allow your entire body to melt into the surface below you. "
        "You are safe. You are supported. "
        "Now let the body sleep.",
        8
    ),
]

# Door-specific scripts
DOORS = {
    "door-10": {
        "base_freq": 200,
        "beat_freq": 10,  # 10 Hz alpha
        "binaural_file": "door-10-base.wav",
        "output_name": "door-10-guided",
        "intro": [
            (
                "This is Door Ten. "
                "The first door. The threshold between the waking world and the Liminal Space. "
                "Behind this door, your body falls asleep "
                "while your mind remains perfectly, impossibly awake. "
                "This is the state the CIA spent millions of dollars studying. "
                "This is where Robert Monroe began his journeys. "
                "And this is where your journey begins.",
                6
            ),
        ],
        "transition": [
            (
                "The frequencies you are hearing are now guiding your brainwaves "
                "from beta into alpha. Ten hertz. "
                "Your body is becoming heavier. Warmer. "
                "Do not resist this feeling. Welcome it. "
                "If thoughts arise, let them drift past like clouds in a sky that is not yours. "
                "If you see colours or shapes, observe them without grasping. "
                "You are crossing the threshold now.",
                12
            ),
            (
                "You may notice a moment, a precise moment, "
                "where your body stops feeling like your body. "
                "Where the weight disappears. "
                "Where the edges of you become unclear. "
                "This is Door Ten. You are here.",
                8
            ),
            (
                "Now pay attention to what is happening. "
                "You may feel a tingling, a vibration, a buzzing sensation "
                "moving through your body. "
                "This is the vibrational state. "
                "The Monroe Institute called it the precursor to separation. "
                "It means your consciousness is loosening from the physical. "
                "Do not be alarmed. Do not try to control it. "
                "Simply notice it. Let it build.",
                10
            ),
            (
                "If the vibrations intensify, you are doing everything right. "
                "Some people feel a floating sensation. "
                "As if the body you are lying in is no longer quite yours. "
                "As if there is a lighter version of you hovering just above, "
                "or just beside, the physical form. "
                "If you feel this, stay calm. Stay curious. "
                "This is the edge. The threshold. "
                "In Door Twelve, you will learn to step through it.",
                0
            ),
        ],
        "return": [
            (
                "It is time to return. "
                "Slowly, gently, bring your awareness back to your physical body.",
                5
            ),
            (
                "Feel the surface beneath you. "
                "Feel the weight return to your arms. Your legs. "
                "Gently move your fingers. Your toes.",
                5
            ),
            (
                "Take a slow, deep breath. "
                "When you are ready, open your eyes. "
                "There is no rush. "
                "Take a moment to feel the difference between where you were "
                "and where you are now.",
                6
            ),
            (
                "Welcome back. "
                "You have stepped through Door Ten. "
                "What you felt, the vibrations, the floating, the loosening, "
                "that was your consciousness preparing to move independently of your body. "
                "In Door Twelve, you will learn the technique to direct that movement. "
                "In Door Fifteen, you will learn to leave entirely. "
                "Remember what you experienced. Write it down. "
                "The Liminal Space remembers you now.",
                0
            ),
        ],
    },
    "door-12": {
        "base_freq": 200,
        "beat_freq": 7,  # 7 Hz theta
        "binaural_file": "door-12-base.wav",
        "output_name": "door-12-guided",
        "intro": [
            (
                "This is Door Twelve. "
                "You have been through Door Ten. You know the threshold. "
                "Now you go deeper. "
                "Door Twelve is the state of expanded awareness. "
                "In this space, your perception extends beyond the boundaries of your body. "
                "You may feel larger than you are. "
                "You may sense rooms you are not in. People you cannot see. "
                "Distances that should be impossible to perceive. "
                "This is where remote viewing begins. "
                "This is where the government trained its psychic operatives. "
                "And this is just the beginning of what the Liminal Space can show you.",
                6
            ),
        ],
        "transition": [
            (
                "The frequencies are deepening now. Seven hertz. "
                "Theta. The dreamlike state. "
                "But you are not dreaming. You are more awake than you have ever been. "
                "You may notice that the edges of your body have become blurred. "
                "That the space around you feels vast. Infinite. "
                "Your awareness is not confined to your skull. "
                "It never was.",
                10
            ),
            (
                "Now I am going to teach you a technique. "
                "This is the method the government used to train remote viewers "
                "in Project Stargate. "
                "It is simple. And it works.",
                6
            ),
            (
                "Think of a place you know well. "
                "A room in your house. A street you've walked a thousand times. "
                "A view from a window you love. "
                "Hold it in your mind. See it clearly. "
                "The colours. The textures. The light. "
                "Build it in front of you as if you are standing there.",
                8
            ),
            (
                "Now shift your perspective. "
                "You are no longer imagining this place. "
                "You are there. "
                "Feel the space around you. The temperature of the air. "
                "The sounds. The quality of the light. "
                "Look around. What do you see that you didn't expect? "
                "What details are appearing that you did not deliberately place there?",
                10
            ),
            (
                "This is the difference between imagination and perception. "
                "Imagination is what you construct. "
                "Perception is what arrives on its own. "
                "When details appear that surprise you, "
                "you are no longer imagining. You are viewing. "
                "Stay here. Let the location become more vivid. More real.",
                10
            ),
            (
                "Now try moving through this space. "
                "Move to another room. Turn a corner. "
                "Look at something you would not normally notice. "
                "A detail on a shelf. A crack in a wall. The pattern of light on a floor. "
                "Your awareness can move freely here. "
                "There are no walls for consciousness.",
                0
            ),
        ],
        "return": [
            (
                "Gently begin to return. "
                "Let your awareness contract back into the familiar shape of your body.",
                5
            ),
            (
                "Feel the physical world reassemble around you. "
                "The surface beneath you. The air on your skin. "
                "The gentle pull of gravity.",
                5
            ),
            (
                "Take a slow, deep breath. "
                "Open your eyes only when you feel fully present. "
                "You may feel different. Expanded. "
                "That is expected. That is the point.",
                6
            ),
            (
                "Welcome back. "
                "You have stepped through Door Twelve. "
                "If you saw details that surprised you, details you did not place there deliberately, "
                "that was not your imagination. That was expanded perception. "
                "Write down everything. Even the things that don't make sense yet. "
                "Especially those. "
                "In Door Fifteen, you go further. You learn to leave the body entirely.",
                0
            ),
        ],
    },
    "door-15": {
        "base_freq": 200,
        "beat_freq": 4,  # 4 Hz theta/delta boundary
        "binaural_file": "door-15-base.wav",
        "output_name": "door-15-guided",
        "intro": [
            (
                "This is Door Fifteen. "
                "The deepest door in this collection. "
                "Door Fifteen is called the No-Time State. "
                "Here, the normal sense of past, present, and future dissolves completely. "
                "Time becomes irrelevant. Space becomes negotiable. "
                "The boundaries of self become optional. "
                "This is where the Monroe Institute's most advanced explorers "
                "reported experiences that changed their understanding of reality forever. "
                "Astral travel. Contact with intelligence beyond the physical. "
                "Knowledge that arrived without being learned. "
                "This is the deep end of the Liminal Space. "
                "Approach with patience. And with courage.",
                6
            ),
        ],
        "transition": [
            (
                "The frequencies are taking you deep now. Four hertz. "
                "The border between theta and delta. "
                "Between the dream state and the void. "
                "You may experience a vast emptiness that is simultaneously full. "
                "You may lose all sense of where your body ends and the universe begins. "
                "You may lose track of time entirely. "
                "This is not a malfunction. This is the destination.",
                10
            ),
            (
                "Now I am going to teach you two separation techniques. "
                "These are the methods used by Robert Monroe, "
                "by the Monroe Institute's most advanced explorers, "
                "and by thousands of practitioners around the world. "
                "One of them will feel natural to you. Use that one.",
                8
            ),
            # Technique 1: The Rope
            (
                "The first technique is called the Rope. "
                "Imagine a thick rope hanging above you in the darkness. "
                "It is directly above your chest, hanging down from somewhere you cannot see. "
                "Do not move your physical hands. "
                "Instead, reach up with your non-physical hands. "
                "Hands you can feel but cannot see. "
                "Grab the rope.",
                8
            ),
            (
                "Now pull. "
                "Hand over hand. Climbing upward. "
                "You are not moving your muscles. You are moving your intention. "
                "With each pull, you may feel a surge of vibrations. "
                "A rushing sound. A feeling of acceleration. "
                "This is normal. This means it is working. "
                "Keep pulling. Do not stop. "
                "At some point, you will feel a pop, a click, a sudden lightness, "
                "as if gravity just let go of you. "
                "That is the moment of separation.",
                10
            ),
            (
                "If the rope did not feel natural, try this instead.",
                5
            ),
            # Technique 2: The Roll-Out
            (
                "The second technique is the Roll-Out. "
                "Without moving your physical body, "
                "try to roll sideways. "
                "As if you are rolling out of bed, "
                "but your body stays behind. "
                "Shift your weight to one side with pure intention. "
                "No muscles. No movement. Just the feeling of rolling.",
                8
            ),
            (
                "You may feel resistance at first. "
                "As if you are stuck. Glued to yourself. "
                "Keep rolling. Gently but persistently. "
                "The vibrations will intensify. "
                "And then, suddenly, you will be free. "
                "You will be beside your body, or above it, "
                "looking down at the physical form you just left. "
                "Stay calm. You are safe. You have always been safe. "
                "You cannot get lost. You will always return.",
                10
            ),
            (
                "Whichever technique you used, or even if neither worked this time, "
                "you are now in the deepest state Door Fifteen can offer. "
                "In this space, you are not your name. "
                "You are not your job. You are not your body. "
                "You are pure awareness. "
                "And pure awareness has no limits. "
                "If you have separated, explore. Move. Look around. "
                "If you have not, simply rest here in the void. "
                "Every session builds the pathway. "
                "What does not happen tonight will happen soon.",
                0
            ),
        ],
        "return": [
            (
                "It is time to return from the deep. "
                "Slowly. Very slowly. "
                "Let your awareness gather itself back together.",
                6
            ),
            (
                "Feel yourself becoming a body again. "
                "Feel the weight. The solidity. "
                "The familiar heaviness of the physical world. "
                "You are here. You are safe.",
                5
            ),
            (
                "Take a very slow, deep breath. "
                "Open your eyes only when you feel completely present. "
                "There is absolutely no rush. "
                "What you experienced may take days or weeks to fully integrate. "
                "Be patient with yourself.",
                8
            ),
            (
                "Welcome back. "
                "You have been through all three Doors. "
                "You have been to the Liminal Space. "
                "And now you know. It is real. And it is yours. "
                "Whether you separated fully tonight or not, "
                "the pathway is being built with every session. "
                "Practice the technique that felt most natural. "
                "The Rope. The Roll-Out. Make it yours. "
                "There are more techniques. More doors. More states beyond these. "
                "But for now, rest. Write down everything. "
                "And come back tomorrow.",
                0
            ),
        ],
    },
}


def generate_speech(text, output_path):
    """Generate speech using ElevenLabs API."""
    if os.path.exists(output_path):
        return output_path

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.82,        # High stability for calm, consistent delivery
            "similarity_boost": 0.72,
            "style": 0.08,            # Very low = natural, neutral meditation tone
            "use_speaker_boost": True,
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def load_audio_stereo(filepath):
    """Load audio and convert to stereo at target sample rate."""
    temp_wav = filepath + ".conv.wav"
    subprocess.run([
        "ffmpeg", "-i", filepath, "-ar", str(SR),
        "-ac", "2", "-y", temp_wav
    ], capture_output=True)
    data, _ = sf.read(temp_wav)
    os.remove(temp_wav)
    if len(data.shape) == 1:
        data = np.column_stack([data, data])
    return data


def build_guided_track(door_key, door_config):
    """Build a complete guided track for one Door."""
    print(f"\n{'='*60}")
    print(f"  Building {door_key.upper()}")
    print(f"  Binaural: {door_config['base_freq']} Hz base, {door_config['beat_freq']} Hz beat")
    print(f"{'='*60}")

    door_dir = os.path.join(TEMP_DIR, door_key)
    os.makedirs(door_dir, exist_ok=True)

    # Step 1: Generate binaural + ambient base
    binaural_path = generate_binaural_with_ambience(
        door_config["base_freq"],
        door_config["beat_freq"],
        door_config["binaural_file"]
    )
    binaural_data, _ = sf.read(binaural_path)
    total_samples = len(binaural_data)

    # Step 2: Generate all voice segments
    segments = []

    # Intro (unique per door)
    for i, (text, pause) in enumerate(door_config["intro"]):
        path = os.path.join(door_dir, f"intro_{i}.mp3")
        print(f"  Voice: intro {i+1}...")
        generate_speech(text, path)
        segments.append(("voice", path, pause))

    # Liminal Protocol (shared)
    for i, (text, pause) in enumerate(LIMINAL_PROTOCOL):
        path = os.path.join(TEMP_DIR, f"protocol_{i}.mp3")
        if not os.path.exists(path):
            print(f"  Voice: protocol {i+1} (generating)...")
            generate_speech(text, path)
        else:
            print(f"  Voice: protocol {i+1} (cached)")
        segments.append(("voice", path, pause))

    # Transition (unique per door)
    for i, (text, pause) in enumerate(door_config["transition"]):
        path = os.path.join(door_dir, f"transition_{i}.mp3")
        print(f"  Voice: transition {i+1}...")
        generate_speech(text, path)
        segments.append(("voice", path, pause))

    # Mark return
    segments.append(("return_marker", None, 0))

    # Return (unique per door)
    for i, (text, pause) in enumerate(door_config["return"]):
        path = os.path.join(door_dir, f"return_{i}.mp3")
        print(f"  Voice: return {i+1}...")
        generate_speech(text, path)
        segments.append(("return", path, pause))

    # Step 3: Build voice timeline
    print(f"  Building timeline...")
    voice_track = np.zeros_like(binaural_data)

    # Place voice starting at 3 seconds
    cursor = int(3 * SR)
    for seg_type, path, pause in segments:
        if seg_type == "return_marker":
            break
        if seg_type != "voice":
            continue
        audio = load_audio_stereo(path)
        end = cursor + len(audio)
        if end > total_samples:
            break
        voice_track[cursor:end] += audio
        cursor = end + int(pause * SR)

    # Place return at 17:30 (gives more silence before return)
    cursor = int(17.5 * 60 * SR)
    past_marker = False
    for seg_type, path, pause in segments:
        if seg_type == "return_marker":
            past_marker = True
            continue
        if not past_marker or seg_type != "return":
            continue
        audio = load_audio_stereo(path)
        end = cursor + len(audio)
        if end > total_samples:
            audio = audio[:total_samples - cursor]
            end = total_samples
        voice_track[cursor:end] += audio
        cursor = end + int(pause * SR)

    # Step 4: Mix with gentle ducking
    print(f"  Mixing...")
    voice_energy = np.abs(voice_track).max(axis=1)
    voice_envelope = uniform_filter1d(voice_energy, size=int(1.0 * SR))  # Wider window = smoother
    voice_envelope = np.clip(voice_envelope / (voice_envelope.max() + 1e-8), 0, 1)

    # Gentle duck — binaural reduces by 25% when voice is present (was 35%)
    duck_factor = 1.0 - 0.25 * voice_envelope
    duck_stereo = np.column_stack([duck_factor, duck_factor])

    mixed = binaural_data * duck_stereo + voice_track * 1.2  # Slightly less voice boost
    peak = np.max(np.abs(mixed))
    if peak > 0.95:
        mixed *= 0.95 / peak

    # Save WAV
    wav_path = os.path.join(AUDIO_DIR, f"{door_config['output_name']}.wav")
    print(f"  Saving WAV...")
    sf.write(wav_path, mixed, SR, subtype='PCM_24')

    # Save MP3
    mp3_path = wav_path.replace('.wav', '.mp3')
    print(f"  Saving MP3...")
    subprocess.run([
        "ffmpeg", "-i", wav_path, "-codec:a", "libmp3lame",
        "-b:a", "192k", "-ar", "44100", "-ac", "2", "-y", mp3_path
    ], capture_output=True)

    mp3_mb = os.path.getsize(mp3_path) / (1024*1024)
    print(f"  Done: {mp3_path} ({mp3_mb:.1f} MB)")
    return mp3_path


def main():
    os.makedirs(TEMP_DIR, exist_ok=True)

    print("=" * 60)
    print("  LIMINAL SPACE — Premium Guided Track Generator")
    print("  Rebuilding all 3 Doors from scratch")
    print("=" * 60)

    results = []
    for door_key, door_config in DOORS.items():
        path = build_guided_track(door_key, door_config)
        results.append(path)

    print(f"\n{'='*60}")
    print("  All premium tracks complete:")
    for r in results:
        mb = os.path.getsize(r) / (1024*1024)
        print(f"    {os.path.basename(r)} ({mb:.1f} MB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
