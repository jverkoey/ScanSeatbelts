import numpy as np
import matplotlib.pyplot as plt

# Define the data sequence and repeat it to get more samples
data_sequence = np.tile([0, 2, 0, 2, 0, 2], 10)  # Repeat the pattern to create a longer signal
sampling_rate = 1  # Sample rate in Hz (1 sample per second)

# Remove DC component (subtract the mean)
data_sequence_no_dc = data_sequence - np.mean(data_sequence)

# Perform Fourier Transform
fourier_transform = np.fft.fft(data_sequence_no_dc)
n = len(data_sequence)
frequencies = np.fft.fftfreq(n, d=1/sampling_rate)

# Only consider positive frequencies
positive_frequencies = frequencies[:n // 2]
magnitude_spectrum = np.abs(fourier_transform)[:n // 2]

# Plot both the original signal and the Fourier Transform
plt.figure(figsize=(12, 6))

# Plot the original data sequence
plt.subplot(2, 1, 1)
plt.plot(data_sequence_no_dc, marker='o')
plt.title("Original Signal (DC Component Removed)")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")

# Plot the Fourier Transform
plt.subplot(2, 1, 2)
plt.stem(positive_frequencies, magnitude_spectrum)
plt.title("Fourier Transform Magnitude Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid()

plt.tight_layout()
plt.show()
