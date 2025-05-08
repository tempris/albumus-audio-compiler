# Albumus Audio Compiler - Setup Guide

This guide explains how to install and run the **Albumus Audio Compiler**, a Python-based tool that compiles structured music folders into fully tagged, multi-format albums with embedded album art.

---

## 📦 Requirements

Before you begin, install the following:

### 1. Python 3.9+
Install from [https://www.python.org/downloads/](https://www.python.org/downloads/)

On Linux, ensure `tkinter` is also installed:
```bash
sudo apt install python3-tk
````

### 2. FFmpeg

Albumus uses FFmpeg for audio conversion. Download and install:

* [FFmpeg Official Site](https://ffmpeg.org/download.html)
* Make sure it's accessible from the terminal:

```bash
ffmpeg -version
```

---

## 📚 Python Dependencies

Install Python packages using:

```bash
pip install -r requirements.txt
```

This installs:

* `mutagen` – for reading/writing metadata
* `Pillow` – for image resizing
* `customtkinter` – GUI support

---

## 📂 Folder Structure Overview

```
albumus-audio-compiler/
├── config/
│   ├── settings.json              # Global settings (created or updated automatically)
│   └── default/
│       └── project/config.json    # Default per-project config fallback
├── example/
│   └── min/                       # A minimal working project
├── source/
│   └── python_packages_custom/    # Core logic and task scripts
└── gui.py                         # Launches the GUI
```

---

## 🚀 First-Time Setup

1. **Clone or extract the project**

2. **(Optional) Review default settings**

   * Edit `config/default/project/config.json` to customize output formats, image sizes, and audio quality defaults.

3. **Run the GUI**

```bash
python gui.py
```

4. **Or run directly from the terminal**

```bash
python source/python_packages_custom/compile_audio.py
```

---

## 🧪 Using the Examples

You can use `example/min` as a reference project or duplicate it to create your own.

### Create a New Project

1. Copy `example/min` to a new location.

2. Ensure the copied folder contains:

   * `config.json`
   * An `in/` folder with subfolders structured as:

     ```
     in/
     └── Artist/
         └── Album/
             ├── audio files (.wav, .flac, etc.)
             ├── folder.png
             ├── metadata_album.json
             ├── metadata_artist.json
             └── metadata_track.json
     ```

3. Select this directory from the GUI or update `config/settings.json`:

```json
{
  "dir": "./my_new_project",
  "dir_recent": [
    "./my_new_project"
  ],
  "dir_recent_max": 10
}
```

---

## 🐞 Troubleshooting

| Problem                    | Solution                                          |
| -------------------------- | ------------------------------------------------- |
| FFmpeg not found           | Ensure it’s installed and added to system PATH    |
| GUI won’t launch           | Install `customtkinter` and run with Python 3.9+  |
| Logs show missing metadata | Check for required `.json` files in album folders |
| No output generated        | Verify folder names, metadata, and config formats |

---

## ✅ Ready to Go

Once set up, you can compile full albums, clear output, and generate embedded cover art with just a few clicks or commands.

Happy compiling!
