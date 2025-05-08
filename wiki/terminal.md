# Albumus Audio Compiler - Terminal Guide

The Albumus Audio Compiler can be run entirely from the command line for fast, scriptable operation. This guide outlines how to use its available terminal tasks.

---

## ⚡ Available Terminal Commands

### 1. Compile Audio Files

This command reads from the project’s `in/` directory and generates multi-format, tagged output in `out/`.

```bash
python source/python_packages_custom/compile_audio.py
````

* Uses metadata from `metadata_artist.json`, `metadata_album.json`, and `metadata_track.json`
* Applies filename formatting (e.g., `01_TrackName`)
* Supports `.wav`, `.flac`, `.mp3`, `.ogg` as input
* Outputs to `flac/`, `mp3/`, `ogg/`, and `wav/` subdirectories

---

### 2. Clear Output Folder

Deletes the `out/` folder in the currently selected project directory.

```bash
python source/python_packages_custom/clear_output.py
```

Use this to clean up before re-compiling.

---

## 📁 Log Files

Each script writes detailed logs to the `_log/` directory:

| Log File            | Description                   |
| ------------------- | ----------------------------- |
| `compile_audio.log` | Output from compilation tasks |
| `clear_output.log`  | Output from clearing process  |
| `gui.log` (if used) | GUI interaction history       |

---

## 🧪 Best Practices

* Always check that your project contains:

  * A valid `config.json`
  * An `in/` directory with albums and metadata
  * A `folder.png` image for album art (optional but recommended)

* Run `clear_output.py` before rebuilding if you want a clean output directory.

* Use `python gui.py` if you prefer visual task selection and directory browsing.

---

## 🛠 Example Automation Script

Here’s how to compile and then package the output automatically:

```bash
python source/python_packages_custom/clear_output.py
python source/python_packages_custom/compile_audio.py
cd out && zip -r album_export.zip .
```

---

## ✅ Summary

The Albumus terminal interface is perfect for automation, batch processing, or advanced users who prefer command-line tools. Everything you can do in the GUI is also accessible through the terminal.
