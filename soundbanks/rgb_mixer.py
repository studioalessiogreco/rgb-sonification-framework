#!/usr/bin/env python3
"""
RGB Sound Mixer
===============
Mixes R / G / B WAV files from an existing sound bank into a single
composite WAV file for any RGB colour value.

Usage:
    # Single colour
    python rgb_mixer.py --rgb 255 120 40

    # Multiple colours
    python rgb_mixer.py --rgb 255 0 0   --rgb 0 255 0   --rgb 0 0 255

    # Batch from a text file  (one "R G B" per line)
    python rgb_mixer.py --batch colors.txt

    # Full 256³ palette subset demo (first N colours)
    python rgb_mixer.py --demo 16

    # Custom bank / output directories
    python rgb_mixer.py --rgb 200 100 50 --bank ./RGB_SOUND_BANK --out ./mixed

Requirements:
    pip install numpy
"""

import os
import sys
import wave
import json
import csv
import struct
import argparse
import time
from typing import List, Tuple

# ── auto-install numpy if missing ────────────────────────────────────────────
try:
    import numpy as np
except ImportError:
    print("[INFO] Installing numpy …")
    os.system(f"{sys.executable} -m pip install numpy --break-system-packages -q")
    import numpy as np

# ── defaults ──────────────────────────────────────────────────────────────────
DEFAULT_BANK   = os.path.join(os.path.dirname(__file__), "RGB_SOUND_BANK")
DEFAULT_OUT    = os.path.join(os.path.dirname(__file__), "RGB_MIXED")
SAMPLE_RATE    = 48_000
SAMPLE_WIDTH   = 3          # 24-bit
PEAK_TARGET    = 0.92       # headroom after normalisation

# ── low-level 24-bit I/O ──────────────────────────────────────────────────────

def read_wav_24bit(path: str) -> np.ndarray:
    """Read a 24-bit mono WAV → float64 array in [-1, 1]."""
    with wave.open(path, "rb") as wf:
        sw = wf.getsampwidth()
        n  = wf.getnframes()
        raw = wf.readframes(n)

    if sw == 3:
        # Unpack 3-byte LE signed integers manually
        samples = np.zeros(n, dtype=np.float64)
        raw_bytes = bytearray(raw)
        for i in range(n):
            b0, b1, b2 = raw_bytes[i*3], raw_bytes[i*3+1], raw_bytes[i*3+2]
            val = b0 | (b1 << 8) | (b2 << 16)
            if val >= 0x800000:          # two's complement
                val -= 0x1000000
            samples[i] = val / 8_388_607.0
        return samples

    elif sw == 2:
        arr = np.frombuffer(raw, dtype="<i2").astype(np.float64)
        return arr / 32_767.0
    else:
        raise ValueError(f"Unsupported sample width {sw} in {path}")


def write_wav_24bit(path: str, samples: np.ndarray, sample_rate: int = SAMPLE_RATE):
    """Write float64 [-1, 1] array as a 24-bit mono WAV file."""
    int_samples = np.clip(samples * 8_388_607.0,
                          -8_388_608, 8_388_607).astype(np.int32)
    raw = bytearray(len(int_samples) * 3)
    for i, s in enumerate(int_samples):
        # Convert numpy int32 → Python int first, then pack as 4-byte LE
        v = int(s)
        b = v.to_bytes(4, byteorder="little", signed=True)
        raw[i*3:i*3+3] = b[:3]

    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(3)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(raw))


# ── core mixer ────────────────────────────────────────────────────────────────

