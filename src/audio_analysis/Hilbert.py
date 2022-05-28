import numpy as np
from scipy.signal import hilbert


def envelope(signal, fs=16000):
    """
    Extract the envelope using the Hilbert's transform and save it into a figure.


    Parameters
    ------------
    signal : array_like
            Amplitud of the original signal.
    fs : int
            Sample frequency of the signal.
            
    Return
    -----------
    amp_norm : array_like
            Normalized [0 1]-envelope amplitude.
    """
    analytic_signal = hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)
    amp_min, amp_max = np.min(amplitude_envelope), np.max(amplitude_envelope)
    amp_norm = list(map(lambda x: (x - amp_min) / (amp_max - amp_min), amplitude_envelope))
    inst_phase = np.unwrap(np.angle(amp_norm))
    inst_freq = np.diff(inst_phase)/(2*np.pi)*fs

    return amp_norm
