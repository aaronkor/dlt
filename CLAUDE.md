# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is dlt

`dlt` is a Python CLI tool for cover band musicians. It downloads audio from any music video URL, transposes it by a given number of semitones (preserving tempo), and outputs an MP3 file. Fully self-contained — all dependencies install via pip/pipx, no system binaries required.

```bash
dlt <url> <semitones> [-o output.mp3]

dlt "https://youtu.be/abc123" -3
dlt "https://youtu.be/abc123" +5 -o rehearsal-eb.mp3
```

## Install

```bash
pipx install dlt
# or
pip install dlt
```

## Development

```bash
pip install -e ".[dev]"   # install in editable mode with dev deps
pytest                    # run all tests
pytest tests/test_pitcher.py  # run a single test file
```

## Architecture

Three-stage pipeline: `URL → Downloader → Pitcher → Encoder → output.mp3`

| Module | Responsibility |
|---|---|
| `dlt/cli.py` | Entry point — arg parsing, pipeline orchestration, temp dir lifecycle |
| `dlt/downloader.py` | `yt-dlp` Python API → WAV in temp dir |
| `dlt/pitcher.py` | `pedalboard.PitchShift` — loads WAV via `soundfile`, writes shifted WAV |
| `dlt/encoder.py` | `imageio-ffmpeg` bundled binary → V0 VBR MP3 |

## Key Dependencies

| Package | Role |
|---|---|
| `yt-dlp` | Audio download from 1000+ sites |
| `pedalboard` | High-quality pitch shifting (Spotify/JUCE, bundled native) |
| `soundfile` | WAV read/write |
| `imageio-ffmpeg` | Bundled ffmpeg — no system install needed |

## Conventions

- Semitones validated to [-12, +12] before any network calls
- Default output filename: `{slugified-title}-{+/-N}st.mp3` (lowercase, spaces→hyphens, strip non-alphanumeric)
- Temp directory always cleaned up in a `finally` block
- Errors prefixed with `dlt: <stage> failed:` and exit 1
