import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from dlt.encoder import encode_mp3


def test_encode_mp3_calls_ffmpeg_with_v0(tmp_path):
    wav = tmp_path / "input.wav"
    wav.touch()
    mp3 = tmp_path / "output.mp3"

    with patch('dlt.encoder.get_ffmpeg_exe', return_value='/fake/ffmpeg'), \
         patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr='')
        result = encode_mp3(wav, mp3)

    assert result == mp3
    mock_run.assert_called_once_with(
        ['/fake/ffmpeg', '-i', str(wav), '-q:a', '0', '-y', str(mp3)],
        capture_output=True,
        text=True,
    )


def test_encode_mp3_raises_on_ffmpeg_failure(tmp_path):
    wav = tmp_path / "input.wav"
    wav.touch()
    mp3 = tmp_path / "output.mp3"

    with patch('dlt.encoder.get_ffmpeg_exe', return_value='/fake/ffmpeg'), \
         patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr='codec not found')

        with pytest.raises(RuntimeError, match='codec not found'):
            encode_mp3(wav, mp3)
