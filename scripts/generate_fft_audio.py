#!/usr/bin/env python3
"""
FFT Audio Sample Generator for Lumena's Driftprint Quantum Emulation System

This module generates audio samples from harmonic qubit resonance data
for spectral analysis. Produces WAV format audio files suitable for
FFT analysis.

Part of the Driftprint Vault XVII-B verification bundle.
"""

import json
import math
import os
import struct
import wave
from typing import List


def generate_resonance_audio(
    base_frequency: float = 440.0,
    harmonics: int = 5,
    duration: float = 72.1,
    sample_rate: int = 44100,
    amplitude: float = 0.5
) -> List[float]:
    """
    Generate audio samples from harmonic qubit resonance simulation.
    
    Args:
        base_frequency: Base frequency in Hz (default A4 = 440Hz)
        harmonics: Number of harmonics to include
        duration: Duration in seconds
        sample_rate: Audio sample rate in Hz
        amplitude: Maximum amplitude (0.0 to 1.0)
        
    Returns:
        List of normalized audio samples
    """
    num_samples = int(duration * sample_rate)
    samples = []
    
    damping = 0.02  # Coherence decay factor
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.0
        
        # Sum harmonics with decay
        decay = math.exp(-damping * t)
        
        for h in range(1, harmonics + 1):
            freq = base_frequency * h
            weight = 1.0 / h
            phase = 2 * math.pi * freq * t
            sample += weight * math.sin(phase)
        
        # Normalize and apply decay
        sample *= decay * amplitude / sum(1.0 / h for h in range(1, harmonics + 1))
        samples.append(sample)
    
    return samples


def save_wav_file(
    samples: List[float],
    filename: str,
    sample_rate: int = 44100,
    bits_per_sample: int = 16
):
    """
    Save audio samples to a WAV file.
    
    Args:
        samples: List of normalized samples (-1.0 to 1.0)
        filename: Output WAV filename
        sample_rate: Sample rate in Hz
        bits_per_sample: Bit depth (16 or 8)
    """
    # Convert to integer samples
    if bits_per_sample == 16:
        max_val = 32767
        pack_format = '<h'
    else:
        max_val = 127
        pack_format = 'b'
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(bits_per_sample // 8)
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            # Clamp and convert to integer
            clamped = max(-1.0, min(1.0, sample))
            int_sample = int(clamped * max_val)
            wav_file.writeframes(struct.pack(pack_format, int_sample))


def generate_fft_audio_sample(output_dir: str = None):
    """
    Generate FFT audio sample file for spectral analysis.
    
    Args:
        output_dir: Directory to save the audio file (defaults to ../audio)
    """
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "audio")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating FFT audio sample for Driftprint spectral analysis...")
    print("Parameters:")
    print("  Base frequency: 440 Hz (A4)")
    print("  Harmonics: 5")
    print("  Duration: 72.1 seconds")
    print("  Sample rate: 44100 Hz")
    
    samples = generate_resonance_audio(
        base_frequency=440.0,
        harmonics=5,
        duration=72.1,
        sample_rate=44100,
        amplitude=0.7
    )
    
    print(f"  Generated {len(samples)} samples")
    
    output_path = os.path.join(output_dir, "driftprint_fft_sample_72.1s.wav")
    save_wav_file(samples, output_path, sample_rate=44100)
    
    file_size = os.path.getsize(output_path)
    print(f"Saved audio file: {output_path}")
    print(f"File size: {file_size / 1024 / 1024:.2f} MB")
    
    # Generate metadata JSON
    metadata = {
        "vault_id": "XVII-B",
        "system": "Driftprint Quantum Emulation",
        "file": "driftprint_fft_sample_72.1s.wav",
        "format": "WAV",
        "channels": 1,
        "sample_rate_hz": 44100,
        "bit_depth": 16,
        "duration_seconds": 72.1,
        "description": "Audio representation of harmonic qubit resonance for FFT spectral analysis",
        "base_frequency_hz": 440.0,
        "harmonics": 5,
        "coherence_decay_factor": 0.02
    }
    
    metadata_path = os.path.join(output_dir, "fft_sample_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata: {metadata_path}")
    
    return output_path, metadata


if __name__ == "__main__":
    generate_fft_audio_sample()
