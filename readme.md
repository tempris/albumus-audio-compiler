# 🎵 Albumus Audio Compiler

**Albumus Audio Compiler** is a Python-based tool that converts raw audio files into fully tagged, multi-format music albums with embedded cover art. It's ideal for musicians, archivists, and developers who want streamlined batch processing using structured folders.

---

## 📦 Features

- Compile albums from `.wav`, `.flac`, `.mp3`, or `.ogg` source files
- Export to `FLAC`, `MP3`, `OGG`, and `WAV` formats
- Auto-detect track numbers and apply formatted output names
- Embed album art using `folder.png`
- Generate album art variants (e.g., `cover.jpg`, `thumb.jpg`, etc.)
- Output organized into per-format subfolders
- Run via GUI (`gui.py`) or CLI (`compile_audio.py`)
- Includes colorized logging and full output tracking

---

## 🖥️ Requirements

- Python 3.9 or higher
- [FFmpeg](https://ffmpeg.org/) (must be available in system PATH)
- Python packages:
  - `mutagen`
  - `Pillow`
  - `customtkinter` (only needed for GUI)

Install with:
```bash
pip install -r requirements.txt
````

---

## 🚀 Quick Start

### GUI (Recommended)

```bash
python gui.py
```

From the interface, you can:

* Select a project directory
* Click `compile_audio` to convert tracks
* Click `clear_output` to delete the output directory

### Command Line

Compile albums directly:

```bash
python source/python_packages_custom/compile_audio.py
```

Clear generated output:

```bash
python source/python_packages_custom/clear_output.py
```

---

## 📂 Project Structure

### Example Input

```
example/
├── config.json
└── in/
    └── TitleArtist/
        ├── metadata_artist.json
        └── 01_TitleAlbum/
            ├── 01_ExampleAudioFileWAV.wav
            ├── 02_ExampleAudioFileFLAC.flac
            ├── 03_ExampleAudioFileMP3.mp3
            ├── 04_ExampleAudioFileOGG.ogg
            ├── folder.png
            ├── metadata_album.json
            └── metadata_track.json
```

### Example Output

```
out/
└── TitleArtist/
    └── 01_TitleAlbum/
        ├── cover.jpg
        ├── thumb.jpg
        ├── flac/
        │   └── 01_ExampleAudioFileWAV.flac
        ├── mp3/
        │   └── 01_ExampleAudioFileWAV.mp3
        ├── ogg/
        │   └── 01_ExampleAudioFileWAV.ogg
        └── wav/
            └── 01_ExampleAudioFileWAV.wav
```

---

## ⚙️ Configuration Overview

* `config/settings.json`: Controls selected project directory and recent paths
* Per-project `config.json` files override defaults
* Default values can be set in `config/default/project/config.json`

---

## 📖 Wiki & Docs

* [Setup Guide](./wiki/setup.md)
* [GUI Reference](./wiki/gui.md)
* [Command Line Tasks](./wiki/terminal.md)
* [Configuration Reference](./wiki/config.md)

---

## 📜 License

Licensed under GNU GPL v3. Projects created using this tool **are not required** to use the GPL license and may be licensed however you wish.

---

## ⚠️ Disclaimer

This tool is provided “as-is” with no warranty. Use at your own risk. Contributions are welcome!
