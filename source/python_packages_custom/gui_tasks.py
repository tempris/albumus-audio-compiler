TASK_CATEGORIES = [
  {
    "name": "Build",
    "color": "#286ba1",
    "tasks": [
      {
        "name": "compile_audio",
        "tooltip": "Compile audio in selected project.",
        "command": ["python", '-u', "source/python_packages_custom/compile_audio.py"]
      }
    ]
  },
  {
    "name": "Reset",
    "color": "#9e3c35",
    "tasks": [
      {
        "name": "clear_output",
        "tooltip": "Delete generated output files.",
        "command": ["python", '-u', "source/python_packages_custom/clear_output.py"]
      }
    ]
  }
]

def get_gui_tasks():
  return TASK_CATEGORIES
