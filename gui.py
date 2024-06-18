import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
from action import Action
from firmware import Firmware
from connection_manager import ConnectionManager
from bfb import BFB
from ofed import OFED


class GUI:
    def __init__(self, root, connection_manager, action):
        self.root = root
        self.connection_manager = connection_manager
        self.action = action
        self.devices = []
        self.firmware = Firmware(self.connection_manager)
        self.bfb = BFB(self.connection_manager)
        self.setup_ui()
        self.ofed = OFED(self.connection_manager)
        self.username = ''
        self.password = ''
        self.server_name = ''

    def setup_ui(self):
        self.root.title("Card Configurator")
        self.center_window(self.root)

        self.request_button = tk.Button(self.root, text="Request Server Machine Name",
                                        command=self.show_server_name_input)
        self.request_button.pack(pady=10)

        self.close_button = tk.Button(self.root, text="Close Application", command=self.close_application)
        self.close_button.pack(pady=10)

    def show_server_name_input(self):
        self.request_button.pack_forget()
        self.close_button.pack_forget()

        self.message_label = tk.Label(self.root, text="Please enter the server machine name or IP address:")
        self.message_label.pack(pady=10)

        self.server_entry = tk.Entry(self.root)
        self.server_entry.pack(pady=5)

        self.submit_button = tk.Button(self.root, text="Submit", command=self.request_machine_ip)
        self.submit_button.pack(pady=10)

        self.bind_enter_key()

    def bind_enter_key(self):
        self.server_entry.bind("<Return>", lambda event: self.submit_button.invoke())

    def request_machine_ip(self):
        self.server_name = self.server_entry.get()
        if self.server_name:
            if self.connection_manager.is_valid_hostname_or_ip(self.server_name):
                self.message_label.pack_forget()
                self.server_entry.pack_forget()
                self.submit_button.pack_forget()

                self.username = simpledialog.askstring("Input", "Please enter your username:")
                if self.username:
                    self.password = simpledialog.askstring("Input", "Please enter your password:", show='*')
                    if self.password:
                        ssh = self.connection_manager.ssh_connect(self.server_name, self.username, self.password)
                        if ssh:
                            self.show_message(f"Connected successfully to {self.server_name}")
                            output = self.connection_manager.install_and_run_lhca(ssh)
                            if output is not None:
                                self.display_output(output)
                                self.create_device_buttons(output)
                            ssh.close()
                        else:
                            self.show_message(f"Failed to connect to {self.server_name}")
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
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD)
        self.output_text.pack(side=tk.LEFT, expand=True, fill='both')

        self.scrollbar = tk.Scrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')

        self.output_text.config(yscrollcommand=self.scrollbar.set)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)

    def create_device_buttons(self, output):
        self.devices = self.action.parse_output(output)
        for device in self.devices:
            desc = device.get('Desc', 'Unknown Desc')
            if desc == 'Mellanox Technologies Device':
                desc = 'Mellanox Technologies Device [Bluefield-3]'
            pn = device.get('PN', 'Unknown PN')
            fw = device.get('FW', 'Unknown FW')
            driver = device.get('Driver', 'Unknown Driver')
            first_pci = device.get('First_PCI', 'Unknown PCI').split('|')[0]
            button_text = f"{desc}\nPN: {pn}\nFW: {fw}\nDriver: {driver}\nPCI: {first_pci}"
            button = tk.Button(self.root, text=button_text, command=lambda dev=device: self.show_device_info(dev))
            button.pack(pady=5)

        self.add_installation_buttons()

    def add_installation_buttons(self):
        install_fw_button = tk.Button(self.root, text="Install FW", command=self.install_fw)
        install_fw_button.pack(pady=5)

        install_ofed_button = tk.Button(self.root, text="Install OFED", command=self.show_ofed_installation_window)
        install_ofed_button.pack(pady=5)

        install_bfb_button = tk.Button(self.root, text="Install BFB", command=self.install_bfb)
        install_bfb_button.pack(pady=5)

        install_driver_button = tk.Button(self.root, text="Install DOCA", command=self.install_driver)
        install_driver_button.pack(pady=5)

    # def show_ofed_installation_window(self):
    #     ofed_install_window = tk.Toplevel(self.root)
    #     ofed_install_window.title("Install OFED")
    #
    #     label = tk.Label(ofed_install_window, text="Enter specific version:")
    #     label.pack(pady=10)
    #
    #     version_entry = tk.Entry(ofed_install_window, width=50)
    #     version_entry.pack(pady=5)
    #     version_entry.insert(tk.END, "24.01-0.2.9.0")
    #
    #     apply_button = tk.Button(ofed_install_window, text="Apply",
    #                              command=lambda: self.apply_ofed_installation(version_entry.get(), ofed_install_window))
    #     apply_button.pack(pady=10)

    def show_ofed_installation_window(self):
        ofed_install_window = tk.Toplevel(self.root)
        ofed_install_window.title("OFED Installation")

        window_width = 500
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        ofed_install_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        label = tk.Label(ofed_install_window, text="Enter specific version:")
        label.pack(pady=10)

        version_entry = tk.Entry(ofed_install_window, width=50)
        version_entry.pack(pady=10)

        version_entry.insert(tk.END, "24.01-0.2.9.0")

        apply_button = tk.Button(ofed_install_window, text="Apply",
                                 command=lambda: self.apply_version_ofed(version_entry.get(), ofed_install_window))
        apply_button.pack(pady=10)

        or_label = tk.Label(ofed_install_window, text="OR")
        or_label.pack(pady=5)

        auto_update_button = tk.Button(ofed_install_window, text="Automatic update to latest",
                                       command=lambda: self.update_ofed(ofed_install_window))
        auto_update_button.pack(pady=10)

    def apply_version_ofed(self, version, parent_window):
        self.show_message(f"Applying OFED version {version}")

        ssh = self.connection_manager.ssh_connect(self.server_name, self.username, self.password)
        if not ssh:
            self.show_message(f"Failed to connect to {self.server_name}")
            return

        self.show_progress_window()
        threading.Thread(target=self.install_ofed, args=(version, ssh, parent_window)).start()

    def update_ofed(self, parent_window):
        self.show_message("Updating OFED to latest version")

        ssh = self.connection_manager.ssh_connect(self.server_name, self.username, self.password)
        if not ssh:
            self.show_message(f"Failed to connect to {self.server_name}")
            return

        self.show_progress_window()
        threading.Thread(target=self.install_ofed_latest, args=(ssh, parent_window)).start()

    def install_ofed_latest(self, ssh, parent_window):
        output = self.ofed.install_latest(ssh)
        self.show_message(output, text_flag=True)
        self.progress_window.destroy()
        parent_window.destroy()
        ssh.close()


    def apply_ofed_installation(self, version, ofed_install_window):
        ofed_install_window.destroy()
        self.show_message(f"Installing OFED version: {version}")
        # Add your logic to install OFED here

    def install_fw(self):
        self.show_device_dropdown("Install FW")

    def install_driver(self):
        self.show_device_dropdown("Install DOCA")

    def show_device_dropdown(self, action):
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
        if parent_window:
            for widget in parent_window.winfo_children():
                widget.destroy()

        label = tk.Label(parent_window or self.root, text=f"{action} for {device_name}")
        label.pack(pady=10)

        version_label = tk.Label(parent_window or self.root, text="Enter specific version:")
        version_label.pack(pady=5)
        version_entry = tk.Entry(parent_window or self.root, width=50)
        version_entry.pack(pady=5)

        if action == "Install FW":
            version_entry.insert(tk.END, "12.22.1994")
        elif action == "Install DOCA":
            version_entry.insert(tk.END, "DOCA_2.5.2_BSP_4.5.2_Ubuntu_22.04-9.24-06-LTS.dev")

        apply_button = tk.Button(parent_window or self.root, text="Apply",
                                 command=lambda: self.apply_version(device_name, version_entry.get(), action,
                                                                    parent_window))
        apply_button.pack(pady=10)

        or_label = tk.Label(parent_window or self.root, text="OR")
        or_label.pack(pady=5)

        auto_update_button = tk.Button(parent_window or self.root, text="Automatic update to latest",
                                       command=lambda: self.update_device(device_name, action, parent_window))
        auto_update_button.pack(pady=10)

    def apply_version(self, device_name, version, action, parent_window):
        self.show_message(f"Applying version {version} to {device_name} for {action}")

        device = next((d for d in self.devices if d.get('Desc', '') == device_name), None)
        if not device:
            self.show_message(f"Device {device_name} not found.")
            return

        ssh = self.connection_manager.ssh_connect(self.server_name, self.username, self.password)
        if not ssh:
            self.show_message(f"Failed to connect to {self.server_name}")
            return

        if action == "Install FW":
            self.show_progress_window()
            threading.Thread(target=self.install_firmware, args=(device, version, ssh, parent_window)).start()
        elif action == "Install OFED":
            # Directly show OFED installation window, no need to create a separate thread
            self.show_ofed_installation_window()
        elif action == "Install BFB":
            threading.Thread(target=self.install_bfb, args=(device, version, ssh, parent_window)).start()
        elif action == "Install DOCA":
            threading.Thread(target=self.install_driver, args=(device, version, ssh, parent_window)).start()

    def install_firmware(self, device, version, ssh, parent_window):
        output = self.firmware.install(device, version, ssh)
        self.show_message(output, text_flag=True)
        self.progress_window.destroy()
        if parent_window:
            parent_window.destroy()
        ssh.close()

    def install_bfb(self, device, version, ssh, parent_window):
        output = self.bfb.install(device, version, ssh)
        self.show_message(output, text_flag=True)
        if parent_window:
            parent_window.destroy()
        ssh.close()

    def install_ofed(self, version, ssh, parent_window):
        output = self.ofed.install(version, ssh)
        self.show_message(output, text_flag=True)
        self.progress_window.destroy()
        if parent_window:
            parent_window.destroy()
        ssh.close()

    def install_driver(self, device, version, ssh, parent_window):
        output = self.connection_manager.install_driver(device, version, ssh)
        self.show_message(output)
        if parent_window:
            parent_window.destroy()
        ssh.close()

    def show_progress_window(self):
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Installing Firmware")
        self.progress_window.geometry("400x200")
        label = tk.Label(self.progress_window, text="Installation in progress...")
        label.pack(pady=40)

        self.progress_label = tk.Label(self.progress_window, text="")
        self.progress_label.pack(pady=40)

        self.update_progress()

    def update_progress(self):
        current_text = self.progress_label.cget("text")
        new_text = current_text + "." if len(current_text) < 3 else ""
        self.progress_label.config(text=new_text)
        self.progress_label.after(500, self.update_progress)

    def update_device(self, device_name, action, parent_window):
        self.show_message(f"Updating {device_name} to latest version for {action}")
        if parent_window:
            parent_window.destroy()

    def show_device_info(self, device):
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
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry(f"{screen_width}x{screen_height}+0+0")

    def show_message(self, message, text_flag=False):
        if text_flag:
            message_window = tk.Toplevel(self.root)
            message_window.title("Message")
            message_window.geometry("700x700")

            text_widget = tk.Text(message_window, wrap=tk.WORD)
            text_widget.pack(side=tk.LEFT, expand=True, fill='both')

            scrollbar = tk.Scrollbar(message_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill='y')

            text_widget.config(yscrollcommand=scrollbar.set)
            text_widget.insert(tk.END, message)
            text_widget.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Message", message)

    def close_application(self):
        self.root.destroy()


