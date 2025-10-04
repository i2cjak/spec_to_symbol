from .sexp_parser import SexpAtom
import copy

class KiCadSymbol:
    def __init__(self, name, properties_sexp, pins, graphics, attributes, template_name=None):
        self.name = name
        self.properties = properties_sexp
        self.pins = pins
        self.attributes = attributes
        
        if template_name:
            self.graphics = self._rename_graphics(graphics, template_name, name)
        else:
            self.graphics = graphics

    def _rename_graphics(self, graphics_list, old_prefix, new_prefix):
        new_graphics_list = []
        for graphic_sexp in graphics_list:
            new_graphic = copy.deepcopy(graphic_sexp)
            old_name = str(new_graphic[1])
            new_name = old_name.replace(old_prefix, new_prefix, 1)
            new_graphic[1] = new_name
            new_graphics_list.append(new_graphic)
        return new_graphics_list

    @classmethod
    def from_sexp(cls, sexp):
        name = str(sexp[1])
        properties_sexp = {}
        pins = []
        graphics = []
        attributes = []
        
        for item in sexp[2:]:
            if not isinstance(item, list) or not item:
                continue
            
            item_type = str(item[0])
            if item_type == "property":
                properties_sexp[str(item[1])] = item
            elif item_type == "pin":
                pins.append(item)
            elif item_type == "symbol" and str(item[1]).startswith(name + "_"):
                graphics.append(item)
            else:
                attributes.append(item)

        return cls(name, properties_sexp, pins, graphics, attributes)

    def set_property(self, key, value):
        if key in self.properties:
            self.properties[key][2] = value
        else:
            new_prop = [
                SexpAtom("property"), key, value,
                [SexpAtom("at"), 0, 0, 0],
                [SexpAtom("effects"),
                    [SexpAtom("font"), [SexpAtom("size"), 1.27, 1.27]],
                ]
            ]
            self.properties[key] = new_prop

    def ensure_hidden_properties(self):
        for key, prop_sexp in self.properties.items():
            if key in ["Reference", "Value"]:
                continue

            effects_block = next((item for item in prop_sexp if isinstance(item, list) and item and item[0] == SexpAtom("effects")), None)
            if effects_block is None: continue

            is_hidden = any(isinstance(effect, list) and effect and effect[0] == SexpAtom("hide") for effect in effects_block)
            if not is_hidden:
                effects_block.append([SexpAtom("hide"), SexpAtom("yes")])

    def to_sexp(self):
        sexp = [SexpAtom("symbol"), self.name]
        sexp.extend(self.attributes)
        
        prop_order = ["Reference", "Value", "Footprint", "Datasheet", "Description"]
        sorted_props = sorted(self.properties.values(), key=lambda p: prop_order.index(p[1]) if p[1] in prop_order else 99)

        sexp.extend(sorted_props)
        sexp.extend(self.graphics)
        sexp.extend(self.pins)
        return sexp
