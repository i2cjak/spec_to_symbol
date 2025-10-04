from spec_to_symbol.tui.terminal import Terminal
from spec_to_symbol.component import COMPONENT_MAP
from spec_to_symbol.fuzzy import footprint_finder
from spec_to_symbol.library_manager import LibraryManager
from spec_to_symbol.kicad_symbol import KiCadSymbol
from spec_to_symbol.logger import logger
import copy
import os

class SpecToSymbolTUI:
    def __init__(self):
        self.active = True
        self.mode = "nav_tabs"
        self.template_library = LibraryManager("symbol_templates/Device.kicad_sym")
        self.component_types = [name for name in COMPONENT_MAP.keys() if name in self.template_library.symbols]
        self.tab_selection = 0
        self.form_selection = 0
        self.form_data = {}
        self.dirty_fields = set() # Track modified fields
        self.completions = []
        self.completion_selection = -1
        self.dialog_message = None
        self.last_key = ""
        self.just_entered_insert = False
        self.setup_form()

    def setup_form(self):
        self.form_selection = 0
        self.completion_selection = -1
        self.completions = []
        self.dirty_fields = set()
        template_name = self.component_types[self.tab_selection]
        _, form_fields_config = COMPONENT_MAP[template_name]
        
        self.form_fields = ["mpn", "package", "lcsc"] + form_fields_config
        self.form_data = {
            "mpn": "PART-NUMBER", "package": "Footprint:Name", "lcsc": "",
            "value": "100k", "tolerance": "5", "power": "0.1",
            "voltage": "50V", "dielectric": "X7R", "current": "100mA",
            "color": "Red", "impedance": "120-ohm @ 100MHz"
        }

    def handle_key(self, key):
        logger.debug(f"Key: {key!r}, Mode: {self.mode}")
        if self.dialog_message:
            self.dialog_message = None
            return

        if key == 'q' and self.mode != "insert":
            self.active = False
            return

        if self.mode == "nav_tabs":
            if key == 'l': self.tab_selection = (self.tab_selection + 1) % len(self.component_types)
            elif key == 'h': self.tab_selection = (self.tab_selection - 1 + len(self.component_types)) % len(self.component_types)
            elif key == 'j' or key == '\r' or key == '\t':
                self.setup_form()
                self.mode = "nav_form"
        
        elif self.mode == "nav_form":
            if key == 'k' and self.form_selection == 0: self.mode = "nav_tabs"
            elif key == 'j': self.form_selection = (self.form_selection + 1) % (len(self.form_fields) + 1)
            elif key == 'k': self.form_selection = (self.form_selection - 1 + len(self.form_fields) + 1) % (len(self.form_fields) + 1)
            elif key == 'g' and self.last_key == 'g': self.form_selection = 0
            elif key == 'G': self.form_selection = len(self.form_fields)
            elif key == 'd' and self.last_key == 'd':
                if self.form_selection < len(self.form_fields):
                    field_name = self.form_fields[self.form_selection]
                    self.form_data[field_name] = ""
                    self.dirty_fields.add(field_name)
            elif (key == 'i' or key == 'a') and self.form_selection < len(self.form_fields):
                self.mode = "insert"
                self.completion_selection = -1
                self.just_entered_insert = True
            elif key == '\r' and self.form_selection == len(self.form_fields):
                self.submit_form()

        elif self.mode == "insert":
            field_name = self.form_fields[self.form_selection]
            if key == '\x1b': self.mode = "nav_form"; self.completions = []
            elif key == '\r':
                if self.completion_selection != -1: self.form_data[field_name] = self.completions[self.completion_selection]
                self.mode = "nav_form"; self.completions = []
            elif key == '\x7f': 
                if self.form_data[field_name]: self.form_data[field_name] = self.form_data[field_name][:-1]
            elif key == '\t':
                if self.completions: self.completion_selection = (self.completion_selection + 1) % len(self.completions)
            elif key.isprintable():
                if self.just_entered_insert and field_name not in self.dirty_fields:
                    self.form_data[field_name] = ""
                self.just_entered_insert = False
                self.form_data[field_name] += key
                self.dirty_fields.add(field_name)
                if field_name == "package" and len(self.form_data[field_name]) > 1:
                    self.completions = footprint_finder.find(self.form_data[field_name])
                else: self.completions = []
        
        self.last_key = key

    def submit_form(self):
        logger.info(f"Submit action triggered. Form data: {self.form_data}")
        try:
            template_name = self.component_types[self.tab_selection]
            component_class, field_keys = COMPONENT_MAP[template_name]
            
            kwargs = {key: self.form_data[key] for key in field_keys}
            kwargs['mpn'] = self.form_data['mpn']
            kwargs['package'] = self.form_data['package']
            kwargs['lcsc'] = self.form_data.get('lcsc') or None

            component = component_class(**kwargs)
            message = self.create_symbol(component)
            self.dialog_message = ("Success", message)
            logger.info(f"Symbol creation successful: {message}")
        except Exception as e:
            self.dialog_message = ("Error", str(e))
            logger.error(f"Symbol creation failed: {e}", exc_info=True)
        self.mode = "nav_tabs"

    def create_symbol(self, component, library_path="libraries/Passives.kicad_sym"):
        template_symbol = self.template_library.symbols[component.template_name]
        new_symbol = KiCadSymbol(
            component.mpn, copy.deepcopy(template_symbol.properties), template_symbol.pins,
            template_symbol.graphics, template_symbol.attributes, template_name=template_symbol.name
        )
        for key, value in component.get_properties().items():
            new_symbol.set_property(key, value)
        new_symbol.ensure_hidden_properties()
        library = LibraryManager(library_path)
        library.add_symbol(new_symbol)
        library.save_library()
        return f"Symbol {component.mpn} added to {library_path}"

    def draw(self, term: Terminal):
        term.hide_cursor(); term.clear_screen(); rows, cols = term.get_size()
        
        term.move_cursor(1, 1); term.set_color(fg=255, bg=57); term.write(" spec-to-symbol ".center(cols, "─")); term.reset_color()

        tab_row = 3; current_col = 2
        for i, name in enumerate(self.component_types):
            is_selected = i == self.tab_selection
            label = f" {name.replace('_Small', '').replace('_US','')} "
            term.move_cursor(tab_row, current_col)
            if is_selected and self.mode == "nav_tabs": term.set_color(fg=255, bg=27)
            else: term.set_color(fg=248, bg=236)
            term.write(label)
            current_col += len(label)
        
        form_start_row = 5; form_start_col = 4
        term.move_cursor(form_start_row, form_start_col - 1); term.set_color(fg=240); term.write("┌" + "─" * 40 + "┐"); term.reset_color()
        for i, field in enumerate(self.form_fields):
            row = form_start_row + i + 1
            term.move_cursor(row, form_start_col - 1); term.set_color(fg=240); term.write("│"); term.reset_color()
            is_focused = i == self.form_selection
            if is_focused and self.mode == "nav_form": term.set_color(bg=235)
            term.write(f" {field.title()}: ".ljust(14))
            term.reset_color()
            
            # Draw placeholder text in gray
            if field not in self.dirty_fields:
                term.set_color(fg=244)
            term.write(f" {self.form_data.get(field, '')}")
            term.reset_color()

            term.move_cursor(row, form_start_col + 40); term.set_color(fg=240); term.write("│"); term.reset_color()
        
        submit_row = form_start_row + len(self.form_fields) + 1
        term.move_cursor(submit_row, form_start_col - 1); term.set_color(fg=240); term.write("│"); term.reset_color()
        if self.form_selection == len(self.form_fields): term.set_color(bg=27)
        term.write(" " * 14 + "[ Submit ]".center(12))
        term.reset_color()
        term.move_cursor(submit_row, form_start_col + 40); term.set_color(fg=240); term.write("│"); term.reset_color()
        term.move_cursor(submit_row + 1, form_start_col - 1); term.set_color(fg=240); term.write("└" + "─" * 40 + "┘"); term.reset_color()

        if self.mode == "insert" and self.completions:
            comp_row = form_start_row + self.form_selection + 2
            for i, item in enumerate(self.completions[:rows - comp_row - 2]):
                term.move_cursor(comp_row + i, form_start_col + 15)
                if i == self.completion_selection: term.set_color(bg=238)
                term.write(item.ljust(25)); term.reset_color()
        if self.dialog_message:
            title, message = self.dialog_message; box_width = max(len(title), len(message)) + 6; box_height = 5
            start_row = rows // 2 - box_height // 2; start_col = cols // 2 - box_width // 2
            term.set_color(bg=27, fg=255)
            for r in range(box_height): term.move_cursor(start_row + r, start_col); term.write(" " * box_width)
            term.move_cursor(start_row + 1, start_col + (box_width - len(title)) // 2); term.write(title)
            term.move_cursor(start_row + 3, start_col + (box_width - len(message)) // 2); term.write(message)
        footer_text = "[h/l] Tabs | [j/k] Form | [i] Insert | [dd] Clear | [enter] Select/Submit | [q] Quit"
        term.move_cursor(rows, 1); term.set_color(fg=255, bg=57); term.write(footer_text.ljust(cols)); term.reset_color()
        if self.mode == "insert":
            cursor_row = form_start_row + self.form_selection + 1
            cursor_col = form_start_col + 15 + len(self.form_data.get(self.form_fields[self.form_selection], ''))
            term.move_cursor(cursor_row, cursor_col); term.show_cursor()

    def run(self):
        with Terminal() as term:
            while self.active:
                self.draw(term)
                key = term.get_key()
                self.handle_key(key)

def run_tui():
    if not os.path.exists(footprint_finder.cache_path):
        print("First-time setup: Caching KiCad footprints for faster searching...")
    footprint_finder.scan()
    SpecToSymbolTUI().run()