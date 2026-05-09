"""
Food Hub Ticket Bot — Interfaz gráfica
"""

import tkinter as tk
from tkinter import scrolledtext
import json
import threading
import asyncio
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

# ── Paleta ─────────────────────────────────────────────────────────────────────
BG       = "#16161a"
BG2      = "#1f1f26"
BG3      = "#2a2a35"
ACCENT   = "#f5c842"
ACCENT_H = "#ffd84d"
TEXT     = "#f0eeff"
TEXT_DIM = "#7c7a8e"
BORDER   = "#35334a"
GREEN    = "#3ddc84"
RED      = "#ff6b6b"
YELLOW   = "#ffd166"

FONT      = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SM   = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 9)


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class StyledEntry(tk.Frame):
    """Entry con borde personalizado y focus highlight."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BORDER, padx=1, pady=1)
        self.entry = tk.Entry(
            self, font=FONT, bg=BG2, fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            bd=0, **kwargs
        )
        self.entry.pack(fill="x", ipady=7, padx=1, pady=1)
        self.entry.bind("<FocusIn>",  lambda e: self.configure(bg=ACCENT))
        self.entry.bind("<FocusOut>", lambda e: self.configure(bg=BORDER))

    def get(self):        return self.entry.get()
    def insert(self, i, v): self.entry.insert(i, v)
    def delete(self, a, b): self.entry.delete(a, b)


class StyledDropdown(tk.Frame):
    """Dropdown personalizado sin ttk — con texto legible."""
    def __init__(self, parent, options, default="", **kwargs):
        super().__init__(parent, bg=BORDER, padx=1, pady=1)
        self.options   = options
        self.var       = tk.StringVar(value=default or options[0])
        self.expanded  = False

        # Botón principal
        self.btn = tk.Button(
            self, textvariable=self.var,
            font=FONT, bg=BG2, fg=TEXT,
            activebackground=BG3, activeforeground=TEXT,
            relief="flat", anchor="w", padx=10,
            cursor="hand2", bd=0,
            command=self._toggle
        )
        self.btn.pack(fill="x", ipady=6)

        # Flecha
        self.arrow = tk.Label(
            self.btn, text="▾", font=("Segoe UI", 9),
            bg=BG2, fg=TEXT_DIM
        )
        self.arrow.place(relx=1.0, rely=0.5, anchor="e", x=-10)

        # Popup de opciones (toplevel)
        self._popup = None

    def _toggle(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
            self._popup = None
            return
        self._open_popup()

    def _open_popup(self):
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        w = self.winfo_width()

        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.geometry(f"{w}x{len(self.options)*34}+{x}+{y}")
        popup.configure(bg=BORDER)
        self._popup = popup

        for opt in self.options:
            def make_cmd(o=opt):
                return lambda: self._select(o, popup)
            btn = tk.Button(
                popup, text=opt, font=FONT,
                bg=BG3, fg=TEXT,
                activebackground=ACCENT, activeforeground=BG,
                relief="flat", anchor="w", padx=12,
                cursor="hand2", bd=0,
                command=make_cmd()
            )
            btn.pack(fill="x", pady=1, padx=1, ipady=5)

        popup.bind("<FocusOut>", lambda e: popup.destroy())
        popup.focus_set()

    def _select(self, value, popup):
        self.var.set(value)
        popup.destroy()
        self._popup = None

    def get(self): return self.var.get()
    def set(self, v): self.var.set(v)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Food Hub Bot")
        self.geometry("480x640")
        self.resizable(False, False)
        self.configure(bg=BG)

        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        self.bot_running = False
        cfg = load_config()
        self._build_ui(cfg)

    def _label(self, parent, text, small=False):
        return tk.Label(
            parent, text=text,
            font=FONT_SM if small else FONT,
            bg=BG, fg=TEXT_DIM if small else TEXT,
            anchor="w"
        )

    def _section(self, text):
        f = tk.Frame(self, bg=BG)
        f.pack(fill="x", padx=24, pady=(14, 4))
        tk.Label(f, text=text, font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=TEXT_DIM, anchor="w").pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x",
                                               expand=True, padx=(8, 0), pady=6)

    def _build_ui(self, cfg):
        # ── Header ─────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=ACCENT, height=4)
        hdr.pack(fill="x")

        title_frame = tk.Frame(self, bg=BG, pady=18)
        title_frame.pack(fill="x", padx=24)

        tk.Label(title_frame, text="⚡ Food Hub Bot",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(title_frame, text="USYD · USU",
                 font=("Segoe UI", 9),
                 bg=BG, fg=TEXT_DIM).pack(side="right", pady=6)

        # ── Datos personales ────────────────────────────────────────────────────
        self._section("DATOS DEL COMPRADOR")

        self.fields = {}
        fields_def = [
            ("first_name", "Nombre"),
            ("last_name",  "Apellido"),
            ("email",      "Email"),
            ("mobile",     "Móvil"),
        ]
        for key, label in fields_def:
            row = tk.Frame(self, bg=BG)
            row.pack(fill="x", padx=24, pady=2)
            tk.Label(row, text=label, font=FONT_SM, bg=BG,
                     fg=TEXT_DIM, width=10, anchor="w").pack(side="left")
            entry = StyledEntry(row)
            entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
            entry.insert(0, cfg.get(key, ""))
            self.fields[key] = entry

        # ── Ticket info ─────────────────────────────────────────────────────────
        self._section("TICKET INFO")

        self.dropdowns = {}
        drops_def = [
            ("student_type",  "Estudiante",  ["Domestic", "International", "Staff", "Other"]),
            ("student_level", "Nivel",       ["Postgraduate", "Undergraduate", "Staff", "Other"]),
            ("usu_member",    "USU Member",  ["Yes", "No"]),
        ]
        for key, label, options in drops_def:
            row = tk.Frame(self, bg=BG)
            row.pack(fill="x", padx=24, pady=2)
            tk.Label(row, text=label, font=FONT_SM, bg=BG,
                     fg=TEXT_DIM, width=10, anchor="w").pack(side="left")
            dd = StyledDropdown(row, options, default=cfg.get(key, options[0]))
            dd.pack(side="left", fill="x", expand=True, padx=(6, 0))
            self.dropdowns[key] = dd

        # ── Botón ───────────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=BG, pady=18)
        btn_frame.pack(fill="x", padx=24)

        self.run_btn = tk.Button(
            btn_frame,
            text="▶   EJECUTAR BOT",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT, fg=BG,
            activebackground=ACCENT_H, activeforeground=BG,
            relief="flat", cursor="hand2",
            padx=20, pady=12,
            command=self.toggle_bot
        )
        self.run_btn.pack(fill="x")

        # Hover effect
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.configure(bg=ACCENT_H))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.configure(
            bg=ACCENT if not self.bot_running else BG3))

        # ── Log ─────────────────────────────────────────────────────────────────
        self._section("LOG")

        log_container = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        log_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.log = scrolledtext.ScrolledText(
            log_container,
            font=FONT_MONO, bg=BG2, fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            state="disabled", height=8, bd=0,
            padx=8, pady=6
        )
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("ok",   foreground=GREEN)
        self.log.tag_config("err",  foreground=RED)
        self.log.tag_config("live", foreground=YELLOW)
        self.log.tag_config("dim",  foreground=TEXT_DIM)

        self._log("Configura tus datos y pulsa Ejecutar.", "dim")

    def _log(self, msg, tag=""):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def log_thread_safe(self, msg, tag=""):
        self.after(0, lambda: self._log(msg, tag))

    def toggle_bot(self):
        if self.bot_running:
            self.bot_running = False
            self.run_btn.configure(text="▶   EJECUTAR BOT", bg=ACCENT)
            self._log("Bot detenido.", "err")
            return

        for key, entry in self.fields.items():
            if not entry.get().strip():
                self._log(f"⚠ Rellena el campo: {key}", "err")
                return

        cfg = {k: v.get().strip() for k, v in self.fields.items()}
        cfg.update({k: v.get() for k, v in self.dropdowns.items()})
        save_config(cfg)

        self.bot_running = True
        self.run_btn.configure(text="⏹   DETENER", bg=BG3)
        self._log("─" * 38, "dim")
        self._log("Iniciando bot…", "live")

        threading.Thread(target=self._run_bot, args=(cfg,), daemon=True).start()

    def _run_bot(self, cfg):
        try:
            asyncio.run(self._bot_main(cfg))
        except Exception as e:
            self.log_thread_safe(f"✘ Error: {e}", "err")
        finally:
            self.bot_running = False
            self.after(0, lambda: self.run_btn.configure(
                text="▶   EJECUTAR BOT", bg=ACCENT))

    async def _bot_main(self, cfg):
        from bot import run_bot
        await run_bot(cfg, self.log_thread_safe)


if __name__ == "__main__":
    app = App()
    app.mainloop()
