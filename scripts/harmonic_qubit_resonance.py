#!/usr/bin/env python3
"""
Harmonic Qubit Resonance Simulator for Lumena's Driftprint Quantum Emulation System

This module simulates harmonic qubit resonance patterns used in the Driftprint
quantum emulation architecture. It models the behavior of quantum states under
periodic driving fields.

Part of the Driftprint Vault XVII-B verification bundle.
"""

import json
import math
import os
from datetime import datetime, timezone
from typing import Dict, List, Tuple


def compute_resonance_amplitude(frequency: float, time: float, damping: float = 0.01) -> float:
    """
    Compute the resonance amplitude of a qubit at a given frequency and time.
    
    Args:
        frequency: The driving frequency in Hz
        time: Time point in seconds
        damping: Damping coefficient for decoherence effects
        
    Returns:
        The normalized amplitude value between -1 and 1
    """
    phase = 2 * math.pi * frequency * time
    decay = math.exp(-damping * time)
    amplitude = decay * math.sin(phase)
    return amplitude


def simulate_harmonic_qubit(
    base_frequency: float = 5.0,
    harmonics: int = 5,
    duration: float = 72.1,
    sample_rate: float = 100.0
) -> Dict:
    """
    Simulate harmonic qubit resonance over a specified duration.
    
    Args:
        base_frequency: Base resonance frequency in Hz
        harmonics: Number of harmonic overtones to include
        duration: Total simulation duration in seconds
        sample_rate: Samples per second
        
    Returns:
        Dictionary containing simulation results and metadata
    """
    num_samples = int(duration * sample_rate)
    time_points = [t / sample_rate for t in range(num_samples)]
    
    # Combined resonance from all harmonics
    resonance_data = []
    
    for t in time_points:
        total_amplitude = 0.0
        for h in range(1, harmonics + 1):
            freq = base_frequency * h
            weight = 1.0 / h  # Higher harmonics have less contribution
            total_amplitude += weight * compute_resonance_amplitude(freq, t)
        
        # Normalize
        total_amplitude /= sum(1.0 / h for h in range(1, harmonics + 1))
        resonance_data.append({
            "time": round(t, 4),
            "amplitude": round(total_amplitude, 6)
        })
    
    return {
        "simulation_type": "harmonic_qubit_resonance",
        "parameters": {
            "base_frequency_hz": base_frequency,
            "harmonics": harmonics,
            "duration_seconds": duration,
            "sample_rate_hz": sample_rate
        },
        "data_points": len(resonance_data),
        "resonance_data": resonance_data
    }


def compute_coherence_metrics(resonance_data: List[Dict]) -> Dict:
    """
    Compute memory coherence metrics from resonance data.
    
    Args:
        resonance_data: List of time/amplitude data points
        
    Returns:
        Dictionary containing coherence metrics
    """
    amplitudes = [d["amplitude"] for d in resonance_data]
    times = [d["time"] for d in resonance_data]
    
    if not amplitudes:
        return {
            "total_duration_s": 0,
            "initial_peak_amplitude": 0,
            "final_avg_amplitude": 0,
            "coherence_retention": 0,
            "sample_count": 0
        }
    
    # Compute coherence decay envelope
    # Use min of 100 or available samples to avoid IndexError
    initial_count = min(100, len(amplitudes))
    final_count = min(100, len(amplitudes))
    
    peak_amplitude = max(abs(a) for a in amplitudes[:initial_count])  # Initial peak
    final_amplitude = sum(abs(a) for a in amplitudes[-final_count:]) / final_count  # Final average
    
    # Coherence time estimation (T2*)
    coherence_ratio = final_amplitude / peak_amplitude if peak_amplitude > 0 else 0
    
    return {
        "total_duration_s": times[-1] if times else 0,
        "initial_peak_amplitude": round(peak_amplitude, 6),
        "final_avg_amplitude": round(final_amplitude, 6),
        "coherence_retention": round(coherence_ratio, 4),
        "sample_count": len(resonance_data)
    }


