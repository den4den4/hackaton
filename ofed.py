class OFED:
    def __init__(self, connection_manager):
        """
        Initialize the OFED class with a connection manager.

        Args:
            connection_manager (ConnectionManager): The connection manager instance.
        """
        self.connection_manager = connection_manager

    def install(self, version, ssh):
        """
        Install OFED for the given device and version.

        Args:
            device (dict): The device information dictionary.
            version (str): The version of the OFED.
            ssh (paramiko.SSHClient): The SSH client for the connection.

        Returns:
            str: The output of the installation command.
        """
        # Command to execute on the remote machine to install OFED
        command = (
            f"build=MLNX_OFED_LINUX-{version} /.autodirect/mswg/release/MLNX_OFED/mlnx_ofed_install --ovs-dpdk --bluefield --without-fw-update --add-kernel-support"
        )

        # Execute the command on the remote machine
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
        return output
