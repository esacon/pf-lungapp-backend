from scipy.signal import butter, lfilter

CUT_FREQ = 2250.0


def filter_audio(amp, fs, cut_freq=CUT_FREQ, ftype='low'):
    """
    Apply a low-pass filter setted in 2250 Hz.

    Parameters
    ------------
    amp : array_like, optional
            Amplitud of the signal.
    fs : int
            Sample frequency of the signal.
    cut_freq : array_like, optional
            The critical frequency or frequencies. For lowpass and highpass 
            filters, Wn is a scalar; for bandpass and bandstop filters, 
            Wn is a length-2 sequence.
    ftype : string, optional, optional
            Filter's type. Default 'lowpass'.

    Return
    -----------
    y : array_like
            Filtered amplitude.
    """
    # Filter applied to .wav audio.
    b, a = butter(9, cut_freq, fs=fs, btype=ftype)

    return lfilter(b, a, amp)