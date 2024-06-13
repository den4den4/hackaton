class Firmware:
    def __init__(self, connection_manager):
        """
        Initialize the Firmware class with a connection manager.

        Args:
            connection_manager (ConnectionManager): The connection manager instance.
        """
        self.connection_manager = connection_manager

    def get_fw_code(self, desc):
        """
        Get the firmware code based on the device description.

        Args:
            desc (str): The description of the device.

        Returns:
            str: The firmware code if found, otherwise None.
        """
        fw_code_map = {
            'Bluefield-3': '41692',
            'Bluefield-2': '41686',
            'ConnextX-7': '4129',
            'ConnextX-6 Lx': '4127',
            'ConnextX-6 Dx': '4125'
        }
        for key in fw_code_map:
            if key in desc:
                return fw_code_map[key]
        return None

    def install(self, device, version, ssh):
        """
        Install the firmware for the given device and version.

        Args:
            device (dict): The device information dictionary.
            version (str): The version of the firmware.
            ssh (paramiko.SSHClient): The SSH client for the connection.

        Returns:
            str: The output of the installation command.
        """
        fw_code = self.get_fw_code(device.get('Desc', ''))
        if not fw_code:
            return f"Unknown device description: {device.get('Desc', '')}"

        # Format version by replacing dots with underscores
        version_formatted = version.replace('.', '_')
        first_pci = device.get('First_PCI', 'Unknown PCI')

        # Command to execute on the remote machine to install firmware
        command = (
            f"mlxburn -d {first_pci} "
            f"-img_dir /mswg/release/host_fw/fw-{fw_code}/fw-{fw_code}-rel-{version_formatted}-build-001/etc/bin/"
        )

        # Execute the command on the remote machine
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
        return output
