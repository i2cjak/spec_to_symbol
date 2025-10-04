# spec-to-symbol

A fast, keyboard-driven TUI for generating KiCad symbols from component specifications without leaving the terminal.

## Purpose

This tool is designed for electronics engineers and hobbyists who want to quickly create standardized KiCad symbol library parts for common components (resistors, capacitors, diodes, etc.). It streamlines the process by using pre-defined templates, automatically searching for footprints, and providing a fast, mouse-free interface, allowing you to build your component library without getting sidetracked from your design work.

## Features

- **Vim-like Interface:** Navigate entirely with keyboard commands (`j/k/h/l`, `gg`/`G`, `dd`, etc.).
- **Performant TUI:** Built from scratch in Python with no external TUI libraries for maximum speed and responsiveness.
- **Template-Based:** Dynamically generates forms based on the component templates found in the `symbol_templates/` directory.
- **Fuzzy Footprint Search:** Live fuzzy-finding for KiCad footprints as you type in the "Package" field.
- **Instant Startup:** Footprint libraries are scanned once and then cached, making subsequent launches of the application nearly instantaneous.
- **Valid KiCad Output:** Generates correctly formatted and indented `.kicad_sym` files that are fully compatible with KiCad's symbol editor.

## Getting Started

### Prerequisites

- Python 3.8+
- A local installation of KiCad with standard footprint libraries (for footprint searching).

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd spec-to-symbol
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt 
    # (Or pip install rapidfuzz if there is no requirements file)
    ```

4.  **Run the application:**
    ```bash
    python spec_to_symbol/main.py
    ```

The application will start, and any symbols you create will be saved to `libraries/Passives.kicad_sym`.

## Keybindings

The interface is designed to be used entirely with the keyboard.

| Mode              | Key(s)              | Action                                      |
| ----------------- | ------------------- | ------------------------------------------- |
| **Global (Nav)**  | `q`                 | Quit the application.                       |
| **Tabs**          | `h` / `l`           | Navigate between component tabs.            |
|                   | `j` / `enter` / `tab` | Move down to the form for the selected tab. |
| **Form**          | `j` / `k`           | Navigate up/down between fields.            |
|                   | `k` (on first field) | Move focus back up to the tabs.             |
|                   | `gg` / `G`          | Jump to the top/bottom of the form.         |
|                   | `dd`                | Clear the contents of the highlighted field.|
|                   | `i` / `a`           | Enter **Insert Mode** to edit a field.      |
|                   | `enter` (on Submit) | Create the symbol.                          |
| **Insert Mode**   | `(any printable)`   | Type to enter text.                         |
|                   | `esc`               | Exit **Insert Mode** and return to Form Nav.|
|                   | `tab`               | Cycle through footprint completions.        |
|                   | `enter`             | Confirm a completion and exit Insert Mode.  |

## Configuration

- **Symbol Templates:** Place your base KiCad symbol files (e.g., `Device.kicad_sym`) in the `symbol_templates/` directory. The application will automatically parse this file to create the component tabs and forms.
- **Output Library:** Generated symbols are saved to `libraries/Passives.kicad_sym` by default. This can be changed with the `--library` command-line argument.
- **Footprint Path:** The application defaults to searching for footprints in `/usr/share/kicad/footprints`. You can specify a different path with the `--footprint-dir` argument.