# dlt — Design Spec

## Overview

`dlt` is a Python CLI tool for cover band musicians. Given any music video URL and a semitone count, it downloads the audio, transposes it by the specified number of semitones (preserving tempo), and writes an MP3 file to the current directory.

The tool is **fully self-contained via pip/pipx** — no system dependencies required beyond Python.

---

## CLI Interface

```
dlt <url> <semitones> [-o output.mp3]
```

| Argument | Description |
|---|---|
| `url` | Any URL supported by yt-dlp (YouTube, Vimeo, SoundCloud, etc.) |
| `semitones` | Integer between -12 and +12 (negative = lower, positive = higher) |
| `-o / --output` | Optional output filename. Default: `{video-title-slug}-{semitones}st.mp3` |

### Examples

```bash
dlt "https://youtu.be/abc123" -3
dlt "https://youtu.be/abc123" +5 -o rehearsal-eb-tuning.mp3
```

---

## Architecture

Three-stage pipeline:

```
URL → [Downloader] → [Pitcher] → [Encoder] → output.mp3
```

### Module Structure

```
dlt/
  __init__.py
  cli.py         # entry point, arg parsing, pipeline orchestration
  downloader.py  # yt-dlp wrapper → temp WAV
  pitcher.py     # pedalboard pitch shift → shifted WAV
  encoder.py     # imageio-ffmpeg wrapper → MP3
tests/
  test_pitcher.py
  test_cli.py
  test_integration.py
pyproject.toml
```

### Module Responsibilities

**`cli.py`**
- Parses arguments with `argparse`
- Validates semitones is an integer in [-12, +12]
- Creates a temp directory for intermediate files
- Calls Downloader → Pitcher → Encoder in sequence
- Generates default output filename: lowercase video title, spaces→hyphens, strip non-alphanumeric (except hyphens), append `{+N}st` or `{-N}st` suffix
- Moves final MP3 to cwd
- Cleans up temp directory in a `finally` block

**`downloader.py`**
- Uses the `yt-dlp` Python API (not subprocess) to download the best available audio stream
- Extracts to WAV format into the temp directory
- Returns: `(wav_path: Path, video_title: str)`

**`pitcher.py`**
- Loads WAV with `soundfile` into a numpy array + sample rate
- Applies `pedalboard.PitchShift(semitones=N)` to the audio array
- Writes the shifted audio back to a new temp WAV
- Returns: `shifted_wav_path: Path`

**`encoder.py`**
- Resolves the bundled ffmpeg binary path via `imageio.plugins.ffmpeg.get_exe()`
- Calls ffmpeg subprocess: `ffmpeg -i shifted.wav -q:a 0 output.mp3`
- `-q:a 0` = V0 VBR, highest quality MP3 encoding
- Returns: `mp3_path: Path`

---

## Dependencies

All installable via pip — no system binaries required.

| Package | Purpose |
|---|---|
| `yt-dlp` | Video/audio download from 1000+ sites |
| `pedalboard` | Pitch shifting with bundled native code (Spotify/JUCE) |
| `soundfile` | WAV read/write |
| `imageio-ffmpeg` | Bundled ffmpeg binary for MP3 encoding |
| `numpy` | Audio array manipulation (transitive dep) |

---

## Data Flow

1. `cli.py` validates args, creates `tempdir`
2. `downloader.py` → `yt-dlp` downloads best audio → `tempdir/original.wav`; returns video title
3. `cli.py` generates default output filename from video title if `-o` not given
4. `pitcher.py` → loads WAV, applies pitch shift → `tempdir/shifted.wav`
5. `encoder.py` → encodes `shifted.wav` → `tempdir/output.mp3`
6. `cli.py` moves `tempdir/output.mp3` to `cwd/output.mp3`
7. `finally`: temp directory deleted regardless of success or failure

---

## Error Handling

| Scenario | Behavior |
|---|---|
| Semitones out of [-12, +12] range | `argparse` error before any network calls |
| Non-integer semitones | `argparse` type error |
| yt-dlp download failure | Caught, re-raised as `dlt: download failed: {original message}`, exit 1 |
| Unsupported URL | yt-dlp error surfaced with same prefix |
| ffmpeg encoding failure | `dlt: encoding failed: {stderr}`, exit 1 |
| Temp dir cleanup | Always runs via `finally`, even on error |

---

## Testing

**Runner:** `pytest`

| Test file | What it covers |
|---|---|
| `test_pitcher.py` | Generate a 440 Hz sine wave WAV, shift by +2 semitones, verify dominant frequency is ~494 Hz |
| `test_cli.py` | Filename slug generation: special chars, spaces, semitone sign formatting |
| `test_integration.py` | Mock yt-dlp API and ffmpeg subprocess; verify full pipeline wiring and temp dir cleanup |

---

## Packaging

`pyproject.toml` with:
- `[project.scripts] dlt = "dlt.cli:main"`
- Python ≥ 3.10
- Dependencies: `yt-dlp`, `pedalboard`, `soundfile`, `imageio-ffmpeg`

Primary install method: `pipx install dlt`