def mix_rgb(r: int, g: int, b: int,
            bank_dir: str,
            out_dir: str,
            verbose: bool = True) -> dict:
    """
    Load R_rrr.wav, G_ggg.wav, B_bbb.wav from bank_dir,
    mix them into a normalised 24-bit WAV in out_dir.

    Returns a metadata dict.
    """
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    r_path = os.path.join(bank_dir, "R", f"R_{r:03d}.wav")
    g_path = os.path.join(bank_dir, "G", f"G_{g:03d}.wav")
    b_path = os.path.join(bank_dir, "B", f"B_{b:03d}.wav")

    for p in (r_path, g_path, b_path):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Bank file not found: {p}")

    sig_r = read_wav_24bit(r_path)
    sig_g = read_wav_24bit(g_path)
    sig_b = read_wav_24bit(b_path)

    # Equalise length (all should be 48000 samples but be defensive)
    n = max(len(sig_r), len(sig_g), len(sig_b))
    def pad(s, length):
        if len(s) < length:
            return np.pad(s, (0, length - len(s)))
        return s
    sig_r, sig_g, sig_b = pad(sig_r, n), pad(sig_g, n), pad(sig_b, n)

    # --- Perceptual weighting -------------------------------------------------
    # The three channels span very different frequency registers.
    # Equal-power mixing (1/√3 each) avoids the centre-cluster masking that
    # plain 1/3 summation causes, while staying clip-safe before normalisation.
    w = 1.0 / np.sqrt(3.0)
    mixed = (sig_r + sig_g + sig_b) * w

    # --- Safe peak normalisation ---------------------------------------------
    peak = np.max(np.abs(mixed))
    if peak > 1e-9:
        mixed *= PEAK_TARGET / peak
    mixed = np.clip(mixed, -1.0, 1.0)

    # --- Output filename -----------------------------------------------------
    hex_str  = f"{r:02X}{g:02X}{b:02X}"
    filename = f"COLOR_{hex_str}.wav"
    out_path = os.path.join(out_dir, filename)

    os.makedirs(out_dir, exist_ok=True)
    write_wav_24bit(out_path, mixed, SAMPLE_RATE)

    if verbose:
        print(f"  ✔  RGB({r:3d},{g:3d},{b:3d})  →  #{hex_str}  →  {filename}")

    return {
        "hex"      : f"#{hex_str}",
        "r"        : r,
        "g"        : g,
        "b"        : b,
        "filename" : filename,
        "path"     : out_path,
    }


# ── batch engine ─────────────────────────────────────────────────────────────

def batch_mix(colours: List[Tuple[int, int, int]],
              bank_dir: str,
              out_dir: str) -> List[dict]:
    """Mix a list of (r,g,b) tuples; return list of metadata dicts."""
    results = []
    total   = len(colours)
    t_start = time.time()

    print(f"\n[BATCH] Mixing {total} colour(s) …\n")
    for idx, (r, g, b) in enumerate(colours, 1):
        bar_len = 36
        filled  = int(bar_len * idx / total)
        bar     = "█" * filled + "░" * (bar_len - filled)
        eta     = ((time.time() - t_start) / idx) * (total - idx)
        print(f"\r  [{bar}] {idx}/{total}  ETA {eta:4.0f}s", end="", flush=True)
        rec = mix_rgb(r, g, b, bank_dir, out_dir, verbose=False)
        results.append(rec)

    elapsed = time.time() - t_start
    print(f"\r  [{'█'*bar_len}] {total}/{total}  done in {elapsed:.1f}s     ")
    return results


# ── database writers ─────────────────────────────────────────────────────────

def write_json_db(records: List[dict], out_dir: str):
    path = os.path.join(out_dir, "colour_db.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"[DB] colour_db.json  ({len(records)} entries)")


def write_csv_db(records: List[dict], out_dir: str):
    path = os.path.join(out_dir, "colour_db.csv")
    fields = ["hex", "r", "g", "b", "filename"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"[DB] colour_db.csv   ({len(records)} entries)")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="RGB Sound Mixer — combine R/G/B tones into colour audio files"
    )
    p.add_argument("--bank", default=DEFAULT_BANK,
                   help="Path to the RGB_SOUND_BANK folder (default: ./RGB_SOUND_BANK)")
    p.add_argument("--out",  default=DEFAULT_OUT,
                   help="Output folder for mixed WAV files (default: ./RGB_MIXED)")
    p.add_argument("--rgb",  nargs=3, type=int, metavar=("R","G","B"),
                   action="append", dest="colours",
                   help="RGB values 0-255 (can be repeated)")
    p.add_argument("--batch", metavar="FILE",
                   help="Text file with one 'R G B' per line")
    p.add_argument("--demo", type=int, metavar="N",
                   help="Generate N demo colours (evenly spread palette)")
    p.add_argument("--no-db", action="store_true",
                   help="Skip writing colour_db.json / .csv")
    return p.parse_args()


