# Albumus Audio Compiler - GUI Guide

The Albumus GUI (`gui.py`) provides a simple, interactive interface to select project folders and run audio-related tasks such as compiling albums and clearing output. It offers visual feedback, customizable settings, and a categorized task panel.

---

## 🚀 Launching the GUI

To run the GUI:
```bash
python gui.py
````

Make sure the following requirements are met:

* Python 3.9+
* `customtkinter` installed
* A valid `config/settings.json` exists (will be created if missing)

---

## 🖼 GUI Features

### Project Directory Management

* **Recent Directory Dropdown:**

  * Select from previously used project directories.
  * Automatically filters invalid paths.

* **Browse Button (🔍):**

  * Opens a file dialog to select a new project directory.
  * Updates the dropdown and config settings automatically.

### Task Buttons

Tasks are grouped by category and displayed in horizontal scrollable sections. Each button:

* Executes a predefined Python command.
* Shows a tooltip describing what it does.
* Logs output in the GUI and writes it to disk.

#### Default Tasks:

| Task            | Description                                           |
| --------------- | ----------------------------------------------------- |
| `compile_audio` | Compiles input files into tagged, multi-format albums |
| `clear_output`  | Deletes the project's output directory (`out/`)       |

### Status Panel

* Located at the bottom of the interface
* Displays real-time task results or error messages
* Color-coded: Green = success, Red = error

---

## 🔧 Configuration

The GUI references:

* `config/settings.json` to track the current working project
* Automatically updates:

  * `dir`: currently selected project
  * `dir_recent`: history of recent projects
  * `dir_recent_max`: how many recent paths to remember

If invalid directories are detected on launch, they are removed from the dropdown list automatically.

---

## 🧪 Example Workflow

1. Launch the app:

   ```bash
   python gui.py
   ```

2. Use the dropdown or browse button to choose a valid project folder.

3. Click `compile_audio` to process the files in the `in/` directory.

4. View results in the status panel and check the `_log/` directory for full logs.

5. Use `clear_output` to delete generated output (`out/` folder) for a clean rebuild.

---

## 🛠 Troubleshooting

| Problem                      | Fix / Explanation                              |
| ---------------------------- | ---------------------------------------------- |
| "Config file not found"      | Ensure `config.json` exists in your project    |
| "Invalid directory selected" | Must include `config.json` and an `in/` folder |
| No output generated          | Make sure metadata JSON and audio files exist  |
| GUI doesn’t launch           | Confirm `customtkinter` is installed properly  |

---

## 📁 Log Files

All actions are logged in the `_log/` directory:

* `gui.log`
* `compile_audio.log`
* `clear_output.log`

These include timestamped entries, error reports, and command details.

---

## ✅ Summary

The GUI offers an easy-to-use interface for managing audio compilation projects without needing to use the terminal. It provides structure validation, task execution, logging, and feedback for a smooth user experience.
