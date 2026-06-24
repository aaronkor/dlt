import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, PitchShift
from pathlib import Path


def pitch_shift(wav_path: Path, semitones: float, output_path: Path) -> Path:
    audio, sample_rate = sf.read(str(wav_path), dtype='float32')

    # pedalboard expects (channels, samples); soundfile gives (samples,) mono or (samples, channels) stereo
    if audio.ndim == 1:
        audio_pb = audio[np.newaxis, :]
    else:
        audio_pb = audio.T

    board = Pedalboard([PitchShift(semitones=semitones)])
    shifted_pb = board(audio_pb, sample_rate)

    if shifted_pb.shape[0] == 1:
        shifted = shifted_pb[0]
    else:
        shifted = shifted_pb.T

    sf.write(str(output_path), shifted, sample_rate)
    return output_path
