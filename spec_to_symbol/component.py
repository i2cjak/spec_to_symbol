from abc import ABC, abstractmethod

class Component(ABC):
    def __init__(self, mpn, package, lcsc=None):
        self.mpn = mpn
        self.package = package
        self.lcsc = lcsc

    @property
    @abstractmethod
    def template_name(self):
        pass

    def get_base_properties(self):
        keywords = f"{self.mpn} {self.lcsc or ''}".strip()
        properties = { "Footprint": self.package, "MPN": self.mpn }
        if self.lcsc:
            properties["LCSC"] = self.lcsc
        return properties, keywords

class Resistor(Component):
    template_name = "R_Small_US"
    def __init__(self, value, tolerance, power, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.tolerance = tolerance
        self.power = power

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Power"] = f"{self.power}W"
        props["Tolerance"] = f"{self.tolerance}%"
        props["Description"] = f"Resistor {self.value} {self.tolerance}% {self.power}W, {self.package}"
        props["ki_keywords"] = f"R resistor {self.value} {keywords}"
        return props

class Capacitor(Component):
    template_name = "C_Small"
    def __init__(self, value, voltage, dielectric, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.voltage = voltage
        self.dielectric = dielectric

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Voltage"] = self.voltage
        props["Dielectric"] = self.dielectric
        props["Description"] = f"{self.dielectric} Capacitor {self.value} {self.voltage}, {self.package}"
        props["ki_keywords"] = f"C capacitor {self.value} {keywords}"
        return props

class Inductor(Component):
    template_name = "L_Small"
    def __init__(self, value, current, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.current = current

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Current"] = self.current
        props["Description"] = f"Inductor {self.value} {self.current}, {self.package}"
        props["ki_keywords"] = f"L inductor {self.value} {keywords}"
        return props

class Diode(Component):
    template_name = "D_Small"
    def __init__(self, value="Diode", **kwargs):
        super().__init__(**kwargs)
        self.value = value
    
    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Description"] = f"Diode, {self.package}"
        props["ki_keywords"] = f"diode {keywords}"
        return props

class LED(Component):
    template_name = "LED_Small"
    def __init__(self, value="LED", color="Red", **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.color = color

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Color"] = self.color
        props["Description"] = f"{self.color} LED, {self.package}"
        props["ki_keywords"] = f"LED diode {self.color} {keywords}"
        return props

class ZenerDiode(Component):
    template_name = "D_Zener_Small"
    def __init__(self, value="Zener", voltage="5.1V", **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.voltage = voltage

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Voltage"] = self.voltage
        props["Description"] = f"Zener Diode {self.voltage}, {self.package}"
        props["ki_keywords"] = f"zener diode {self.voltage} {keywords}"
        return props

class SchottkyDiode(Component):
    template_name = "D_Schottky_Small"
    def __init__(self, value="Schottky", voltage="40V", **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.voltage = voltage

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Voltage"] = self.voltage
        props["Description"] = f"Schottky Diode {self.voltage}, {self.package}"
        props["ki_keywords"] = f"schottky diode {self.voltage} {keywords}"
        return props

class Polyfuse(Component):
    template_name = "Polyfuse_Small"
    def __init__(self, value="Polyfuse", current="100mA", **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.current = current

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Current"] = self.current
        props["Description"] = f"Polyfuse {self.current}, {self.package}"
        props["ki_keywords"] = f"polyfuse fuse ptc {keywords}"
        return props

class FerriteBead(Component):
    template_name = "FerriteBead_Small"
    def __init__(self, value="Ferrite Bead", impedance="120-ohm @ 100MHz", **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.impedance = impedance

    def get_properties(self):
        props, keywords = self.get_base_properties()
        props["Value"] = self.value
        props["Impedance"] = self.impedance
        props["Description"] = f"Ferrite Bead {self.impedance}, {self.package}"
        props["ki_keywords"] = f"ferrite bead inductor {keywords}"
        return props

# Mapping from template name to class and its form fields
COMPONENT_MAP = {
    "R_Small_US": (Resistor, ["value", "tolerance", "power"]),
    "C_Small": (Capacitor, ["value", "voltage", "dielectric"]),
    "L_Small": (Inductor, ["value", "current"]),
    "D_Small": (Diode, ["value"]),
    "LED_Small": (LED, ["value", "color"]),
    "D_Zener_Small": (ZenerDiode, ["value", "voltage"]),
    "D_Schottky_Small": (SchottkyDiode, ["value", "voltage"]),
    "Polyfuse_Small": (Polyfuse, ["value", "current"]),
    "FerriteBead_Small": (FerriteBead, ["value", "impedance"]),
}