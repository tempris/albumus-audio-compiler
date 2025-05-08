# Albumus Audio Compiler - Configuration Reference

This guide outlines the structure and purpose of configuration files used by the **Albumus Audio Compiler**.

Albumus supports two key configuration files:

1. **Global Settings:** `config/settings.json` – Manages project paths and recent selections
2. **Project Configuration:** `config.json` (inside each project) – Customizes album output behavior

---

## 1. Global Settings (`config/settings.json`)

Used by both GUI and CLI scripts to track which project is active and maintain history.

### Example:
```json
{
  "dir": "./example/min",
  "dir_recent": [
    "./example/min",
    "./example/full"
  ],
  "dir_recent_max": 10
}
````

### Fields:

| Key              | Type      | Description                                      |
| ---------------- | --------- | ------------------------------------------------ |
| `dir`            | string    | The current working project directory            |
| `dir_recent`     | string\[] | List of most recently used directories           |
| `dir_recent_max` | number    | Maximum number of recent directories to remember |

---

## 2. Project Configuration (`config.json` in each project folder)

This file controls how audio is compiled, how album art is generated, and how FFmpeg handles audio encoding.

### Example:

```json
{
  "formats": ["flac", "mp3", "ogg", "wav"],
  "output": {
    "art_sizes": {
      "thumb": [64, 64],
      "cover": [300, 300],
      "folder": [512, 512],
      "large": [1000, 1000]
    },
    "image_quality": 95,
    "image_output_format": "JPEG"
  },
  "logging": {
    "log_relative_paths": true
  },
  "ffmpeg": {
    "bitrate_strategy": {
      "mp3": {
        "fallback_qscale": 2
      },
      "ogg": {
        "fallback_qscale": 10,
        "min_quality": 0,
        "max_quality": 10,
        "base_bitrate": 64000,
        "step": 16000
      }
    }
  }
}
```

### Sections:

#### `formats`

* **Type:** array of strings
* **Options:** `flac`, `mp3`, `ogg`, `wav`
* **Purpose:** Selects which audio formats to generate.

#### `output.art_sizes`

* **Type:** object
* **Description:** Defines the dimensions of generated `.jpg` images from `folder.png`.

#### `output.image_quality`

* **Type:** number (0–100)
* **Purpose:** Sets JPEG quality for output images.

#### `output.image_output_format`

* **Type:** string
* **Options:** `JPEG`, `PNG`, etc.
* **Purpose:** Defines image format used when resizing album art.

#### `logging.log_relative_paths`

* **Type:** boolean
* **Purpose:** Controls whether paths in the log are relative to the project root.

#### `ffmpeg.bitrate_strategy`

* **Purpose:** Customizes how FFmpeg compresses audio.

##### For `mp3`

| Key               | Type   | Description                                |
| ----------------- | ------ | ------------------------------------------ |
| `fallback_qscale` | number | Used if source bitrate can't be determined |

##### For `ogg`

| Key               | Type   | Description                              |
| ----------------- | ------ | ---------------------------------------- |
| `fallback_qscale` | number | Default quality level if bitrate missing |
| `min_quality`     | number | Minimum quality setting                  |
| `max_quality`     | number | Maximum quality setting                  |
| `base_bitrate`    | number | Starting bitrate threshold               |
| `step`            | number | Size of steps between quality levels     |

---

## Where to Place Configs

* Global config:

  * `config/settings.json`
  * `config/default/settings.json` (fallback used if missing)
* Project config:

  * `your_project/config.json`
  * Default fallback at: `config/default/project/config.json`

---

## Notes

* `folder.png` is required for album art generation.
* All `.json` files must be UTF-8 encoded and well-formed.
* Track metadata must match the actual audio filenames.
