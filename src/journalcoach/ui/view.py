# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from typing import Callable

class MainView(ttk.Frame):
    def __init__(
        self,
        master,
        on_ask: Callable[[], None],
        on_summarize: Callable[[], None],
        on_choose_file: Callable[[], None],
        on_clear: Callable[[], None],
        on_history: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self.grid(sticky="nsew")
        master.title("JournalCoach")
        master.geometry("900x600")
        master.minsize(700, 400)

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.lbl_in = ttk.Label(self, text="Input")
        self.lbl_in.grid(row=0, column=0, sticky="w", padx=6, pady=(6, 0))

        self.txt_in = tk.Text(self, wrap="word", height=12, undo=True)
        self.txt_in.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        self.lbl_out = ttk.Label(self, text="Return")
        self.lbl_out.grid(row=2, column=0, sticky="w", padx=6, pady=(6, 0))

        self.txt_out = tk.Text(self, wrap="word", height=12, state="disabled")
        self.txt_out.grid(row=3, column=0, sticky="nsew", padx=6, pady=6)

        btns = ttk.Frame(self)
        btns.grid(row=4, column=0, sticky="ew", padx=6, pady=6)
        for i in range(5):
            btns.columnconfigure(i, weight=1)

        self.btn_ask = ttk.Button(btns, text="Ask Questions", command=on_ask)
        self.btn_ask.grid(row=0, column=0, sticky="ew", padx=4)

        self.btn_sum = ttk.Button(btns, text="Summarize & Save", command=on_summarize)
        self.btn_sum.grid(row=0, column=1, sticky="ew", padx=4)

        self.btn_choose = ttk.Button(btns, text="Choose JSONL", command=on_choose_file)
        self.btn_choose.grid(row=0, column=2, sticky="ew", padx=4)

        self.btn_history = ttk.Button(btns, text="History", command=on_history)
        self.btn_history.grid(row=0, column=3, sticky="ew", padx=4)

        self.btn_clear = ttk.Button(btns, text="Clear", command=on_clear)
        self.btn_clear.grid(row=0, column=4, sticky="ew", padx=4)

        status_row = ttk.Frame(self)
        status_row.grid(row=5, column=0, sticky="ew", padx=6, pady=(0, 6))
        status_row.columnconfigure(0, weight=1)
        self.status = ttk.Label(status_row, text="Ready")
        self.status.grid(row=0, column=0, sticky="w")
        self.pb = ttk.Progressbar(status_row, mode="indeterminate", length=140)
        self.pb.grid(row=0, column=1, sticky="e", padx=4)

    def get_input(self) -> str:
        return self.txt_in.get("1.0", "end-1c")

    def set_input(self, text: str) -> None:
        self.txt_in.delete("1.0", "end")
        self.txt_in.insert("1.0", text)

    def append_output(self, text: str) -> None:
        self.txt_out.configure(state="normal")
        self.txt_out.insert("end", text)
        self.txt_out.see("end")
        self.txt_out.configure(state="disabled")

    def clear_output(self) -> None:
        self.txt_out.configure(state="normal")
        self.txt_out.delete("1.0", "end")
        self.txt_out.configure(state="disabled")

    def set_status(self, text: str) -> None:
        self.status.configure(text=text)
