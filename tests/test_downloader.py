import pytest
import numpy as np
import soundfile as sf
import yt_dlp
from unittest.mock import patch, MagicMock
from pathlib import Path
from dlt.downloader import download


def _make_mock_ydl(tmp_path, title='Test Song', ext='m4a'):
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl.__exit__ = MagicMock(return_value=False)

    def fake_extract_info(url, download):
        (tmp_path / f'original_raw.{ext}').touch()
        return {'title': title, 'ext': ext}

    mock_ydl.extract_info = fake_extract_info
    return mock_ydl


def _fake_ffmpeg_writes_wav(tmp_path):
    def side_effect(cmd, **kwargs):
        out = Path(cmd[-1])
        sf.write(str(out), np.zeros(100, dtype=np.float32), 44100)
        return MagicMock(returncode=0, stderr='')
    return side_effect


def test_download_returns_title_and_wav_path(tmp_path):
    with patch('yt_dlp.YoutubeDL', return_value=_make_mock_ydl(tmp_path)), \
         patch('dlt.downloader.get_ffmpeg_exe', return_value='/fake/ffmpeg'), \
         patch('dlt.downloader.subprocess.run', side_effect=_fake_ffmpeg_writes_wav(tmp_path)):

        wav_path, title = download('https://youtu.be/test', tmp_path)

    assert title == 'Test Song'
    assert wav_path == tmp_path / 'original.wav'
    assert wav_path.exists()


def test_download_raises_on_yt_dlp_error(tmp_path):
    mock_ydl = MagicMock()
    mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError('video unavailable')

    with patch('yt_dlp.YoutubeDL', return_value=mock_ydl):
        with pytest.raises(RuntimeError, match='video unavailable'):
            download('https://youtu.be/invalid', tmp_path)
