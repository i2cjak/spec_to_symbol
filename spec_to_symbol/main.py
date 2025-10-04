import argparse
import sys
import os
import copy

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from spec_to_symbol.library_manager import LibraryManager
from spec_to_symbol.component import COMPONENT_MAP
from spec_to_symbol.kicad_symbol import KiCadSymbol
from spec_to_symbol.fuzzy import footprint_finder
from spec_to_symbol.tui.tui import run_tui

def main():
    parser = argparse.ArgumentParser(description="Create KiCad symbols for passive components.")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode.")
    parser.add_argument("component_type", nargs="?", choices=COMPONENT_MAP.keys(), help="Type of component template to use.")
    # Generic arguments
    parser.add_argument("--mpn", help="Manufacturer Part Number.")
    parser.add_argument("--package", help="Component package/footprint.")
    parser.add_argument("--value", help="Component value (e.g., 10k, 100uF).")
    parser.add_argument("--lcsc", help="LCSC Part Number.")
    # Specific arguments
    parser.add_argument("--tolerance", type=float, help="Resistor tolerance in percent.")
    parser.add_argument("--power", type=float, help="Resistor power in watts.")
    parser.add_argument("--voltage", type=str, help="Capacitor/Diode voltage.")
    parser.add_argument("--dielectric", default="X7R", help="Capacitor dielectric material.")
    parser.add_argument("--current", type=str, help="Inductor/Fuse current.")
    parser.add_argument("--color", type=str, help="LED color.")
    parser.add_argument("--impedance", type=str, help="Ferrite Bead impedance.")
    # Config
    parser.add_argument("--footprint-dir", default="/usr/share/kicad/footprints", help="KiCad footprint directory.")
    parser.add_argument("--library", default="libraries/Passives.kicad_sym", help="Output symbol library.")
    parser.add_argument("--template-library", default="symbol_templates/Device.kicad_sym", help="Template symbol library.")

    args = parser.parse_args()

    if args.cli:
        if not all([args.component_type, args.mpn]):
            parser.error("component_type and mpn are required in CLI mode.")
        
        footprint_finder.footprint_dir = args.footprint_dir
        footprint_finder.scan()

        component_class, field_keys = COMPONENT_MAP[args.component_type]
        kwargs = {key: getattr(args, key) for key in field_keys if hasattr(args, key)}
        kwargs['mpn'] = args.mpn
        kwargs['package'] = args.package
        kwargs['lcsc'] = args.lcsc
        
        component = component_class(**kwargs)

        template_library = LibraryManager(args.template_library)
        template_symbol = template_library.symbols[component.template_name]

        new_symbol = KiCadSymbol(
            component.mpn, copy.deepcopy(template_symbol.properties), template_symbol.pins,
            template_symbol.graphics, template_symbol.attributes, template_name=template_symbol.name
        )

        for key, value in component.get_properties().items():
            new_symbol.set_property(key, value)
        new_symbol.ensure_hidden_properties()

        library = LibraryManager(args.library)
        library.add_symbol(new_symbol)
        library.save_library()

        print(f"Symbol {new_symbol.name} added to {args.library}")
    else:
        run_tui()

if __name__ == "__main__":
    main()