def load_batch_file(path: str) -> List[Tuple[int,int,int]]:
    colours = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.replace(",", " ").split()
            if len(parts) >= 3:
                colours.append((int(parts[0]), int(parts[1]), int(parts[2])))
    return colours


def demo_palette(n: int) -> List[Tuple[int,int,int]]:
    """Return n evenly-spaced colours across the RGB cube."""
    import math
    side = max(2, math.ceil(n ** (1/3)))
    step = 255 // (side - 1)
    pts  = list(range(0, 256, step))[:side]
    cols = [(r, g, b) for r in pts for g in pts for b in pts]
    # Spread them evenly if more were generated than requested
    stride = max(1, len(cols) // n)
    return cols[::stride][:n]


def main():
    args = parse_args()

    # ── collect colours ──────────────────────────────────────────────────────
    colours: List[Tuple[int,int,int]] = []

    if args.colours:
        colours += [tuple(c) for c in args.colours]

    if args.batch:
        colours += load_batch_file(args.batch)

    if args.demo:
        colours += demo_palette(args.demo)

    if not colours:
        # Fallback: interactive prompt
        print("No colours specified. Enter RGB values interactively.")
        print("Type 'done' to finish.\n")
        while True:
            raw = input("  RGB (e.g. 255 120 40): ").strip()
            if raw.lower() in ("done", "q", ""):
                break
            parts = raw.replace(",", " ").split()
            if len(parts) == 3:
                colours.append((int(parts[0]), int(parts[1]), int(parts[2])))
            else:
                print("  ✗  Please enter exactly three integers.")

    if not colours:
        print("No colours to process. Exiting.")
        sys.exit(0)

    # ── deduplicate while preserving order ───────────────────────────────────
    seen = set()
    unique = []
    for c in colours:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    colours = unique

    print("=" * 60)
    print(f"  RGB SOUND MIXER")
    print(f"  Bank : {args.bank}")
    print(f"  Out  : {args.out}")
    print(f"  Jobs : {len(colours)} colour(s)")
    print("=" * 60)

    # ── mix ──────────────────────────────────────────────────────────────────
    if len(colours) == 1:
        r, g, b = colours[0]
        rec = mix_rgb(r, g, b, args.bank, args.out, verbose=True)
        records = [rec]
    else:
        records = batch_mix(colours, args.bank, args.out)

    # ── database ─────────────────────────────────────────────────────────────
    if not args.no_db:
        print()
        write_json_db(records, args.out)
        write_csv_db(records, args.out)

    print("\n" + "=" * 60)
    print(f"  DONE.  {len(records)} file(s) in {os.path.abspath(args.out)}")
    print("=" * 60 + "\n")


# ── importable API ────────────────────────────────────────────────────────────

def mix_colour(r: int, g: int, b: int,
               bank_dir: str = DEFAULT_BANK,
               out_dir:  str = DEFAULT_OUT) -> str:
    """
    Public API: mix a single RGB colour and return the output WAV path.

    Example:
        from rgb_mixer import mix_colour
        path = mix_colour(255, 120, 40)
    """
    rec = mix_rgb(r, g, b, bank_dir, out_dir, verbose=True)
    return rec["path"]


def mix_colours(colours: List[Tuple[int,int,int]],
                bank_dir: str = DEFAULT_BANK,
                out_dir:  str = DEFAULT_OUT) -> List[dict]:
    """
    Public API: batch-mix a list of (r,g,b) tuples.

    Example:
        from rgb_mixer import mix_colours
        results = mix_colours([(255,0,0),(0,255,0),(0,0,255)])
    """
    return batch_mix(colours, bank_dir, out_dir)


if __name__ == "__main__":
    main()


LICENCE
───────
“© 2026 Alessio Greco – Tutti i diritti riservati. Nessuna licenza di riuso concessa.”
"© 2026 Alessio Greco – All rights reserved. No reuse license granted."