def generate_fft_spectrum(
    resonance_data: List[Dict],
    sample_rate: float = 100.0,
    max_bins: int = 50
) -> Dict:
    """
    Generate FFT spectrum data from resonance simulation.
    
    Uses a simple DFT implementation for spectral analysis.
    
    Note: The number of frequency bins is limited to max_bins for computational
    efficiency. For higher frequency resolution, increase max_bins at the cost
    of longer computation time (O(n * max_bins) complexity).
    
    Args:
        resonance_data: Time-domain resonance data
        sample_rate: Sample rate in Hz
        max_bins: Maximum number of frequency bins to compute (default: 50)
        
    Returns:
        Dictionary containing frequency spectrum data
    """
    amplitudes = [d["amplitude"] for d in resonance_data]
    n = len(amplitudes)
    
    # Compute limited FFT bins (limited for computational efficiency)
    num_bins = min(max_bins, n // 2)
    spectrum = []
    
    for k in range(num_bins):
        real = 0.0
        imag = 0.0
        for i, amp in enumerate(amplitudes):
            angle = -2 * math.pi * k * i / n
            real += amp * math.cos(angle)
            imag += amp * math.sin(angle)
        
        magnitude = math.sqrt(real**2 + imag**2) / n
        frequency = k * sample_rate / n
        
        spectrum.append({
            "frequency_hz": round(frequency, 4),
            "magnitude": round(magnitude, 6)
        })
    
    return {
        "spectrum_type": "fft",
        "frequency_resolution_hz": round(sample_rate / n, 6),
        "bins": num_bins,
        "spectrum_data": spectrum
    }


def run_simulation() -> Tuple[Dict, Dict, Dict]:
    """
    Run the complete harmonic qubit resonance simulation.
    
    Returns:
        Tuple of (simulation_result, coherence_metrics, fft_spectrum)
    """
    # Run simulation with 72.1s duration (as specified)
    print("Starting harmonic qubit resonance simulation...")
    print(f"Duration: 72.1 seconds")
    
    simulation = simulate_harmonic_qubit(
        base_frequency=5.0,
        harmonics=5,
        duration=72.1,
        sample_rate=100.0
    )
    
    print(f"Generated {simulation['data_points']} data points")
    
    # Compute coherence metrics
    coherence = compute_coherence_metrics(simulation["resonance_data"])
    print(f"Coherence retention: {coherence['coherence_retention'] * 100:.2f}%")
    
    # Generate FFT spectrum
    fft_data = generate_fft_spectrum(simulation["resonance_data"])
    print(f"FFT spectrum computed with {fft_data['bins']} frequency bins")
    
    return simulation, coherence, fft_data


def save_results(output_dir: str = None):
    """
    Run simulation and save results to JSON files.
    
    Args:
        output_dir: Directory to save output files (defaults to ../logs)
    """
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "logs")
    
    os.makedirs(output_dir, exist_ok=True)
    
    simulation, coherence, fft_data = run_simulation()
    
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Save coherence log
    coherence_log = {
        "vault_id": "XVII-B",
        "system": "Driftprint Quantum Emulation",
        "timestamp": timestamp,
        "simulation_parameters": simulation["parameters"],
        "coherence_metrics": coherence,
        "verification_status": "pending_grok_validation"
    }
    
    coherence_path = os.path.join(output_dir, "memory_coherence_72.1s.json")
    with open(coherence_path, "w") as f:
        json.dump(coherence_log, f, indent=2)
    print(f"Saved coherence log to: {coherence_path}")
    
    # Save FFT data
    fft_log = {
        "vault_id": "XVII-B",
        "system": "Driftprint Quantum Emulation",
        "timestamp": timestamp,
        "analysis_type": "spectral_fft",
        "source_duration_s": 72.1,
        "fft_results": fft_data
    }
    
    fft_path = os.path.join(output_dir, "fft_spectral_analysis.json")
    with open(fft_path, "w") as f:
        json.dump(fft_log, f, indent=2)
    print(f"Saved FFT analysis to: {fft_path}")
    
    return coherence_log, fft_log


if __name__ == "__main__":
    save_results()
