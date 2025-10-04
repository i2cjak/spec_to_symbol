from spec_to_symbol.kicad_symbol import KiCadSymbol
from spec_to_symbol.sexp_parser import parse_sexp, build_sexp, SexpAtom
import os

class LibraryManager:
    def __init__(self, library_path):
        self.library_path = library_path
        self.symbols = self._load_library()

    def _load_library(self):
        symbols = {}
        if not os.path.exists(self.library_path):
            return symbols
        
        with open(self.library_path, "r") as f:
            content = f.read()
        
        sexp = parse_sexp(content)
        for item in sexp:
            if isinstance(item, list) and item[0] == SexpAtom("symbol"):
                symbol = KiCadSymbol.from_sexp(item)
                symbols[symbol.name] = symbol
        return symbols

    def save_library(self):
        """
        Saves the library to a file with proper KiCad formatting and indentation.
        """
        # Build the entire library as a nested list, using SexpAtom for keywords.
        lib_sexp = [
            SexpAtom('kicad_symbol_lib'),
            [SexpAtom('version'), SexpAtom('20211014')],
            [SexpAtom('generator'), 'spec-to-symbol']
        ]
        
        # Add sorted symbols to the library structure
        sorted_symbols = sorted(self.symbols.values(), key=lambda s: s.name)
        for symbol in sorted_symbols:
            lib_sexp.append(symbol.to_sexp())

        # Build the final string from the nested list
        output = build_sexp(lib_sexp)

        # Ensure the output directory exists.
        lib_dir = os.path.dirname(self.library_path)
        if lib_dir:
            os.makedirs(lib_dir, exist_ok=True)

        with open(self.library_path, "w") as f:
            f.write(output)

    def add_symbol(self, symbol):
        self.symbols[symbol.name] = symbol
