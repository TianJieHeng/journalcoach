# -*- coding: utf-8 -*-
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional
from .ui.view import MainView
from .ui.history import HistoryDialog
from .services.llm import LLMService
from .storage.jsonl_store import JSONLStore, build_record
from .utils.threads import run_in_thread
from .utils.retry import retry
from .utils.rate_limit import TokenBucket
from .config import env
from platformdirs import user_config_dir
import os

class Controller:
    def __init__(self, master: tk.Tk) -> None:
        self.view = MainView(
            master,
            self.on_ask,
            self.on_summarize,
            self.on_choose_file,
            self.on_clear,
            self.on_history,
        )
        self.llm = LLMService()
        self.original_entry: Optional[str] = None
        self.questions: Optional[str] = None
        self.answers: Optional[str] = None

        cfg_dir = user_config_dir("journalcoach", "journalcoach")
        os.makedirs(cfg_dir, exist_ok=True)
        self.cfg_path = os.path.join(cfg_dir, "config.json")

        self.store = JSONLStore(self._load_path_from_config())
        self.bucket = TokenBucket(env.get_rate_limit_per_minute())

        # Prompt for path if missing
        self.view.after(0, self._prompt_for_path_if_missing)

    def _prompt_for_path_if_missing(self) -> None:
        if not self.store.path:
            messagebox.showinfo("JournalCoach", "Choose a JSONL file to save your entries.")
            self.on_choose_file()

    def _load_path_from_config(self) -> Optional[str]:
        try:
            with open(self.cfg_path, "r", encoding="utf-8") as f:
                obj = json.load(f)
                return obj.get("jsonl_path")
        except Exception:
            return None

    def _save_path_to_config(self, path: str) -> None:
        with open(self.cfg_path, "w", encoding="utf-8") as f:
            json.dump({"jsonl_path": path}, f)

    def on_choose_file(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".jsonl",
            filetypes=[("JSON Lines", "*.jsonl"), ("All Files", "*.*")],
            title="Choose or create your journal JSONL file",
        )
        if path:
            self.store.set_path(path)
            self._save_path_to_config(path)
            self.view.set_status("Using file: " + path)
            messagebox.showinfo("JournalCoach", "Using file:\n" + path)

    def on_history(self) -> None:
        if not self.store.path:
            self._prompt_for_path_if_missing()
            if not self.store.path:
                return
        try:
            HistoryDialog(self.view, self.store)
        except Exception as exc:
            messagebox.showerror("JournalCoach", "Could not open history: " + str(exc))

    def on_clear(self) -> None:
        self.view.set_input("")
        self.view.clear_output()
        self.view.set_status("Ready")
        self.original_entry = None
        self.questions = None
        self.answers = None

    def on_ask(self) -> None:
        if not self.bucket.allow():
            messagebox.showwarning("Rate Limit", "Please wait before making another request.")
            return

        entry = self.view.get_input().strip()
        if not entry:
            messagebox.showwarning("JournalCoach", "Please write your journal entry in the input box.")
            return

        self.original_entry = entry
        self.view.clear_output()
        self.view.set_status("Calling GPT for questions...")
        self.view.pb.start(10)

        def work():
            try:
                acc = []

                def on_delta(s: str) -> None:
                    acc.append(s)
                    self.view.after(0, self.view.append_output, s)

                text = retry(lambda: self.llm.stream_questions(entry, on_delta))
                self.questions = text
                self.view.after(0, self.view.set_status, "Questions ready. Type your answers in the input box, then click Summarize & Save.")
                self.view.after(0, self.view.set_input, "")
            except Exception as exc:
                self.view.after(0, self.view.append_output, "\n\n[Error] " + str(exc))
                self.view.after(0, self.view.set_status, "Error while asking questions.")
            finally:
                self.view.after(0, self.view.pb.stop)

        run_in_thread(work)

    def on_summarize(self) -> None:
        if not self.bucket.allow():
            messagebox.showwarning("Rate Limit", "Please wait before making another request.")
            return

        if not self.original_entry or not self.questions:
            messagebox.showwarning("JournalCoach", "First write an entry and click Ask Questions.")
            return
        if not self.store.path:
            self._prompt_for_path_if_missing()
            if not self.store.path:
                return

        self.answers = self.view.get_input().strip()
        if not self.answers:
            messagebox.showwarning("JournalCoach", "Please type your answers in the input box first.")
            return

        self.view.set_status("Summarizing and saving...")
        self.view.pb.start(10)

        def work():
            try:
                title, summary = retry(
                    lambda: self.llm.summarize_and_clean(
                        self.original_entry, self.questions, self.answers
                    )
                )
                record = build_record(title=title, summary=summary)
                try:
                    self.store.append_entry(record)
                except Exception:
                    self.store.ensure_file()
                    self.store.append_entry(record)

                self.view.after(0, self.view.clear_output)
                self.view.after(0, self.view.append_output, "Title: " + title + "\n\n" + summary + "\n")
                self.view.after(0, self.view.set_status, "Saved.")
            except Exception as exc:
                self.view.after(0, self.view.append_output, "\n\n[Error] " + str(exc))
                self.view.after(0, self.view.set_status, "Error while summarizing.")
            finally:
                self.view.after(0, self.view.pb.stop)

        run_in_thread(work)
