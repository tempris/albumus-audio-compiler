import os
import re
import time
import sys

class ANSI:
    def __init__(self):
        self.no_color = "NO_COLOR" in os.environ
        self.debug = False

        self.reset = "\x1b[0m"

        self.style = {
            "bold": "\x1b[1m",
            "dim": "\x1b[2m",
            "italic": "\x1b[3m",
            "underline": "\x1b[4m",
            "blink": "\x1b[5m",
            "reverse": "\x1b[7m",
            "hidden": "\x1b[8m",
            "strikethrough": "\x1b[9m",
            "doubleUnderline": "\x1b[21m",
            "framed": "\x1b[51m",
            "encircled": "\x1b[52m",
            "overlined": "\x1b[53m",
            "resetBoldDim": "\x1b[22m",
            "resetUnderline": "\x1b[24m",
            "resetBlink": "\x1b[25m",
            "resetReverse": "\x1b[27m",
            "resetHidden": "\x1b[28m",
            "resetStrikethrough": "\x1b[29m",
            "resetOverlined": "\x1b[55m"
        }

        self.fg = {
            "reset": "\x1b[39m",
            "black": "\x1b[30m",
            "red": "\x1b[31m",
            "green": "\x1b[32m",
            "yellow": "\x1b[33m",
            "blue": "\x1b[34m",
            "magenta": "\x1b[35m",
            "cyan": "\x1b[36m",
            "white": "\x1b[37m",
            "bright": {
                "black": "\x1b[90m",
                "red": "\x1b[91m",
                "green": "\x1b[92m",
                "yellow": "\x1b[93m",
                "blue": "\x1b[94m",
                "magenta": "\x1b[95m",
                "cyan": "\x1b[96m",
                "white": "\x1b[97m",
            },
        }

        self.bg = {
            "reset": "\x1b[49m",
            "black": "\x1b[40m",
            "red": "\x1b[41m",
            "green": "\x1b[42m",
            "yellow": "\x1b[43m",
            "blue": "\x1b[44m",
            "magenta": "\x1b[45m",
            "cyan": "\x1b[46m",
            "white": "\x1b[47m",
            "bright": {
                "black": "\x1b[100m",
                "red": "\x1b[101m",
                "green": "\x1b[102m",
                "yellow": "\x1b[103m",
                "blue": "\x1b[104m",
                "magenta": "\x1b[105m",
                "cyan": "\x1b[106m",
                "white": "\x1b[107m",
            },
        }

        self.hc = {
            "fg": {k: self.fg["bright"][k] for k in self.fg["bright"]},
            "bg": {k: self.bg[k] for k in self.bg if not isinstance(self.bg[k], dict)},
        }

        self.bc = {
            "fg": {
                "black": self.fg["bright"]["black"],
                "red": self.fg["bright"]["red"],
                "green": self.fg["bright"]["green"],
                "yellow": self.fg["yellow"],
                "blue": self.fg["bright"]["blue"],
                "magenta": self.fg["bright"]["magenta"],
                "cyan": self.fg["bright"]["cyan"],
                "white": self.fg["bright"]["white"],
            },
            "bg": self.hc["bg"],
        }

        self.cursor = {
            "up": lambda n=1: f"\x1b[{n}A",
            "down": lambda n=1: f"\x1b[{n}B",
            "right": lambda n=1: f"\x1b[{n}C",
            "left": lambda n=1: f"\x1b[{n}D",
            "moveTo": lambda row, col: f"\x1b[{row};{col}H",
            "show": "\x1b[?25h",
            "hide": "\x1b[?25l",
            "save": "\x1b7",
            "restore": "\x1b8"
        }

        self.screen = {
            "clear": "\x1b[2J",
            "clearFromCursorToEnd": "\x1b[0J",
            "clearFromCursorToStart": "\x1b[1J",
            "clearLine": "\x1b[2K",
            "clearLineToEnd": "\x1b[0K",
            "clearLineToStart": "\x1b[1K",
        }

        self.color256 = {
            "fg": lambda n: f"\x1b[38;5;{n}m",
            "bg": lambda n: f"\x1b[48;5;{n}m"
        }

        self.colorRGB = {
            "fg": lambda r, g, b: f"\x1b[38;2;{r};{g};{b}m",
            "bg": lambda r, g, b: f"\x1b[48;2;{r};{g};{b}m"
        }

        self.test = {
            "standard": self.test_standard,
            "color256": self.test_color256,
            "screen": self.test_screen,
            "cursor": self.test_cursor,
            "reveal": self.test_reveal,
            "clean": self.test_clean,
            "all": self.test_all
        }

    def set_debug(self, value):
        self.debug = value

    def reveal(self, text):
        ansi_regex = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_regex.sub(lambda m: f"{m.group(0)}{m.group(0).replace(chr(27), '\\x1b')}", text)

    def format(self, code, *messages):
        ansi_code = '' if self.no_color else (code or self.reset)
        reset_code = '' if self.no_color else self.reset
        text = " ".join(messages)
        text = text.replace("[[ANSI_ON]]", ansi_code).replace("[[ANSI_OFF]]", reset_code)
        return f"{ansi_code}{text}{reset_code}"
    
    def clean(self, input_string):
        ansi_regex = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        lines = input_string.split('\n')
        processed_lines = []

        active_codes = {
            "foreground": '',
            "background": '',
            "formatting": [],
        }

        def categorize_code(code):
            if code == self.reset:
                active_codes["foreground"] = ''
                active_codes["background"] = ''
                active_codes["formatting"] = []
            elif re.match(r'^\x1b\[(3[0-7]|9[0-7])m$', code):
                active_codes["foreground"] = code
            elif re.match(r'^\x1b\[(4[0-7]|10[0-7])m$', code):
                active_codes["background"] = code
            elif re.match(r'^\x1b\[(1|2|3|4|5|7|8|9)m$', code):
                if code not in active_codes["formatting"]:
                    active_codes["formatting"].append(code)

        for line in lines:
            if self.debug:
                print(f"\n+ line:\n{self.reveal(line)}{self.reset}")

            leading_match = re.match(r'^((?:\x1b\[[0-9;]*[a-zA-Z])*\s*)', line)
            leading_part = leading_match.group(0) if leading_match else ''
            rest_of_line = line[len(leading_part):].strip()

            leading_ansi_codes = ansi_regex.findall(leading_part)
            leading_spaces = ansi_regex.sub('', leading_part)

            for code in leading_ansi_codes:
                categorize_code(code)

            active_code_string = (
                active_codes["foreground"]
                + active_codes["background"]
                + ''.join(active_codes["formatting"])
            )

            reconstructed_leading = f"{self.reset}{leading_spaces}{active_code_string}"

            for code in ansi_regex.findall(rest_of_line):
                categorize_code(code)

            processed_line = f"{reconstructed_leading}{rest_of_line}{self.reset}{self.fg['reset']}{self.bg['reset']}"

            if self.debug:
                print(f"+ processedLine:\n{self.reveal(processed_line)}{self.reset}")

            processed_lines.append(processed_line)

        return '\n'.join(processed_lines)

    def get_contrast_name(self, input_, threshold=0.2):
        def parse_escape_sequence(seq):
            match = re.match(r'\x1b\[(\d+)m', seq)
            if match:
                code = int(match.group(1))
                if 30 <= code <= 37:
                    return code - 30
                elif 90 <= code <= 97:
                    return code - 90 + 8
            raise ValueError("Invalid ANSI escape sequence")

        def ansi_to_rgb(code):
            if code < 16:
                base = [
                    (0,0,0), (128,0,0), (0,128,0), (128,128,0),
                    (0,0,128), (128,0,128), (0,128,128), (192,192,192),
                    (128,128,128), (255,0,0), (0,255,0), (255,255,0),
                    (0,0,255), (255,0,255), (0,255,255), (255,255,255)
                ]
                return base[code]
            elif 16 <= code < 232:
                base = code - 16
                return (
                    (base // 36) * 51,
                    ((base % 36) // 6) * 51,
                    (base % 6) * 51
                )
            elif 232 <= code < 256:
                gray = (code - 232) * 10 + 8
                return (gray, gray, gray)
            raise ValueError("Invalid ANSI color code")

        def luminance(rgb):
            def f(c):
                c = c / 255
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            r, g, b = map(f, rgb)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        if isinstance(input_, str) and input_.startswith("\x1b["):
            code = parse_escape_sequence(input_)
        elif isinstance(input_, int):
            code = input_
        else:
            raise TypeError("Invalid input type")

        rgb = ansi_to_rgb(code)
        return "black" if luminance(rgb) > threshold else "white"

    def get_contrast_fg(self, code): return self.fg["white"] if self.get_contrast_name(code) == "white" else self.fg["black"]
    def get_contrast_bg(self, code): return self.bg["white"] if self.get_contrast_name(code) == "white" else self.bg["black"]

    def test_standard(self):
        print(f"{self.reset}=== Testing ANSI Codes ===")

        # Test Reset
        print(f"{self.reset}[Reset] This text should be in default style.")

        # Test Styles
        for name, code in self.style.items():
            if "reset" not in name:
                print(f"{code}[{name}] This text uses style '{name}'.{self.reset}")

        # Foreground Colors
        print("\n=== Foreground Colors ===")
        for color, code in self.fg.items():
            if isinstance(code, str):
                print(f"{code}[{color}] This is {color} text.{self.fg['reset']}")

        print("\n=== Bright Foreground Colors ===")
        for color, code in self.fg["bright"].items():
            print(f"{code}[Bright {color}] This is bright {color} text.{self.fg['reset']}")

        # Background Colors
        print("\n=== Background Colors ===")
        for color, code in self.bg.items():
            if isinstance(code, str):
                print(f"{code}[{color}] This is text with {color} background.{self.bg['reset']}")

        print("\n=== Bright Background Colors ===")
        for color, code in self.bg["bright"].items():
            print(f"{code}[Bright {color}] This is text with bright {color} background.{self.bg['reset']}")


    def test_color256(self):
        print("\n=== 256-Color Foreground ===")

        row_len_standard = 8
        row_len_216_step_rgb = 6
        row_len_grayscale = 12
        row_count_standard = 2
        row_count_216_step_rgb = 6 * 6
        index_count_standard = row_len_standard * row_count_standard
        index_count_216_step_rgb = row_len_216_step_rgb * row_count_216_step_rgb
        index_start_216_step_rgb = index_count_standard
        index_start_grayscale = index_count_standard + index_count_216_step_rgb

        def get_row_len(index):
            if index < index_start_216_step_rgb:
                return row_len_standard
            elif index < index_start_grayscale:
                return row_len_216_step_rgb
            else:
                return row_len_grayscale

        # Display 256-color foreground in 2D
        i = 0
        while i < 256:
            row = ""
            row_len = get_row_len(i)
            for j in range(row_len):
                color_index = i + j
                if color_index >= 256:
                    break
                row += f"{self.get_contrast_bg(color_index)}{self.color256['fg'](color_index)} {str(color_index).rjust(3)} "
            print(row + self.reset)
            i += row_len

        print("\n=== 256-Color Background ===")

        i = 0
        while i < 256:
            row = ""
            row_len = get_row_len(i)
            for j in range(row_len):
                color_index = i + j
                row += f"{self.get_contrast_fg(color_index)}{self.color256['bg'](color_index)} {str(color_index).rjust(3)} "
            print(row + self.reset)
            i += row_len

        # print("\n=== 256-Color Background Pixel Style ===")
        # (omitted on purpose just like the JS)

        print("\n=== 256-Color Gradient ===")
        print(f"\nCredit: F. Schröder ({self.fg['cyan'] + self.style['underline']}https://www.hackitu.de/termcolor256/{self.reset})")

        color_grids = [
            {
                "name": "Layer 1 (Outermost)",
                "grid": [
                    [16, 52, 88, 124, 160, 196, 203, 210, 217, 224, 231],
                    [16, 52, 88, 124, 160, 202, 209, 216, 223, 230, 231],
                    [16, 52, 88, 124, 166, 208, 215, 222, 229, 230, 231],
                    [16, 52, 88, 130, 172, 214, 221, 228, 229, 230, 231],
                    [16, 52, 94, 136, 178, 220, 227, 228, 229, 230, 231],
                    [16, 58, 100, 142, 184, 226, 227, 228, 229, 230, 231],
                    [16, 22, 64, 106, 148, 190, 227, 228, 229, 230, 231],
                    [16, 22, 28, 70, 112, 154, 191, 228, 229, 230, 231],
                    [16, 22, 28, 34, 76, 118, 155, 192, 229, 230, 231],
                    [16, 22, 28, 34, 40, 82, 119, 156, 193, 230, 231],
                    [16, 22, 28, 34, 40, 46, 83, 120, 157, 194, 231],
                    [16, 22, 28, 34, 40, 47, 84, 121, 158, 195, 231],
                    [16, 22, 28, 34, 41, 48, 85, 122, 159, 195, 231],
                    [16, 22, 28, 35, 42, 49, 86, 123, 159, 195, 231],
                    [16, 22, 29, 36, 43, 50, 87, 123, 159, 195, 231],
                    [16, 23, 30, 37, 44, 51, 87, 123, 159, 195, 231],
                    [16, 17, 24, 31, 38, 45, 87, 123, 159, 195, 231],
                    [16, 17, 18, 25, 32, 39, 81, 123, 159, 195, 231],
                    [16, 17, 18, 19, 26, 33, 75, 117, 159, 195, 231],
                    [16, 17, 18, 19, 20, 27, 69, 111, 153, 195, 231],
                    [16, 17, 18, 19, 20, 21, 63, 105, 147, 189, 231],
                    [16, 17, 18, 19, 20, 57, 99, 141, 183, 225, 231],
                    [16, 17, 18, 19, 56, 93, 135, 177, 219, 225, 231],
                    [16, 17, 18, 55, 92, 129, 171, 213, 219, 225, 231],
                    [16, 17, 54, 91, 128, 165, 207, 213, 219, 225, 231],
                    [16, 53, 90, 127, 164, 201, 207, 213, 219, 225, 231],
                    [16, 52, 89, 126, 163, 200, 207, 213, 219, 225, 231],
                    [16, 52, 88, 125, 162, 199, 206, 213, 219, 225, 231],
                    [16, 52, 88, 124, 161, 198, 205, 212, 219, 225, 231],
                    [16, 52, 88, 124, 160, 197, 204, 211, 218, 225, 231]
                ]
            },
            {
                "name": "Layer 2",
                "grid": [
                    [59, 95, 131, 167, 174, 181, 188],
                    [59, 95, 131, 173, 180, 187, 188],
                    [59, 95, 137, 179, 186, 187, 188],
                    [59, 101, 143, 185, 186, 187, 188],
                    [59, 65, 107, 149, 186, 187, 188],
                    [59, 65, 71, 113, 150, 187, 188],
                    [59, 65, 71, 77, 114, 151, 188],
                    [59, 65, 71, 78, 115, 152, 188],
                    [59, 65, 72, 79, 116, 152, 188],
                    [59, 66, 73, 80, 116, 152, 188],
                    [59, 60, 67, 74, 116, 152, 188],
                    [59, 60, 61, 68, 110, 152, 188],
                    [59, 60, 61, 62, 104, 146, 188],
                    [59, 60, 61, 98, 140, 182, 188],
                    [59, 60, 97, 134, 176, 182, 188],
                    [59, 96, 133, 170, 176, 182, 188],
                    [59, 95, 132, 169, 176, 182, 188],
                    [59, 95, 131, 168, 175, 182, 188]
                ]
            },
            {
                "name": "Layer 3 (Innermost)",
                "grid": [
                    [102, 138, 144, 108, 109, 103, 139, 145]
                ]
            },
        ]

        for layer in color_grids:
            name = layer.get("name", "")
            grid = layer.get("grid", [])
            print(f"\n{self.format(self.style['bold'], name)}:" if name else "")
            if isinstance(grid, list) and len(grid) > 0:
                for row_index, row in enumerate(grid):
                    if isinstance(row, list):
                        row_display = ""
                        for color_index in row:
                            if isinstance(color_index, int) and 0 <= color_index <= 255:
                                fg = self.get_contrast_fg(color_index)
                                bg = self.color256['bg'](color_index)
                                row_display += f"{fg}{bg} {str(color_index).rjust(3)} "
                            else:
                                row_display += f"{self.format(self.bc['fg']['red'], 'ERR')} ??? "
                        print(row_display + self.reset)
                    else:
                        print(f"Row {row_index + 1} is not a valid array")
            else:
                print(f'Grid "{name}" is empty or invalid.')



    def test_screen(self):
        import time, sys
        print(f"{self.reset}=== Testing Screen Controls ===")

        print("Clearing screen in 2 seconds...")
        time.sleep(2)
        print(self.screen["clear"])

        print("Filling lines then clearing from cursor to end...")
        for i in range(10):
            print(f"Line {i + 1}")
        time.sleep(2)
        sys.stdout.write(self.cursor["moveTo"](5, 5))
        print(self.screen["clearFromCursorToEnd"])

        print("Clearing from cursor to start...")
        time.sleep(2)
        sys.stdout.write(self.cursor["moveTo"](7, 20))
        print(self.screen["clearFromCursorToStart"])

        print("Clearing a line...")
        time.sleep(2)
        sys.stdout.write(self.cursor["moveTo"](9, 0))
        print(f"This line will be cleared shortly!{self.screen['clearLine']}")

        print("Clearing to end of line...")
        time.sleep(2)
        sys.stdout.write(self.cursor["moveTo"](10, 10))
        print(f"Partial clear{self.screen['clearLineToEnd']}")

        print("Clearing to start of line...")
        time.sleep(2)
        sys.stdout.write(self.cursor["moveTo"](11, 30))
        print(f"{self.screen['clearLineToStart']}Rest of line.")

        print("Cursor demo: saving/restoring...")
        time.sleep(1)
        sys.stdout.write(self.cursor["moveTo"](13, 10))
        print("Saving here...")
        sys.stdout.write(self.cursor["save"])
        time.sleep(1)
        sys.stdout.write(self.cursor["moveTo"](15, 5))
        print("Moved somewhere else")
        time.sleep(1)
        sys.stdout.write(self.cursor["restore"])
        print("Restored position.")


    def test_cursor(self):
        import time, sys
        print(f"{self.reset}=== Testing Cursor Controls ===")

        print("\nMoving the cursor up...")
        time.sleep(1)
        sys.stdout.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        sys.stdout.write(self.cursor )
        print("Cursor moved up 3 lines!")

        print("\nMoving the cursor down...")
        time.sleep(1)
        sys.stdout.write(self.cursor )
        print("Cursor moved down 2 lines!")

        print("\nMoving the cursor right...")
        time.sleep(1)
        sys.stdout.write(self.cursor )
        print("Cursor moved right!")

        print("\nMoving the cursor left...")
        time.sleep(1)
        sys.stdout.write(self.cursor )
        print("Cursor moved left!")

        print("\nMoving the cursor to row 10, col 20...")
        time.sleep(1)
        sys.stdout.write(self.cursor["moveTo"](10, 20))
        print("Cursor moved to 10,20!")

        print("\nHiding and then showing the cursor...")
        time.sleep(1)
        sys.stdout.write(self.cursor["hide"])
        print("Cursor is hidden.")
        time.sleep(1)
        sys.stdout.write(self.cursor["show"])
        print("Cursor is shown again!")


    def test_reveal(self):
        test_string = (
            f"{self.fg['red']}{self.style['underline']}This is red underlined text\n"
            f"    {self.fg['green']}{self.style['underline']}This is green underlined text\n"
            f"        This is green underlined text again plus {self.fg['red']}This is red underlined text{self.reset}        \n"
            "No ANSI codes here"
        )
        print(f"++ testString:\n{test_string}")
        print(f"++ ANSI.reveal(testString):\n{self.reveal(test_string)}")


    def test_clean(self):
        test_string = (
            f"{self.fg['red']}{self.style['underline']}This is red underlined text\n"
            f"    {self.fg['green']}{self.style['underline']}This is green underlined text\n"
            f"        This is green underlined text again plus {self.fg['red']}This is red underlined text{self.reset}        \n"
            "No ANSI codes here"
        )
        print(f"++ testString:\n{test_string}")
        print(f"++ [debug] ANSI.reveal(testString):\n{self.reveal(test_string)}")
        print(f"++ ANSI.clean(testString):\n{self.clean(test_string)}")


    def test_all(self):
        for name, test in self.test.items():
            if callable(test):
                response = input(f"Run test '{name}'? (y/n): ").strip().lower()
                if response == 'y':
                    print(f"\n--- Running test: {name} ---\n")
                    test()
                else:
                    print(f"Skipped test: {name}\n")


if __name__ == "__main__":
    ansi = ANSI()
    ansi.test_all()
