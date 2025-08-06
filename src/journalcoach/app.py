# -*- coding: utf-8 -*-
import tkinter as tk
from .controller import Controller

def main() -> None:
    root = tk.Tk()
    Controller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
