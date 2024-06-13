class DOCA:
    def __init__(self, connection_manager):
        """
        Initialize the DOCA class with a connection manager.

        Args:
            connection_manager (ConnectionManager): The connection manager instance.
        """
        self.connection_manager = connection_manager

    def install(self, device, version, ssh):
        """
        Install DOCA for the given device and version.

        Args:
            device (dict): The device information dictionary.
            version (str): The version of the DOCA.
            ssh (paramiko.SSHClient): The SSH client for the connection.

        Returns:
            str: The output of the installation command.
        """
        first_pci = device.get('First_PCI', 'Unknown PCI')

        # Command to execute on the remote machine to install DOCA
        command = (
            f"docainstall --prefix /mswg/release/doca/doca-{version}/"
        )

        # Execute the command on the remote machine
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
        return output
