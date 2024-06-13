class Action:
    def __init__(self):
        pass

    def parser(self, output):
        import re
        pattern = re.compile(r"Dev #(\d+)")
        matches = pattern.findall(output)
        return matches

    def parse_output(self, output):
        devices = []
        device_info = {}
        current_device = None
        pci_lines = []

        lines = output.splitlines()
        for line in lines:
            if line.startswith('Dev #'):
                if current_device:
                    if pci_lines:
                        device_info['PCI'] = '\n'.join(pci_lines)
                    devices.append(device_info)
                    device_info = {}
                    pci_lines = []
                current_device = line.strip()
                device_info['Dev'] = current_device
            elif line.strip():
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = [part.strip() for part in parts]
                    if key.startswith('0000'):
                        pci_lines.append(line.strip())
                        # Add first PCI address
                        if 'First_PCI' not in device_info:
                            device_info['First_PCI'] = value.strip()  # Use 'value' instead of 'key.strip()'
                    else:
                        device_info[key] = value
                else:
                    pci_lines.append(line.strip())
        if current_device:
            if pci_lines:
                device_info['PCI'] = '\n'.join(pci_lines)
            devices.append(device_info)

        return devices



