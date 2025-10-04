import sys
import tty
import termios
import os
import select

class Terminal:
    """A class to handle raw terminal I/O and ANSI escape codes."""
    def __init__(self):
        self._original_settings = None

    def __enter__(self):
        self._original_settings = termios.tcgetattr(sys.stdin)
        self.write("\x1b[?1049h")  # Switch to alternate screen buffer
        self.clear_screen()
        tty.setraw(sys.stdin.fileno())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write("\x1b[?1049l")  # Switch back to main screen buffer
        self.show_cursor()
        self.reset_color()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._original_settings)

    def write(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def get_key(self):
        """
        Reads a key press. Handles multi-byte escape sequences for arrow keys etc.
        Returns a single character or a sequence like '\x1b[A'.
        """
        char = sys.stdin.read(1)
        if char != '\x1b':
            return char

        # If it's an escape, check for more chars with a tiny timeout
        # This prevents blocking if the user just pressed the Esc key.
        remaining_seq = ""
        if select.select([sys.stdin], [], [], 0.01)[0]:
            remaining_seq += sys.stdin.read(1)
            if remaining_seq == '[':
                 if select.select([sys.stdin], [], [], 0.01)[0]:
                    remaining_seq += sys.stdin.read(1)
        
        return char + remaining_seq

    def clear_screen(self):
        self.write("\x1b[2J")

    def move_cursor(self, row, col):
        self.write(f"\x1b[{row};{col}H")

    def hide_cursor(self):
        self.write("\x1b[?25l")

    def show_cursor(self):
        self.write("\x1b[?25h")

    def set_color(self, fg=None, bg=None):
        codes = []
        if fg: codes.append(f"38;5;{fg}")
        if bg: codes.append(f"48;5;{bg}")
        self.write(f"\x1b[{';'.join(codes)}m")

    def reset_color(self):
        self.write("\x1b[0m")

    def get_size(self):
        return os.get_terminal_size()