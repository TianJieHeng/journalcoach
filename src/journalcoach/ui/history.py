# -*- coding: utf-8 -*-
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
from ..storage.jsonl_store import JSONLStore

class HistoryDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, store: JSONLStore) -> None:
        super().__init__(master)
        self.title("History")
        self.geometry("800x500")
        self.minsize(700, 400)
        self.store = store
        self.entries: List[Dict] = []
        self.filtered: List[Dict] = []

        # Layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Path row
        path_frame = ttk.Frame(self)
        path_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        path_frame.columnconfigure(0, weight=1)
        self.lbl_path = ttk.Label(path_frame, text="File: " + (self.store.path or "(not set)"))
        self.lbl_path.grid(row=0, column=0, sticky="w")
        self.btn_open_file = ttk.Button(path_frame, text="Open File", command=self._open_file)
        self.btn_open_file.grid(row=0, column=1, padx=4)
        self.btn_open_folder = ttk.Button(path_frame, text="Open Folder", command=self._open_folder)
        self.btn_open_folder.grid(row=0, column=2, padx=4)

        # Search row
        search_frame = ttk.Frame(self)
        search_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky="w")
        self.var_q = tk.StringVar()
        self.ent_search = ttk.Entry(search_frame, textvariable=self.var_q)
        self.ent_search.grid(row=0, column=1, sticky="ew", padx=6)
        search_frame.columnconfigure(1, weight=1)
        self.btn_refresh = ttk.Button(search_frame, text="Refresh", command=self._load_entries)
        self.btn_refresh.grid(row=0, column=2, padx=4)
        self.btn_clear = ttk.Button(search_frame, text="Clear", command=self._clear_search)
        self.btn_clear.grid(row=0, column=3, padx=4)

        # Main split: list and detail
        main = ttk.Frame(self)
        main.grid(row=2, column=0, sticky="nsew", padx=8, pady=6)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Entries").grid(row=0, column=0, sticky="w")
        self.listbox = tk.Listbox(left, exportselection=False)
        self.listbox.grid(row=1, column=0, sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Details").grid(row=0, column=0, sticky="w")
        self.txt_detail = tk.Text(right, wrap="word", height=10, state="disabled")
        self.txt_detail.grid(row=1, column=0, sticky="nsew")

        # Events
        self.var_q.trace_add("write", lambda *_: self._apply_filter())

        # Modal-ish behavior
        self.transient(master)
        self.grab_set()

        # Initial load
        self._load_entries()

    def _open_file(self) -> None:
        path = self.store.path
        if not path or not os.path.exists(path):
            messagebox.showwarning("History", "JSONL file not found.")
            return
        try:
            os.startfile(path)  # Windows
        except Exception as exc:
            messagebox.showerror("History", "Could not open file: " + str(exc))

    def _open_folder(self) -> None:
        path = self.store.path
        if not path:
            messagebox.showwarning("History", "JSONL path is not set.")
            return
        folder = os.path.dirname(path) or "."
        if not os.path.exists(folder):
            messagebox.showwarning("History", "Folder not found: " + folder)
            return
        try:
            os.startfile(folder)  # Windows
        except Exception as exc:
            messagebox.showerror("History", "Could not open folder: " + str(exc))

    def _clear_search(self) -> None:
        self.var_q.set("")

    def _load_entries(self) -> None:
        try:
            self.entries = list(self.store.load_all())
        except Exception as exc:
            messagebox.showerror("History", "Could not load entries: " + str(exc))
            self.entries = []
        # Sort by time_gmt_iso if present, else by date_local, newest first
        def sort_key(e: Dict) -> str:
            return str(e.get("time_gmt_iso", "")) or str(e.get("date_local", ""))
        self.entries.sort(key=sort_key, reverse=True)
        self._apply_filter()

    def _apply_filter(self) -> None:
        q = self.var_q.get().strip().lower()
        if q:
            def match(e: Dict) -> bool:
                parts = [
                    str(e.get("date_local", "")),
                    str(e.get("time_gmt_iso", "")),
                    str(e.get("title", "")),
                    str(e.get("summary", "")),
                ]
                hay = " ".join(parts).lower()
                return q in hay
            self.filtered = [e for e in self.entries if match(e)]
        else:
            self.filtered = list(self.entries)
        self._reload_listbox()

    def _reload_listbox(self) -> None:
        self.listbox.delete(0, "end")
        for e in self.filtered:
            date_local = str(e.get("date_local", ""))
            title = str(e.get("title", "Untitled"))
            self.listbox.insert("end", date_local + " - " + title)
        # Clear details when list changes
        self._set_detail_text("")

    def _on_select(self, _evt=None) -> None:
        idxs = self.listbox.curselection()
        if not idxs:
            return
        i = idxs[0]
        if i < 0 or i >= len(self.filtered):
            return
        e = self.filtered[i]
        self._show_entry(e)

    def _show_entry(self, e: Dict) -> None:
        date_local = str(e.get("date_local", ""))
        time_gmt_iso = str(e.get("time_gmt_iso", ""))
        title = str(e.get("title", "Untitled"))
        summary = str(e.get("summary", ""))
        text = []
        text.append("Date (local): " + date_local)
        text.append("Time (UTC): " + time_gmt_iso)
        text.append("Title: " + title)
        text.append("")
        text.append(summary)
        self._set_detail_text("\n".join(text))

    def _set_detail_text(self, value: str) -> None:
        self.txt_detail.configure(state="normal")
        self.txt_detail.delete("1.0", "end")
        self.txt_detail.insert("1.0", value)
        self.txt_detail.configure(state="disabled")
