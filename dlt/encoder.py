import subprocess
from pathlib import Path
from imageio_ffmpeg import get_ffmpeg_exe


def encode_mp3(wav_path: Path, mp3_path: Path) -> Path:
    ffmpeg = get_ffmpeg_exe()
    result = subprocess.run(
        [ffmpeg, '-i', str(wav_path), '-q:a', '0', '-y', str(mp3_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return mp3_path
