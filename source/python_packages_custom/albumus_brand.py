import os

arts = [
    r"""                        ▄▄██████▄▄
                  ▄▄█   ▀████████▀   █▄▄
                ▄██▀     ▀██████▀     ▀██▄
               ██▀        ▀████▀        ▀██
              ██▀    ▄██▄        ▄██▄    ▀██
              ██   ▄██████████████████▄   ██
              ██  ██████████████████████  ██
            ▄███  ██████████████████████  ███▄
            ████  ██████████████████████  ████
            ████  ██    ▀▀▀▀██▀▀▀▀    ██  ████
            ████  ██        ██        ██  ████
            ████  █████▄▄▄  ██  ▄▄▄█████  ████
            ▀██▀  ████████  ██  ████████  ▀██▀
                  ████████  ██  ████████
                  ████████      ████████
                  ▀███████      ███████▀
                    ▀█████      █████▀
                      ▀███      ███▀
                        ▀█      █▀""",
    r"""   █    ▀██▀    ▀████▄ ▀██  ██▀ ▀███     ███▀ ▀██  ██▀ ▄███▀
  ███    ██      ██  ██ ██  ██   ████   ████   ██  ██  ██
 ██ ██   ██      █████  ██  ██   ██ ██ ██ ██   ██  ██  ▀███▄
███████  ██      ██  ██ ██  ██   ██  ███  ██   ██  ██     ██
██   ██ ▄█████▄ ▄████▀  ▀████▀  ▄██▄  █  ▄██▄  ▀████▀  ▄███▀""",
    r"""                  █   █   █ █▀▀▄ ▀█▀ ▄▀▀▀▄
                 █▄█  █   █ █  █  █  █   █
                █   █ ▀▄▄▄▀ █▄▄▀ ▄█▄ ▀▄▄▄▀""",
    r"""         ▄▀▀▀ ▄▀▀▀▄ ▄▀▄ ▄▀▄ █▀▀▄ ▀█▀ █   █▀▀▀ █▀▀▄
         █    █   █ █ ▀▄▀ █ █▀▀   █  █   █▀▀▀ █▀▀▄
         ▀▄▄▄ ▀▄▄▄▀ █     █ █    ▄█▄ █▄▄ █▄▄▄ █  █"""
]

arts_small = [
    r"""      ▄▀ ▀██▀ ▀▄
    ▄▀ ▄█▄▄▄▄█▄ ▀▄
    █ ██████████ █
   ██ █   ██   █ ██
   ██ ███ ██ ███ ██
      ███    ███
       ▀█    █▀""",
    "Albumus Audio Compiler"
]

reset_color = "\x1b[0m"

def generate_gradient(start_hex, end_hex, steps):
    """Generate a list of ANSI 24-bit color strings in a gradient."""
    start = tuple(int(start_hex[i:i+2], 16) for i in (0, 2, 4))
    end = tuple(int(end_hex[i:i+2], 16) for i in (0, 2, 4))

    if steps <= 1:
        r = round((start[0] + end[0]) / 2)
        g = round((start[1] + end[1]) / 2)
        b = round((start[2] + end[2]) / 2)
        return [f"\x1b[38;2;{r};{g};{b}m"]

    gradient = []
    for i in range(steps):
        r = round(start[0] + (end[0] - start[0]) * i / (steps - 1))
        g = round(start[1] + (end[1] - start[1]) * i / (steps - 1))
        b = round(start[2] + (end[2] - start[2]) * i / (steps - 1))
        gradient.append(f"\x1b[38;2;{r};{g};{b}m")

    return gradient

def get_colors(force_color256=False, line_count=1):
    """Get ANSI color strings, either 24-bit or fallback yellow."""
    supports_256 = force_color256 or "256color" in os.environ.get("TERM", "")
    if supports_256:
        return generate_gradient("b3c8d6", "8fa2aa", line_count)
    return ['\x1b[33m'] * line_count  # Yellow

def get_art_string(force_color256, art):
    """Return colored version of a single ASCII art string."""
    if os.environ.get("NO_COLOR"):
        return art

    lines = art.split('\n')
    colors = get_colors(force_color256, len(lines))
    return '\n'.join(f"{color}{line}{reset_color}" for color, line in zip(colors, lines))

def get_brand_string(force_color256=False, small=False):
    """Return full colored intro string."""
    art_list = arts_small if small else arts
    newline = "" if small else "\n"
    output = "\n" + newline
    for i, art in enumerate(art_list):
        output += get_art_string(force_color256, art) + "\n"
        if i < len(art_list) - 1:
            output += "\n" + newline
    # return output.strip()
    output += newline
    return output
