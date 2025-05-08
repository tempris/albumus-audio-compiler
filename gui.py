import json
import os
import platform
import re
import subprocess
import sys
import tkinter.filedialog as filedialog
import io
from contextlib import redirect_stdout, redirect_stderr

SCRIPT_TITLE = "Albumus Audio Compiler"
LOG_TAG_GUI = '[💻 GUI]'

print(f'{LOG_TAG_GUI} [Init] {SCRIPT_TITLE} Importing...')

# Path to this Python file
LOCATION_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# Add required directories to sys.path
for subdir in ["source/python_packages_custom", "source/python_packages", ""]:
    LOCATION_PACKAGES = os.path.abspath(os.path.join(LOCATION_SCRIPT, subdir))
    if LOCATION_PACKAGES not in sys.path:
        sys.path.insert(0, LOCATION_PACKAGES)

from source.python_packages import customtkinter
from source.python_packages.supports_color import supportsColor
from source.python_packages.CTkToolTip import *
from source.python_packages_custom.cure_log import CureLog

logger = CureLog(os.path.join(LOCATION_SCRIPT, '_log/gui.log'))

logger.log("debug", LOG_TAG_GUI, "sys.path:", sys.path)
logger.log("init", LOG_TAG_GUI, "Import complete.")

from source.python_packages_custom.albumus_brand import get_brand_string
TERMINAL_COLOR_256 = supportsColor.stdout and supportsColor.stdout.has256
intro_text = get_brand_string(force_color256=TERMINAL_COLOR_256, small=False)
logger.plain(intro_text)

logger.log("init", LOG_TAG_GUI, "Initializing...")

# Toggle to control terminal opening and hiding main window
EXPERIMENT_HIDE_TERMINAL_MAIN = False  # Experimental: Set to True to hide main script window
EXPERIMENT_HIDE_TERMINAL_TASK = False  # Experimental: Set to True to hide terminal for Gulp tasks

from source.python_packages_custom import albumus_defaults
# albumus_defaults.configEnsure()

f_stdout = io.StringIO()
f_stderr = io.StringIO()

with redirect_stdout(f_stdout), redirect_stderr(f_stderr):
    albumus_defaults.configEnsure()

combined_output = f_stdout.getvalue() + f_stderr.getvalue()
if combined_output.strip():
    # logger.plain(f"{LOG_TAG_GUI} Output from configEnsure:\n{combined_output}")
    logger.plain(combined_output)

