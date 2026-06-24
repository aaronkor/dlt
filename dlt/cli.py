import re
import argparse


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
    pass
