# dlt

CLI tool for cover band musicians. Download audio from any music video URL and transpose it by N semitones — tempo preserved, fully self-contained.

```bash
dlt "https://youtu.be/abc123" -3
dlt "https://youtu.be/abc123" +5 -o rehearsal-eb.mp3
```

## Install

```bash
pipx install git+https://github.com/aaronkor/dlt.git
```

Or with pip:

```bash
pip install git+https://github.com/aaronkor/dlt.git
```

No system dependencies required — ffmpeg and all audio libraries are bundled.

## Usage

```
dlt <url> <semitones> [-o output.mp3]
```

| Argument | Description |
|---|---|
| `url` | Music video URL (YouTube, SoundCloud, and [1000+ other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)) |
| `semitones` | Integer from -12 to +12 |
| `-o / --output` | Output filename (default: auto-generated from video title) |

The default output filename is `{title}-{+/-N}st.mp3` (e.g. `bohemian-rhapsody--3st.mp3`).

## Examples

```bash
# Transpose down 3 semitones (e.g. to play in Eb)
dlt "https://youtu.be/abc123" -3

# Transpose up 5 semitones with a custom filename
dlt "https://youtu.be/abc123" +5 -o my-version.mp3
```

## Development

```bash
git clone https://github.com/aaronkor/dlt.git
cd dlt
pip install -e ".[dev]"
pytest
```
