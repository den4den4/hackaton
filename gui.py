
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from action import Action


class GUI:
    def __init__(self, root, connection_manager, action):
        """
        Initialize the GUI with the given root window, connection manager, and action.

        Args:
            root (tk.Tk): The root window of the GUI.
            connection_manager: The connection manager instance for handling server connections.
            action: The action instance for handling actions related to device management.
        """
        self.root = root
        self.connection_manager = connection_manager
        self.action = action
        self.devices = []  # Store devices to use in dropdown lists
        self.setup_ui()

    def setup_ui(self):
        """
        Setup the main UI elements.
        """
        self.root.title("Card Configurator")
        self.center_window(self.root)

        # Request Server Machine Name button
        self.request_button = tk.Button(self.root, text="Request Server Machine Name",
                                        command=self.show_server_name_input)
        self.request_button.pack(pady=10)

        # Close Application button
        self.close_button = tk.Button(self.root, text="Close Application", command=self.close_application)
        self.close_button.pack(pady=10)

    def show_server_name_input(self):
        """
        Display the input field for entering the server machine name or IP address.
        """
        self.request_button.pack_forget()
        self.close_button.pack_forget()

        # Label for entering server machine name or IP address
        self.message_label = tk.Label(self.root, text="Please enter the server machine name or IP address:")
        self.message_label.pack(pady=10)

        # Entry field for server machine name or IP address
        self.server_entry = tk.Entry(self.root)
        self.server_entry.pack(pady=5)

        # Submit button to submit server machine name or IP address
        self.submit_button = tk.Button(self.root, text="Submit", command=self.request_machine_ip)
        self.submit_button.pack(pady=10)

        # Bind Enter key to the submit button
        self.bind_enter_key()

    def bind_enter_key(self):
        """
        Bind the Enter key to the Submit button.
        """
        self.server_entry.bind("<Return>", lambda event: self.submit_button.invoke())

    def request_machine_ip(self):
        """
        Handle the submission of the server machine name or IP address.
        """
        server_name = self.server_entry.get()
        if server_name:
            if self.connection_manager.is_valid_hostname_or_ip(server_name):
                self.message_label.pack_forget()
                self.server_entry.pack_forget()
                self.submit_button.pack_forget()

                # Prompt for username
                username = simpledialog.askstring("Input", "Please enter your username:")
                if username:
                    # Prompt for password
                    password = simpledialog.askstring("Input", "Please enter your password:", show='*')
                    if password:
                        # Attempt SSH connection
                        ssh = self.connection_manager.ssh_connect(server_name, username, password)
                        if ssh:
                            self.show_message(f"Connected successfully to {server_name}")

                            # Install lhca and run the command
                            output = self.connection_manager.install_and_run_lhca(ssh)
                            if output is not None:
                                self.display_output(output)  # Display the output in the main window
                                self.create_device_buttons(output)  # Create device buttons

                            ssh.close()
                        else:
                            self.show_message(f"Failed to connect to {server_name}")
                        self.show_main_window()
                    else:
                        self.show_message("No password entered.")
                        self.show_main_window()
                else:
                    self.show_message("No username entered.")
                    self.show_main_window()
            else:
                self.show_message("The server machine name or IP address is invalid.")
                self.show_main_window()
        else:
            self.show_message("No server machine name entered.")
            self.show_main_window()

    def display_output(self, output):
        """
        Display the output from the server in the main window.

        Args:
            output (str): The output to be displayed.
        """
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Text widget to display output
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD)
        self.output_text.pack(side=tk.LEFT, expand=True, fill='both')

        # Scrollbar for the text widget
        self.scrollbar = tk.Scrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')

        self.output_text.config(yscrollcommand=self.scrollbar.set)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)

    def create_device_buttons(self, output):
        """
        Parse the output and create buttons for each device.

        Args:
            output (str): The output containing device information.
        """
        self.devices = self.action.parse_output(output)  # Store devices for later use
        for device in self.devices:
            desc = device.get('Desc', 'Unknown Desc')
            if desc == 'Mellanox Technologies Device':
                desc = 'Mellanox Technologies Device [Bluefield-3]'
            pn = device.get('PN', 'Unknown PN')
            fw = device.get('FW', 'Unknown FW')
            driver = device.get('Driver', 'Unknown Driver')
            first_pci = device.get('First_PCI', 'Unknown PCI').split('|')[0].strip()
            button_text = f"{desc}\nPN: {pn}\nFW: {fw}\nDriver: {driver}\nPCI: {first_pci}"
            button = tk.Button(self.root, text=button_text, command=lambda dev=device: self.show_device_info(dev))
            button.pack(pady=5)

        # Add additional buttons after the device buttons
        self.add_installation_buttons()

    def add_installation_buttons(self):
        """
        Add installation buttons (FW, OFED, BFB, DOCA) to the main window.
        """
        install_fw_button = tk.Button(self.root, text="Install FW", command=self.install_fw)
        install_fw_button.pack(pady=5)

        install_ofed_button = tk.Button(self.root, text="Install OFED", command=self.install_ofed)
        install_ofed_button.pack(pady=5)

        install_bfb_button = tk.Button(self.root, text="Install BFB", command=self.install_bfb)
        install_bfb_button.pack(pady=5)

        install_driver_button = tk.Button(self.root, text="Install DOCA", command=self.install_driver)
        install_driver_button.pack(pady=5)

    def install_fw(self):
        """
        Handle the installation of firmware.
        """
        self.show_device_dropdown("Install FW")

    def install_ofed(self):
        """
        Handle the installation of OFED.
        """
        self.show_device_dropdown("Install OFED")

    def install_bfb(self):
        """
        Handle the installation of BFB.
        """
        self.show_device_dropdown("Install BFB")

    def install_driver(self):
        """
        Handle the installation of DOCA.
        """
        self.show_device_dropdown("Install DOCA")

    def show_device_dropdown(self, action):
        """
        Display a dropdown list of devices and open a new window with installation options upon selection.

        Args:
            action (str): The action to be performed (e.g., "Install FW", "Install OFED", etc.).
        """
        device_names = [device.get('Desc', 'Unknown Desc') if device.get('Desc',
                                                                         'Unknown Desc') != 'Mellanox Technologies Device' else 'Mellanox Technologies Device [Bluefield-3]'
                        for device in self.devices]

        dropdown_window = tk.Toplevel(self.root)
        dropdown_window.title(f"Select Device for {action}")

        window_width = 500
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        dropdown_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        label = tk.Label(dropdown_window, text="Select a device:")
        label.pack(pady=10)

        selected_device = tk.StringVar()
        dropdown = ttk.Combobox(dropdown_window, textvariable=selected_device, values=device_names, width=70)
        dropdown.pack(pady=10)

        select_button = tk.Button(dropdown_window, text="Select",
                                  command=lambda: self.show_installation_form(dropdown_window, selected_device.get(),
                                                                              action))
        select_button.pack(pady=10)

    def show_installation_form(self, parent_window, device_name, action):
        """
        Display a form with text inputs and buttons for installing specific versions.

        Args:
            parent_window (tk.Toplevel): The parent window for displaying the installation form.
            device_name (str): The name of the selected device.
            action (str): The action to be performed (e.g., "Install FW", "Install OFED", etc.).
        """
        for widget in parent_window.winfo_children():
            widget.destroy()

        label = tk.Label(parent_window, text=f"{action} for {device_name}")
        label.pack(pady=10)

        version_label = tk.Label(parent_window, text="Enter specific version:")
        version_label.pack(pady=5)
        version_entry = tk.Entry(parent_window, width=50)  # Set width here
        version_entry.pack(pady=5)

        if action == "Install FW":
            version_entry.insert(tk.END, "12.22.1994")  # Example FW version
        elif action == "Install OFED":
            version_entry.insert(tk.END, "MLNX_OFED_LINUX-24.01-0.2.9.0")  # Example OFED version
        elif action == "Install BFB":
            version_entry.insert(tk.END, "DOCA_2.5.2_BSP_4.5.2_Ubuntu_22.04-9.24-06-LTS.dev")  # Example BFB version

        apply_button = tk.Button(parent_window, text="Apply",
                                 command=lambda: self.apply_version(device_name, version_entry.get(), action))
        apply_button.pack(pady=10)

        or_label = tk.Label(parent_window, text="OR")
        or_label.pack(pady=5)

        auto_update_button = tk.Button(parent_window, text="Automatic update to latest",
                                       command=lambda: self.update_device(device_name, action))
        auto_update_button.pack(pady=10)

    def apply_version(self, device_name, version, action):
        """
        Apply the specified version to the device.

        Args:
            device_name (str): The name of the device.
            version (str): The version to be applied.
            action (str): The action to be performed (e.g., "Install FW", "Install OFED", etc.).
        """
        self.show_message(f"Applying version {version} to {device_name} for {action}")

    def update_device(self, device_name, action):
        """
        Handle updating the device to the latest version.

        Args:
            device_name (str): The name of the device.
            action (str): The action to be performed (e.g., "Install FW", "Install OFED", etc.).
        """
        self.show_message(f"Updating {device_name} to latest version for {action}")

    def show_device_info(self, device):
        """
        Display detailed information about a selected device in a new window.

        Args:
            device (dict): Dictionary containing device information.
        """
        device_window = tk.Toplevel(self.root)
        device_window.title(f"Device Info: {device.get('Desc', 'Unknown Device')}")

        window_width = 1000
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        device_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        device_info = (
            "-----------------------------------------------------------------------------------------------------\n"
            f"{device.get('Dev', '')}\n"
            f" Desc: {device.get('Desc', 'Unknown Desc')}\n"
            f" PN: {device.get('PN', 'Unknown PN')}\n"
            f" PSID: {device.get('PSID', 'Unknown PSID')}\n"
            f" SN: {device.get('SN', 'Unknown SN')}\n"
            f" FW: {device.get('FW', 'Unknown FW')}\n"
            f" Driver: {device.get('Driver', 'Unknown Driver')}\n"
            f" Tempr: {device.get('Tempr', 'Unknown Tempr')}\n"
        )
        pci_lines = device.get('PCI', '').split('\n')
        for line in pci_lines:
            device_info += f"{line}\n"
        device_info += "-----------------------------------------------------------------------------------------------------\n"

        text = tk.Text(device_window, wrap=tk.WORD)
        text.insert(tk.END, device_info)
        text.config(state=tk.DISABLED)
        text.pack(expand=True, fill='both')

    def show_main_window(self):
        """
        Display the main window of the application.
        """
        if hasattr(self, 'message_label'):
            self.message_label.pack_forget()
        if hasattr(self, 'server_entry'):
            self.server_entry.pack_forget()
        if hasattr(self, 'submit_button'):
            self.submit_button.pack_forget()
        if hasattr(self, 'output_frame'):
            self.output_frame.pack_forget()

        self.request_button.pack(pady=10)
        self.close_button.pack(pady=10)

    def center_window(self, window):
        """
        Center the given window on the screen.

        Args:
            window: The window to be centered.
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry(f"{screen_width}x{screen_height}+0+0")

    def show_message(self, message):
        """
        Display a message box with the given message.

        Args:
            message (str): The message to be displayed.
        """
        messagebox.showinfo("Message", message)

    def close_application(self):
        """
        Close the application.
        """
        self.root.destroy()
