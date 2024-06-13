import re
import subprocess
import sys
import time
from tkinter import messagebox


class ConnectionManager:
    def __init__(self):
        self.install_paramiko_if_needed()
        import paramiko
        self.paramiko = paramiko

    def install_paramiko_if_needed(self):
        try:
            import paramiko
        except ImportError:
            self.install_paramiko()

    def install_paramiko(self):
        try:
            # Upgrade pip first
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            # Install required packages for cryptography
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "setuptools-rust", "wheel"])
            # Install paramiko
            subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Installation Error", f"Failed to install paramiko: {e}")
            sys.exit(1)

    def is_valid_ip(self, value):
        ip_pattern = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        return ip_pattern.match(value) is not None

    def is_valid_hostname(self, value):
        if len(value) > 255:
            return False
        hostname_pattern = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
        return all(hostname_pattern.match(part) for part in value.split("."))

    def is_valid_hostname_or_ip(self, value):
        return self.is_valid_ip(value) or self.is_valid_hostname(value)

    def ssh_connect(self, server_name, username, password):
        try:
            ssh = self.paramiko.SSHClient()
            ssh.set_missing_host_key_policy(self.paramiko.AutoAddPolicy())
            ssh.connect(server_name, username=username, password=password)
            return ssh  # Return the SSH client object on successful connection
        except self.paramiko.AuthenticationException:
            messagebox.showerror("Authentication Error", "Authentication failed, please verify your credentials.")
        except self.paramiko.SSHException as sshException:
            messagebox.showerror("SSH Error", f"Unable to establish SSH connection: {sshException}")
        except self.paramiko.BadHostKeyException as badHostKeyException:
            messagebox.showerror("SSH Error", f"Unable to verify server's host key: {badHostKeyException}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Operation error: {e}")
        return None  # Return None on failure

    def install_and_run_lhca(self, ssh):
        try:
            # Check if lshca is already installed
            stdin, stdout, stderr = ssh.exec_command("pip3 show lshca")
            stdout.channel.recv_exit_status()  # Wait for the command to complete
            check_output = stdout.read().decode('utf-8')

            if "Name: lshca" not in check_output:
                # lshca is not installed, so install it
                stdin, stdout, stderr = ssh.exec_command("pip3 install lshca")
                stdout.channel.recv_exit_status()  # Wait for the command to complete
                install_output = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
            else:
                install_output = "lshca is already installed."

            # Run the lshca command
            stdin, stdout, stderr = ssh.exec_command("lshca")
            stdout.channel.recv_exit_status()  # Wait for the command to complete
            lhca_output = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')

            return install_output + "\n\n" + lhca_output
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to execute commands: {e}")
            return None
