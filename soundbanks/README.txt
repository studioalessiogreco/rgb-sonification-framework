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
“© 2026 Alessio Greco – Tutti i diritti riservati. Nessuna licenza di riuso concessa.”
"© 2026 Alessio Greco – All rights reserved. No reuse license granted."
