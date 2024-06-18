import re

# action.py
class Action:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def parse_output(self, output):
        devices = []
        current_device = None
        device_info = {}
        pci_lines = []

        lines = output.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith('Dev #'):
                if current_device:
                    self._finalize_device_info(device_info, pci_lines)
                    devices.append(device_info)
                    device_info = {}
                    pci_lines = []
                current_device = line
                device_info['Dev'] = current_device
            elif line:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key.startswith('0000'):
                        pci_lines.append(line)
                        if 'First_PCI' not in device_info:
                            device_info['First_PCI'] = value
                    else:
                        device_info[key] = value
                else:
                    pci_lines.append(line)

        if current_device:
            self._finalize_device_info(device_info, pci_lines)
            devices.append(device_info)

        return devices

    def _finalize_device_info(self, device_info, pci_lines):
        if pci_lines:
            device_info['PCI'] = '\n'.join(pci_lines)

    def parser(self, output):
        pattern = re.compile(r"Dev #(\d+)")
        matches = pattern.findall(output)
        return matches
