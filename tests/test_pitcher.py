import numpy as np
import soundfile as sf
from pathlib import Path
from dlt.pitcher import pitch_shift


def _write_sine_wav(path: Path, freq: float, sample_rate: int = 44100, duration: float = 1.0) -> None:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = np.sin(2 * np.pi * freq * t).astype(np.float32)
    sf.write(str(path), audio, sample_rate)


def _dominant_freq(path: Path) -> float:
    audio, sr = sf.read(str(path))
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1 / sr)
    return float(freqs[np.argmax(np.abs(fft))])


def test_pitch_shift_raises_frequency(tmp_path):
    inp = tmp_path / "input.wav"
    out = tmp_path / "output.wav"
    _write_sine_wav(inp, freq=440.0)

    result = pitch_shift(inp, 2, out)

    # 440 Hz * 2^(2/12) ≈ 493.9 Hz
    assert result == out
    assert out.exists()
    dominant = _dominant_freq(out)
    assert 480 < dominant < 510, f"Expected ~494 Hz after +2 semitones, got {dominant:.1f} Hz"


def test_pitch_shift_lowers_frequency(tmp_path):
    inp = tmp_path / "input.wav"
    out = tmp_path / "output.wav"
    _write_sine_wav(inp, freq=440.0)

    pitch_shift(inp, -2, out)

    # 440 Hz * 2^(-2/12) ≈ 392.0 Hz
    dominant = _dominant_freq(out)
    assert 380 < dominant < 405, f"Expected ~392 Hz after -2 semitones, got {dominant:.1f} Hz"


def test_pitch_shift_handles_stereo(tmp_path):
    sample_rate = 44100
    t = np.linspace(0, 1.0, sample_rate, endpoint=False)
    stereo = np.column_stack([
        np.sin(2 * np.pi * 440 * t).astype(np.float32),
        np.sin(2 * np.pi * 440 * t).astype(np.float32),
    ])
    inp = tmp_path / "stereo.wav"
    out = tmp_path / "stereo_out.wav"
    sf.write(str(inp), stereo, sample_rate)

    result = pitch_shift(inp, 2, out)

    assert result == out
    audio, _ = sf.read(str(out))
    assert audio.ndim == 2
    assert audio.shape[1] == 2
