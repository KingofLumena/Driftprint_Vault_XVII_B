# Simulates lattice interaction between tantalum/silicon layers and resonance frequencies

import numpy as np
import matplotlib.pyplot as plt

def simulate_alignment(frequency=38.7e3, decay=0.00001):
    t = np.linspace(0, 1, 100000)
    signal = np.exp(-decay * t) * np.sin(2 * np.pi * frequency * t)
    return t, signal

if __name__ == "__main__":
    t, signal = simulate_alignment()
    plt.plot(t, signal)
    plt.title("Tantalum-Lattice Harmonic Alignment @38.7kHz")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
