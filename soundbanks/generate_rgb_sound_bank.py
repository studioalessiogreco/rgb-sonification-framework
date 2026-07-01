#!/usr/bin/env python3
"""
RGB Sound Bank Generator
========================
Generates 768 WAV files (256 R + 256 G + 256 B) mapped logarithmically
to frequency ranges for accessibility experiments.

Usage:
    python generate_rgb_sound_bank.py

Requirements:
    pip install numpy scipy
"""

import os
import sys
import json
import struct
import wave
import zipfile
import math
import time

# ── Try to import numpy/scipy; install if missing ────────────────────────────
try:
    import numpy as np
except ImportError:
    print("[INFO] numpy not found – installing …")
    os.system(f"{sys.executable} -m pip install numpy scipy")
    import numpy as np

try:
    from scipy.io import wavfile as sp_wav
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────
SAMPLE_RATE    = 48_000
BIT_DEPTH      = 24          # 24-bit signed PCM
DURATION       = 1.0         # seconds
FADE_MS        = 10          # fade in/out in milliseconds
OUTPUT_DIR     = "RGB_SOUND_BANK"
ZIP_NAME       = "RGB_SOUND_BANK.zip"

# Frequency ranges per channel
CHANNEL_RANGES = {
    "R": (4_000.0, 15_000.0),
    "G": (  250.0,  4_000.0),
    "B": (   20.0,    250.0),
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def log_map(value: int, f_min: float, f_max: float) -> float:
    """Map an integer 0-255 to a frequency using logarithmic interpolation."""
    t = value / 255.0
    return f_min * math.exp(t * math.log(f_max / f_min))


def generate_sine(freq: float, sample_rate: int, duration: float,
                  fade_ms: int) -> np.ndarray:
    """
    Generate a normalised mono sine wave with cosine fade-in/out.

    Returns float64 array in range [-1.0, 1.0].
    """
    n_samples   = int(sample_rate * duration)
    n_fade      = int(sample_rate * fade_ms / 1_000)
    t           = np.linspace(0.0, duration, n_samples, endpoint=False)

    # Base sine
    signal = np.sin(2.0 * np.pi * freq * t)

    # --- subtle harmonics for very low frequencies to aid audibility ---
    # B channel (20–250 Hz): below ~80 Hz, headphones/speakers roll off badly;
    # adding 2nd + 3rd harmonic at reduced amplitude improves perceived pitch.
    if freq < 80.0:
        signal += 0.35 * np.sin(2.0 * np.pi * (freq * 2.0) * t)
        signal += 0.15 * np.sin(2.0 * np.pi * (freq * 3.0) * t)
    elif freq < 150.0:
        signal += 0.20 * np.sin(2.0 * np.pi * (freq * 2.0) * t)

    # Cosine fade envelope
    fade_in  = 0.5 * (1.0 - np.cos(np.pi * np.arange(n_fade) / n_fade))
    fade_out = 0.5 * (1.0 - np.cos(np.pi * np.arange(n_fade, 0, -1) / n_fade))
    signal[:n_fade]  *= fade_in
    signal[-n_fade:] *= fade_out

    # Normalise to peak 0.95 (safe headroom, no clipping)
    peak = np.max(np.abs(signal))
    if peak > 0.0:
        signal *= 0.95 / peak

    return signal.astype(np.float64)


def float_to_24bit_pcm(samples: np.ndarray) -> bytes:
    """
    Convert float64 [-1,1] to 24-bit signed PCM little-endian bytes.
    Python's `wave` module only natively supports 16-bit, so we pack manually.
    """
    # Scale to int32 range of 24-bit signed: -8388608 … 8388607
    int_samples = np.clip(samples * 8_388_607.0, -8_388_608, 8_388_607).astype(np.int32)
    # Pack each sample as 3 bytes, little-endian (drop the high byte of int32)
    raw = bytearray()
    for s in int_samples:
        # Two's complement 24-bit little-endian
        b = s.tobytes()[:3]   # int32 LE → take the 3 LSBs
        raw.extend(b)
    return bytes(raw)


def write_wav_24bit(filepath: str, samples: np.ndarray, sample_rate: int):
    """Write a 24-bit mono WAV file without relying on scipy."""
    pcm_data = float_to_24bit_pcm(samples)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(3)          # 3 bytes = 24 bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)


# ── Main generation routine ───────────────────────────────────────────────────

def create_folder_structure():
    for ch in ("R", "G", "B"):
        os.makedirs(os.path.join(OUTPUT_DIR, ch), exist_ok=True)


def generate_all_files() -> list:
    """
    Generate all 768 WAV files and return a list of mapping records.
    """
    mapping = []
    total   = 256 * 3
    done    = 0
    t_start = time.time()

    for channel, (f_min, f_max) in CHANNEL_RANGES.items():
        ch_dir = os.path.join(OUTPUT_DIR, channel)

        for value in range(256):
            freq     = log_map(value, f_min, f_max)
            filename = f"{channel}_{value:03d}.wav"
            filepath = os.path.join(ch_dir, filename)

            samples  = generate_sine(freq, SAMPLE_RATE, DURATION, FADE_MS)
            write_wav_24bit(filepath, samples, SAMPLE_RATE)

            mapping.append({
                "filename"  : filename,
                "channel"   : channel,
                "rgb_value" : value,
                "frequency_hz": round(freq, 4),
                "sample_rate" : SAMPLE_RATE,
                "bit_depth"   : BIT_DEPTH,
                "duration_s"  : DURATION,
            })

            done += 1
            pct   = done / total * 100
            elapsed = time.time() - t_start
            eta     = (elapsed / done) * (total - done) if done else 0
            bar_len = 40
            filled  = int(bar_len * done / total)
            bar     = "█" * filled + "░" * (bar_len - filled)
            print(
                f"\r[{bar}] {pct:5.1f}%  {channel}_{value:03d}  "
                f"{freq:8.2f} Hz  ETA {eta:4.0f}s   ",
                end="", flush=True
            )

    print(f"\n[OK] All {total} files generated in {time.time()-t_start:.1f}s")
    return mapping


# ── mapping.json ──────────────────────────────────────────────────────────────

def write_mapping_json(mapping: list):
    path = os.path.join(OUTPUT_DIR, "mapping.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"[OK] mapping.json  ({len(mapping)} entries)")


# ── README.txt ────────────────────────────────────────────────────────────────

README_TEMPLATE = """\
╔══════════════════════════════════════════════════════════════════════════════╗
║                  RGB SOUND BANK — Accessibility Experiment                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

OVERVIEW
────────
This sound bank maps every possible value (0–255) for each RGB colour channel
to a unique audio tone, enabling colour information to be conveyed through
sound. It is designed for accessibility research and multimodal perception
experiments.

FOLDER STRUCTURE
────────────────
RGB_SOUND_BANK/
├── R/           256 WAV files  (R_000.wav … R_255.wav)
├── G/           256 WAV files  (G_000.wav … G_255.wav)
├── B/           256 WAV files  (B_000.wav … B_255.wav)
├── mapping.json full metadata for all 768 files
└── README.txt   this file

FREQUENCY MAPPING
─────────────────
Logarithmic mapping is used so that perceptual steps in pitch feel uniform
across the range, mirroring how human hearing perceives frequency on a
logarithmic (octave-based) scale.

  Formula:  f(v) = f_min × exp( v/255 × ln(f_max / f_min) )

  Channel │ RGB range │ Frequency range  │ Perceptual register
  ────────┼───────────┼──────────────────┼──────────────────────
    R     │  0 – 255  │  4 000 – 15 000 Hz │ Bright / treble
    G     │  0 – 255  │    250 –  4 000 Hz │ Mid-range
    B     │  0 – 255  │     20 –    250 Hz │ Deep / bass

  Value 0   → minimum frequency (f_min)
  Value 255 → maximum frequency (f_max)

  The three ranges are contiguous and non-overlapping, so R, G, B tones
  can be played simultaneously without masking each other.

NOTE ON HARMONICS
─────────────────
For B-channel tones below ~150 Hz, soft 2nd and 3rd harmonics are added at
reduced amplitude. This compensates for the reduced sensitivity of consumer
headphones and speakers at sub-bass frequencies, and improves perceived pitch.

AUDIO SPECIFICATIONS
────────────────────
  Format       : WAV (PCM)
  Sample rate  : 48 000 Hz
  Bit depth    : 24-bit signed
  Channels     : Mono
  Duration     : 1.00 second per file
  Fade         : 10 ms cosine fade-in and fade-out
  Peak level   : −0.45 dBFS  (safe headroom, no clipping)

USAGE EXAMPLE (Python)
─────────────────────
  import simpleaudio as sa  # or any WAV player

  def play_rgb(r, g, b, bank_dir="RGB_SOUND_BANK"):
      for ch, val in [("R", r), ("G", g), ("B", b)]:
          path = f"{bank_dir}/{ch}/{ch}_{val:03d}.wav"
          wave_obj = sa.WaveObject.from_wave_file(path)
          play_obj = wave_obj.play()
          # play simultaneously or sequentially as needed

INSTALLATION
────────────
1.  Install Python 3.8+ from https://www.python.org
2.  Install dependencies:
        pip install numpy scipy
3.  (Optional) For playback examples:
        pip install simpleaudio

EXECUTION
─────────
Run the generator script once to (re)build the entire bank:

    python generate_rgb_sound_bank.py

The script will:
  • Create the folder structure automatically
  • Generate all 768 WAV files with a live progress bar
  • Write mapping.json
  • Write this README.txt
  • Package everything into RGB_SOUND_BANK.zip

MAPPING.JSON SCHEMA
───────────────────
Each entry in the JSON array has:
  {
    "filename"    : "R_042.wav",
    "channel"     : "R",
    "rgb_value"   : 42,
    "frequency_hz": 5432.1234,
    "sample_rate" : 48000,
    "bit_depth"   : 24,
    "duration_s"  : 1.0
  }

LICENCE
───────
Generated content is released into the public domain (CC0).
The generator script itself is MIT-licensed.
"""

def write_readme():
    path = os.path.join(OUTPUT_DIR, "README.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(README_TEMPLATE)
    print("[OK] README.txt")


# ── ZIP export ────────────────────────────────────────────────────────────────

def create_zip():
    with zipfile.ZipFile(ZIP_NAME, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zf:
        file_count = 0
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for fname in sorted(files):
                abs_path  = os.path.join(root, fname)
                arc_name  = os.path.relpath(abs_path, start=os.path.dirname(OUTPUT_DIR))
                zf.write(abs_path, arc_name)
                file_count += 1
    size_mb = os.path.getsize(ZIP_NAME) / 1_048_576
    print(f"[OK] {ZIP_NAME}  ({file_count} files, {size_mb:.1f} MB)")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  RGB SOUND BANK GENERATOR")
    print(f"  768 files · 48 kHz · 24-bit · Mono · 1 s each")
    print("=" * 60)

    print("\n[1/5] Creating folder structure …")
    create_folder_structure()

    print("[2/5] Generating WAV files …\n")
    mapping = generate_all_files()

    print("\n[3/5] Writing mapping.json …")
    write_mapping_json(mapping)

    print("[4/5] Writing README.txt …")
    write_readme()

    print("[5/5] Creating ZIP archive …")
    create_zip()

    print("\n" + "=" * 60)
    print(f"  DONE.  Output folder : {os.path.abspath(OUTPUT_DIR)}")
    print(f"         ZIP archive   : {os.path.abspath(ZIP_NAME)}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

LICENCE
───────
“© 2026 Alessio Greco – Tutti i diritti riservati. Nessuna licenza di riuso concessa.”
"© 2026 Alessio Greco – All rights reserved. No reuse license granted."