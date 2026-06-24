import sys
import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
from unittest.mock import patch, MagicMock
from dlt.cli import main


def _write_sine_wav(path: Path, sample_rate: int = 44100) -> None:
    t = np.linspace(0, 1.0, sample_rate, endpoint=False)
    audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    sf.write(str(path), audio, sample_rate)


def _fake_ffmpeg_touches_output(cmd, **kwargs):
    Path(cmd[-1]).touch()
    return MagicMock(returncode=0, stderr='')


def test_full_pipeline_creates_mp3_with_auto_name(tmp_path, monkeypatch):
    fake_wav = tmp_path / "original.wav"
    _write_sine_wav(fake_wav)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'argv', ['dlt', 'https://youtu.be/test', '2'])

    with patch('dlt.downloader.download', return_value=(fake_wav, 'Test Song')), \
         patch('dlt.encoder.get_ffmpeg_exe', return_value='/fake/ffmpeg'), \
         patch('dlt.encoder.subprocess.run', side_effect=_fake_ffmpeg_touches_output):
        main()

    output_files = list(tmp_path.glob('*+2st.mp3'))
    assert len(output_files) == 1, f"Expected one +2st.mp3 file, found: {output_files}"
    assert 'test-song' in output_files[0].name


def test_custom_output_filename(tmp_path, monkeypatch):
    fake_wav = tmp_path / "original.wav"
    _write_sine_wav(fake_wav)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'argv', ['dlt', 'https://youtu.be/test', '3', '-o', 'rehearsal.mp3'])

    with patch('dlt.downloader.download', return_value=(fake_wav, 'Test Song')), \
         patch('dlt.encoder.get_ffmpeg_exe', return_value='/fake/ffmpeg'), \
         patch('dlt.encoder.subprocess.run', side_effect=_fake_ffmpeg_touches_output):
        main()

    assert (tmp_path / 'rehearsal.mp3').exists()


def test_download_failure_exits_with_message(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'argv', ['dlt', 'https://youtu.be/invalid', '2'])

    with patch('dlt.downloader.download', side_effect=RuntimeError('video unavailable')):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert 'download failed' in str(exc_info.value)
    assert 'video unavailable' in str(exc_info.value)


def test_encoding_failure_exits_with_message(tmp_path, monkeypatch):
    fake_wav = tmp_path / "original.wav"
    _write_sine_wav(fake_wav)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'argv', ['dlt', 'https://youtu.be/test', '2'])

    with patch('dlt.downloader.download', return_value=(fake_wav, 'Test Song')), \
         patch('dlt.encoder.encode_mp3', side_effect=RuntimeError('codec not found')):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert 'encoding failed' in str(exc_info.value)
    assert 'codec not found' in str(exc_info.value)
