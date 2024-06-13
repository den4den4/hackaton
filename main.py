#!/usr/bin/env python3
import tkinter as tk

from action import Action
from gui import GUI
from connection_manager import ConnectionManager

# ==============MAIN===========================
if __name__ == "__main__":
    root = tk.Tk()
    connection_manager = ConnectionManager()
    action = Action()  # Create an instance of the Action class
    app = GUI(root, connection_manager, action)
    root.mainloop()


