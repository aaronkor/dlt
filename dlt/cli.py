import re
import argparse
import shutil
import tempfile
from pathlib import Path

import dlt.downloader
import dlt.encoder
from dlt.pitcher import pitch_shift


def slugify(title: str, semitones: int) -> str:
    slug = title.lower().replace(' ', '-')
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    semitone_str = f'+{semitones}' if semitones > 0 else str(semitones)
    return f"{slug}-{semitone_str}st.mp3"


def semitones_type(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"semitones must be an integer, got {value!r}")
    if not -12 <= n <= 12:
        raise argparse.ArgumentTypeError(f"semitones must be between -12 and +12, got {n}")
    return n


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transpose audio from a music video URL by N semitones."
    )
    parser.add_argument("url", help="Music video URL (any site supported by yt-dlp)")
    parser.add_argument("semitones", type=semitones_type, help="Semitones to transpose (-12 to +12)")
    parser.add_argument("-o", "--output", help="Output MP3 filename (default: auto-generated from video title)")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        try:
            wav_path, title = dlt.downloader.download(args.url, tmp)
        except Exception as e:
            raise SystemExit(f"dlt: download failed: {e}") from e

        output_name = args.output or slugify(title, args.semitones)
        shifted_path = tmp / "shifted.wav"
        mp3_tmp = tmp / Path(output_name).name

        pitch_shift(wav_path, args.semitones, shifted_path)

        try:
            dlt.encoder.encode_mp3(shifted_path, mp3_tmp)
        except Exception as e:
            raise SystemExit(f"dlt: encoding failed: {e}") from e

        shutil.move(mp3_tmp, output_name)
        print(f"Saved: {output_name}")
