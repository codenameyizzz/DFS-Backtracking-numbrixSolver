# main.py

import tkinter as tk
from gui import NumbrixApp

def main():
    root = tk.Tk()
    app = NumbrixApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
