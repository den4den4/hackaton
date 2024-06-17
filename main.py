#!/usr/bin/env python3

from tkinter import Tk
from gui import GUI
from connection_manager import ConnectionManager
from action import Action

if __name__ == "__main__":
    root = Tk()  # Create a Tkinter root window
    connection_manager = ConnectionManager()  # Initialize ConnectionManager
    action = Action()  # Initialize Action

    app = GUI(root, connection_manager, action)  # Instantiate the GUI with required arguments

    root.mainloop()  # Start the Tkinter main event loop
