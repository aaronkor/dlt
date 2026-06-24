import subprocess
from pathlib import Path
import yt_dlp
from imageio_ffmpeg import get_ffmpeg_exe


def download(url: str, output_dir: Path) -> tuple[Path, str]:
    """Download best audio from url into output_dir as a WAV file.

    Returns (wav_path, video_title).
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_dir / 'original_raw.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(str(e)) from e

    title = info.get('title', 'unknown')

    raw_files = list(output_dir.glob('original_raw.*'))
    if not raw_files:
        raise RuntimeError("yt-dlp download produced no output file")
    raw_path = raw_files[0]

    wav_path = output_dir / 'original.wav'
    ffmpeg = get_ffmpeg_exe()
    result = subprocess.run(
        [ffmpeg, '-i', str(raw_path), '-ar', '44100', '-ac', '2', '-y', str(wav_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"audio extraction failed: {result.stderr}")

    raw_path.unlink(missing_ok=True)
    return wav_path, title