def load_json_config(file_path):
    """
    Load a JSON configuration file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data or an empty dictionary if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.log('error', LOG_TAG_GUI, f"[Configuration] Config file not found at: \"[[ANSI_OFF]]{file_path}[[ANSI_ON]]\"")
    except json.JSONDecodeError as e:
        logger.log('error', LOG_TAG_GUI, "[Configuration] Error decoding JSON file:", e)
    return {}  # Return an empty dictionary as a fallback

# Load the config.json
path_config_settings = os.path.join(LOCATION_SCRIPT, 'config/settings.json')
config_settings = load_json_config(path_config_settings)

def validate_directory(directory):
    """
    Validate that the directory contains a `config.json` file and an `in` subdirectory.
    """
    config_file = os.path.join(directory, 'config.json')
    subdir = os.path.join(directory, 'in')
    return os.path.isfile(config_file) and os.path.isdir(subdir)

# Validate recent project directories on startup
valid_recent_dirs = [d for d in config_settings.get('dir_recent', []) if validate_directory(d)]
if valid_recent_dirs != config_settings.get('dir_recent', []):
    logger.log('warn', LOG_TAG_GUI, "Invalid directories found in recent project list. Removing them.")
    config_settings['dir_recent'] = valid_recent_dirs

    # Save the cleaned recent project directories to config.json
    try:
        with open(path_config_settings, 'w', encoding='utf-8') as f:
            json.dump(config_settings, f, indent=4)
        logger.log('debug', LOG_TAG_GUI, "Updated config.json with valid recent project directories.")
    except Exception as e:
        logger.log('error', LOG_TAG_GUI, "Error saving updated config.json during startup:", e)

def update_recents_dropdown(recent_dirs):
    """
    Update the CTkOptionMenu with recent project directories.
    Fallback to 'dir' value if recent_dirs is empty.
    """
    try:
        if not recent_dirs:
            fallback_dir = config_settings.get('dir', '')
            logger.log('warn', LOG_TAG_GUI, f"Recent project directories list is empty, falling back to: \"[[ANSI_OFF]]{fallback_dir}[[ANSI_ON]]\".")
            recent_dirs = [fallback_dir] if fallback_dir else ["No directories available"]

        recent_dir_menu.configure(values=recent_dirs)  # Update the dropdown options
        recent_dir_menu.set(recent_dirs[0])  # Select the first entry as default
    except Exception as e:
        logger.log('error', LOG_TAG_GUI, "[Configuration] Error updating recent project directories menu:", e)

last_valid_dir = config_settings.get('dir', '')  # Store the last valid directory

def update_config_dir(new_dir):
    """
    Update the 'dir' in config/settings.json and validate the directory.
    Remove invalid directories permanently and ensure the fallback is the last valid directory.
    """
    global last_valid_dir

    # Load the current recent project directories
    dir_recent = config_settings.get('dir_recent', [])

    # Check if the directory is local to the script
    if os.path.isabs(new_dir):
        relative_to_script = os.path.relpath(new_dir, LOCATION_SCRIPT)
        if not relative_to_script.startswith('..'):
            # Replace backslashes with forward slashes and add './' prefix if needed
            new_dir = f"./{relative_to_script.replace(os.sep, '/')}" if not relative_to_script.startswith('.') else relative_to_script.replace(os.sep, '/')

    if not validate_directory(new_dir):
        logger.log('warn', LOG_TAG_GUI, "Selected directory is invalid, removing it from recent project directories:", {"invalid": new_dir})

        # Remove the invalid directory from the recent project list
        if new_dir in dir_recent:
            dir_recent.remove(new_dir)
            config_settings['dir_recent'] = dir_recent  # Update the config_settings dictionary

            # Save changes to config.json
            try:
                with open(path_config_settings, 'w', encoding='utf-8') as f:
                    json.dump(config_settings, f, indent=4)
                logger.log('debug', LOG_TAG_GUI, "Removed invalid directory from recent project directories:", {"removed": new_dir})
            except Exception as e:
                logger.log('error', LOG_TAG_GUI, "Error saving updated config.json:", e)

        # Revert to the last valid directory
        logger.log('debug', LOG_TAG_GUI, "Reverting to last valid directory:", {"last_valid_dir": last_valid_dir})
        update_recents_dropdown(dir_recent)  # Update the dropdown
        result_text.configure(
            text=f"Invalid directory selected: \"{new_dir}\". Reverted to last valid directory: \"{last_valid_dir}\"",
            text_color="red"
        )
        return

    logger.log('info', LOG_TAG_GUI, "Valid project directory selected:", {"new_dir": new_dir})

    try:
        # Update the 'dir' in the config file
        config_settings['dir'] = new_dir
        last_valid_dir = new_dir  # Set the new directory as the last valid directory

        # Manage the recent project directories
        if new_dir in dir_recent:
            dir_recent.remove(new_dir)  # Avoid duplication
        dir_recent.insert(0, new_dir)  # Add to the top
        dir_recent = dir_recent[:config_settings.get('dir_recent_max', 10)]  # Keep only the most recent project directories
        config_settings['dir_recent'] = dir_recent

        # Save the updated configuration
        with open(path_config_settings, 'w', encoding='utf-8') as f:
            json.dump(config_settings, f, indent=4)

        logger.log('debug', LOG_TAG_GUI, "Directory and recent project directories updated:", {"new_dir": new_dir, "dir_recent": dir_recent})
        update_recents_dropdown(dir_recent)  # Update the dropdown
        result_text.configure(text=f"Directory updated to: \"{new_dir}\"", text_color="green")
    except Exception as e:
        logger.log('error', LOG_TAG_GUI, "[Configuration] Error updating config.json:", e)
        result_text.configure(text=f"Failed to update directory to: \"{new_dir}\"", text_color="red")

# Determine the current operating system
current_platform = platform.system().lower()
logger.log('info', LOG_TAG_GUI, f"Detected platform: \"[[ANSI_OFF]]{current_platform}[[ANSI_ON]]\"")

is_supported = False
padding = 4

if current_platform == 'windows' or current_platform == 'linux':
    is_supported = True
    logger.log('success', LOG_TAG_GUI, f"Platform supported: \"[[ANSI_OFF]]{current_platform}[[ANSI_ON]]\"")
else:
    logger.log('error', LOG_TAG_GUI, f"Platform not supported: \"[[ANSI_OFF]]{current_platform}[[ANSI_ON]]\"")

logger.log("init", LOG_TAG_GUI, "Complete.")

def run_command(command_args):
  LOG_TAG_TASK = LOG_TAG_GUI + " [🧾 Task]"
  logger.log('begin', LOG_TAG_TASK, "Running command:", command_args)
  try:
    process = subprocess.Popen(
      command_args,
      cwd=LOCATION_SCRIPT,
      env={**os.environ, "PYTHONIOENCODING": "utf-8"},
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
      encoding='utf-8',  # force decoding
      errors='replace',   # avoid crashes on bad bytes
      bufsize=1,  # Line-buffered
      universal_newlines=True
    )

    for line in process.stdout:
      stripped = line.rstrip()
      if stripped:
        logger.plain(stripped)

    process.wait()

    if process.returncode != 0:
        logger.log('error', LOG_TAG_TASK, "Exited with Error Code:", process.returncode, [
          "[[NEWLINES]]", 
          "", [
            "[[LIST]]",
            "See above for more..."
          ]
        ])
        result_text.configure(text="Error: See Log", text_color="red")
    else:
        logger.log('success', LOG_TAG_TASK, "Command succeeded.")
        result_text.configure(text=f"Command executed: {command_args[0]}", text_color="green")

  except Exception as e:
    logger.log('error', LOG_TAG_TASK, "Exception while running command:", e)
    result_text.configure(text=f"Exception: {e}", text_color="red")


COLOR_SYSTEM = customtkinter.get_appearance_mode()
def color_light_dark(color_light, color_dark):
    if (COLOR_SYSTEM == "Light"):
        return color_light
    return color_dark

def color_hover_shade(hex_color, factor=0.5):
    """Returns a darker shade of the input hex color by the specified factor."""
    # Remove the '#' if it's present
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    if (COLOR_SYSTEM == "Light"):
        factor *= 0.375

    # Reduce brightness by the factor
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))

    # Ensure the values are within the valid range [0, 255]
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    # Convert RGB back to hex
    darker_hex = f'#{r:02x}{g:02x}{b:02x}'
    return darker_hex

font_size__title = 18
font_size__subtitle = 14

config_padding = {
    "padx": padding,
    "pady": padding
}
config_tooltip = {
    "delay": 0,
    "x_offset": 0,
    "y_offset": 32,
    **config_padding
}

class MyScrollableButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values, button_color="#1976D2", **kwargs):
        super().__init__(master, label_text=title, **kwargs)
        logger.log('debug', LOG_TAG_GUI, f"Initializing scrollable button frame for category: \"[[ANSI_OFF]]{title}[[ANSI_ON]]\"")
        self.values = values

        for i, task in enumerate(self.values):
            task_name = task["name"]
            tooltip_message = task.get("tooltip", task_name)
            command_args = task["command"]

            button = customtkinter.CTkButton(
                self,
                text=task_name.replace("_", " ").title(),
                command=lambda c=command_args: run_command(c),
                fg_color=button_color,
                hover_color=color_hover_shade(button_color),
                width=0
            )
            button.grid(
                row=i,
                column=0,
                sticky="ew",
                **config_padding
            )
            CTkToolTip(
                button,
                message=tooltip_message,
                **config_tooltip
            )

        # Ensure the column containing buttons can stretch
        self.grid_columnconfigure(
            0,
            weight=1
        )

def open_directory_explorer():
    """
    Open file explorer to select a directory and update the config.
    Only allow valid directories to be selected.
    """
    logger.log('info', LOG_TAG_GUI, "Opening directory selector.")

    selected_dir = filedialog.askdirectory(initialdir=recent_dir_menu.get(), title="Select Directory")
    if selected_dir:  # If a directory is selected
        update_config_dir(selected_dir)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        logger.log('init', LOG_TAG_GUI, [
            "[[NEWLINES]]",
            "Building initializing...", [
                "[[LIST]]",
                "This can take some time..."
            ]
        ])

        icon_path = os.path.join(LOCATION_SCRIPT, "source/resource/icon.ico") if current_platform == 'windows' else os.path.join(LOCATION_SCRIPT, "source/icon_128px.png")
        if os.path.exists(icon_path):
            if current_platform == 'windows':
                self.iconbitmap(icon_path)
            else:
                # icon_image = customtkinter.CTkImage(file=icon_path)
                # self.iconphoto(False, icon_image)
                logger.log('warn', LOG_TAG_GUI, "Custom window icons are not supported on this platform.")
        else:
            logger.log('warn', LOG_TAG_GUI, "Icon file not found:", {"icon_path": icon_path})

        # Hide the main window if specified
        if EXPERIMENT_HIDE_TERMINAL_MAIN:
            self.withdraw()  # Hides the main window
            logger.log('debug', LOG_TAG_GUI, "Main script window hidden.")

        self.title(SCRIPT_TITLE)
        self.geometry("600x400")

        main_row = 0

        logger.log('info', LOG_TAG_GUI, "UI Building...")
        if is_supported:

            # Configuration UI ===========================
            # Top Frame for Directory Configuration
            self.top_frame = customtkinter.CTkFrame(
                self,
                fg_color=color_light_dark("#cccccc", "#333333")
            )
            self.top_frame.grid(
                row=main_row,
                column=0,
                sticky="ew",
                **config_padding
            )

            config_row = 0
            config_column = 0

            # self.label_config = customtkinter.CTkLabel(
            #     self.top_frame,
            #     text="Project",
            #     font=customtkinter.CTkFont(
            #         size=font_size__title,
            #         weight="bold"
            #     )
            # )
            # config_row_label = config_row
            # config_row += 1

            self.label_dir = customtkinter.CTkLabel(
                self.top_frame,
                text="Project",
                font=customtkinter.CTkFont(size=font_size__subtitle, weight="bold")
            )
            self.label_dir.grid(
                row=config_row,
                column=config_column,
                **config_padding
            )
            config_column += 1

            self.recent_dir_menu = customtkinter.CTkOptionMenu(
                self.top_frame,
                values=[],  # Initialize with an empty list
                command=update_config_dir
            )
            self.recent_dir_menu.grid(
                row=config_row,
                column=config_column,
                sticky="ew",
                **config_padding
            )
            self.top_frame.grid_columnconfigure(
                config_column,
                weight=1
            )  # Make the entry field stretch
            CTkToolTip(
                self.recent_dir_menu,
                message=f"Select a recent project directory.",
                **config_tooltip
            )
            config_column += 1

            # Add "Browse" button for file explorer
            self.button_browse_dir = customtkinter.CTkButton(
                self.top_frame,
                text="🔍",
                command=open_directory_explorer,
                fg_color=color_light_dark("#3B8ED0", "#286ba1"),
                hover_color=color_hover_shade(color_light_dark("#3B8ED0", "#286ba1")),
                width=0  # Allow dynamic width based on text
            )
            self.button_browse_dir.grid(
                row=config_row,
                column=config_column,
                **config_padding
            )
            CTkToolTip(
                self.button_browse_dir,
                message=f"Browse for new project directory.",
                **config_tooltip
            )
            config_column += 1

            main_row += 1

            # Task UI ===========================
            self.frame_task = customtkinter.CTkScrollableFrame(
                self,
                orientation="horizontal",
                fg_color=color_light_dark("#cccccc", "#333333")
            )
            self.frame_task.grid(
                row=main_row,
                column=0,
                sticky="nsew",
                **config_padding
            )
            self.grid_rowconfigure(
                main_row,
                weight=1
            )  # Stretch the row containing the task ui

            task_row = 0

            self.frame_task.grid_rowconfigure(
                task_row,
                weight=1
            )  # fill height
            self.frame_task.grid_columnconfigure(
                0,
                weight=1
            )  # fill width
            task_row += 1

            from source.python_packages_custom.gui_tasks import get_gui_tasks
            tasks_by_category = get_gui_tasks()

            for idx, category in enumerate(tasks_by_category):
                title = category["name"]
                color = category["color"]
                tasks = category["tasks"]
                
                logger.log('debug', LOG_TAG_GUI, f"Adding tasks for category: \"[[ANSI_OFF]]{title}[[ANSI_ON]]\"")

                self.scrollable_button_frame = MyScrollableButtonFrame(
                    self.frame_task,
                    title=title,
                    values=tasks,
                    button_color=color # default: "#1976D2"
                )
                self.scrollable_button_frame.grid(row=0, column=idx, sticky="nsew", **config_padding)


            # id_t = 0

            # for category, tasks in tasks_by_category.items():
            #     logger.log('debug', LOG_TAG_GUI, f"Adding tasks for category: \"[[ANSI_OFF]]{category}[[ANSI_ON]]\"")
            #     self.scrollable_button_frame = MyScrollableButtonFrame(
            #         self.frame_task,
            #         title=category,
            #         # width=0,
            #         values=tasks
            #     )
            #     self.scrollable_button_frame.grid(
            #         row=0,
            #         column=id_t,
            #         sticky="nsew",
            #         **config_padding
            #     )

            #     id_t += 1

            main_row += 1

        main_row += 1

        # Result UI ===========================

        self.result_text = customtkinter.CTkLabel(self, text="Select a task")
        self.result_text.grid(row=main_row, column=0, sticky="ew", **config_padding)

        self.grid_columnconfigure(0, weight=1)

        logger.log('success', LOG_TAG_GUI, "UI Built.")
        logger.log('init', LOG_TAG_GUI, "Building complete.")

try:
    app = App()
    result_text = app.result_text
    recent_dir_menu = app.recent_dir_menu

    # Populate recent project dropdown after initializing UI
    update_recents_dropdown(config_settings.get('dir_recent', []))  # Fallback will be handled if empty

    if is_supported:
        result_text.configure(text=f"Supported operating system: {current_platform}. Select a task.", text_color="green")
    else:
        result_text.configure(text=f"Unsupported operating system: {current_platform}", text_color="red")

    logger.log('begin', LOG_TAG_GUI, "Running...")
    app.mainloop()
    outro_text = get_brand_string(force_color256=TERMINAL_COLOR_256, small=True)
    logger.plain(outro_text)
    logger.log('end', LOG_TAG_GUI, "Closing...")
    logger.log('shutdown', LOG_TAG_GUI, "Shutting Down...")
except Exception as e:
    logger.log('error', LOG_TAG_GUI, "Error initializing app:", e)
