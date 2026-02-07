"""
Speech-to-Text - Minimalist floating hub.
Glassmorphism pill + ses dalgasi animasyonu.
Konusmayi otomatik yapistir, hic yazi/bilgi yok.
"""

import ctypes
import json
import math
import os
import re
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import keyboard as kb_hotkey
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFilter, ImageTk
from pynput.keyboard import Key, Controller as KeyboardController
from pynput import mouse as pynput_mouse

# DPI awareness - piksel keskinligi
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# --- Config ---
CONFIG_PATH = Path(__file__).parent / "config.json"
DEFAULT_CONFIG = {
    "model_size": "small",
    "language": "tr",
    "input_device_index": None,
    "input_device_name": "",
    "hotkey": "mouse_x1",
    "beam_size": 1,
    "button_position": [100, 100],
    "button_size": 56,
    "initial_prompt": "GTRL, RL, AI, ML, DQN, PPO, SAC, TD3, A2C, GPU, CPU, API, LLM, NLP, CNN, RNN, LSTM, GAN, VAE, transformer, epoch, batch, gradient, loss, reward, policy, agent, environment, state, action, observation, GitHub, repo, commit, push, pull, merge, branch, PR, README, open-source, pip, Python, npm, Docker, VSCode, Claude",
}
SAMPLE_RATE = 16000
MIN_RECORDING_SECONDS = 0.5

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008

# --- Renkler ---
C_BG = "#0d0d0d"
C_SURFACE = "#1a1a1a"
C_ACCENT = "#6c5ce7"
C_ACCENT_GLOW = "#a29bfe"
C_REC = "#ff4757"
C_REC_GLOW = "#ff6b81"
C_TRANS = "#ffa502"
C_TRANS_GLOW = "#ffbe76"
C_SUCCESS = "#2ed573"
C_TEXT = "#e0e0e0"
C_DIM = "#555555"
TRANSPARENT = "#010101"

# Pill durumlari: (arkaplan, kenar, glow_rengi)
PILL_STYLES = {
    "loading":      ("#141418", "#2a2a2e", None),
    "idle":         ("#16162a", "#6c5ce7", "#6c5ce7"),
    "recording":    ("#2a1218", "#ff4757", "#ff4757"),
    "transcribing": ("#2a2010", "#ffa502", "#ffa502"),
    "success":      ("#0e2a16", "#2ed573", "#2ed573"),
}

# Pill boyutlari
PILL_W, PILL_H = 72, 28
PILL_R = PILL_H // 2
PILL_PAD = 3  # sadece anti-alias icin minimal margin
CVW = PILL_W + PILL_PAD * 2
CVH = PILL_H + PILL_PAD * 2

MOUSE_HOTKEYS = {
    "mouse_middle": "Mouse Orta Tik",
    "mouse_x1": "Mouse Yan 1",
    "mouse_x2": "Mouse Yan 2",
}


# --- Yardimci ---

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            c = DEFAULT_CONFIG.copy()
            c.update(saved)
            if "<" in c.get("hotkey", ""):
                c["hotkey"] = re.sub(r"[<>]", "", c["hotkey"])
            return c
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def blend(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"


def hex_rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def make_non_activating(root):
    try:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        s = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        s |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, s)
    except Exception:
        pass


def get_hotkey_display(h):
    return MOUSE_HOTKEYS.get(h, h.replace("+", " + ").title())


def render_pill(bg_hex, border_hex, glow_hex=None):
    """3x supersample ile anti-aliased temiz pill. Glow yok, bordur yok."""
    S = 4  # daha yuksek supersample = daha temiz kenar
    p = PILL_PAD * S
    fw, fh = CVW * S, CVH * S
    r = PILL_R * S
    bg = hex_rgb(bg_hex)
    bd = hex_rgb(border_hex)
    tr = hex_rgb(TRANSPARENT)

    img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))

    # Pill govde + ince renkli kenar
    ImageDraw.Draw(img).rounded_rectangle(
        [p, p, fw - p, fh - p], radius=r,
        fill=bg + (250,), outline=bd + (140,), width=S)

    # Ust cam parlama
    shine = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    ImageDraw.Draw(shine).rounded_rectangle(
        [p + S * 3, p + S, fw - p - S * 3, p + fh // 4],
        radius=r // 3, fill=(255, 255, 255, 22))
    shine = shine.filter(ImageFilter.GaussianBlur(S))
    img = Image.alpha_composite(img, shine)

    # Downsample
    img = img.resize((CVW, CVH), Image.LANCZOS)

    # RGB'ye duzlestir
    flat = Image.new("RGB", (CVW, CVH), tr)
    flat.paste(img, mask=img.split()[3])

    # Fringe temizle - karanlik pikselleri transparent yap
    arr = np.array(flat)
    dark = np.all(arr < 20, axis=2)
    arr[dark] = list(tr)
    flat = Image.fromarray(arr)
    return flat


# --- Dialoglar ---

class DeviceSelector:
    def __init__(self, parent, devices, cur_idx=None):
        self.selected_index = cur_idx
        self.selected_name = ""
        self._devices = devices

        self.win = tk.Toplevel(parent)
        self.win.title("Mikrofon")
        self.win.geometry("440x340")
        self.win.configure(bg=C_BG)
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        tk.Label(self.win, text="Mikrofon Secin", font=("Segoe UI", 12, "bold"),
                 bg=C_BG, fg=C_TEXT, pady=8).pack()

        self.lb = tk.Listbox(self.win, font=("Segoe UI", 10), bg=C_SURFACE, fg=C_TEXT,
                             selectbackground=C_ACCENT, selectforeground="white",
                             bd=0, highlightthickness=0, relief=tk.FLAT)
        self.lb.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        rec = None
        for i, (idx, name) in enumerate(devices):
            tag = ""
            nl = name.lower()
            if any(k in nl for k in ("bluetooth", "hands-free", "bthh")):
                tag = " [BT]"
            elif "realtek" in nl and "mic" in nl:
                tag = " *"
                if rec is None:
                    rec = i
            self.lb.insert(tk.END, f"  {name}{tag}")
            if idx == cur_idx:
                self.lb.selection_set(i)

        if cur_idx is None and rec is not None:
            self.lb.selection_set(rec)

        bf = tk.Frame(self.win, bg=C_BG, pady=8)
        bf.pack()
        for txt, cmd in [("Sec", self._ok), ("Varsayilan", self._default)]:
            tk.Button(bf, text=txt, command=cmd, font=("Segoe UI", 9),
                      bg=C_SURFACE, fg=C_TEXT, relief=tk.FLAT, width=10,
                      activebackground=C_ACCENT, cursor="hand2").pack(side=tk.LEFT, padx=4)

        self.win.protocol("WM_DELETE_WINDOW", self._default)
        self.win.wait_window()

    def _ok(self):
        sel = self.lb.curselection()
        if sel:
            self.selected_index, self.selected_name = self._devices[sel[0]]
        self.win.destroy()

    def _default(self):
        self.selected_index = None
        self.selected_name = "Varsayilan"
        self.win.destroy()


class HotkeyRecorder:
    def __init__(self, parent, cur):
        self.result = cur
        self._hook = None

        self.win = tk.Toplevel(parent)
        self.win.title("Kisayol")
        self.win.geometry("340x280")
        self.win.configure(bg=C_BG)
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()
        self.win.attributes("-topmost", True)

        tk.Label(self.win, text="Kisayol Ayarla", font=("Segoe UI", 12, "bold"),
                 bg=C_BG, fg=C_TEXT, pady=8).pack()

        for key, name in MOUSE_HOTKEYS.items():
            tk.Button(self.win, text=name, font=("Segoe UI", 9), bg=C_SURFACE,
                      fg=C_TEXT, relief=tk.FLAT, width=24, cursor="hand2",
                      activebackground=C_ACCENT, activeforeground="white",
                      command=lambda k=key: self._pick(k)).pack(pady=2)

        self._rbtn = tk.Button(self.win, text="Klavye Kisayolu Kaydet...",
                               font=("Segoe UI", 9), bg=C_ACCENT, fg="white",
                               relief=tk.FLAT, width=24, cursor="hand2",
                               command=self._rec_start)
        self._rbtn.pack(pady=(10, 2))
        self._slbl = tk.Label(self.win, text="", font=("Segoe UI", 8),
                              bg=C_BG, fg=C_DIM)
        self._slbl.pack()

        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self.win.wait_window()

    def _pick(self, k):
        self.result = k
        self._unhook()
        self.win.destroy()

    def _rec_start(self):
        self._rbtn.config(text="Tusa bas...", bg=C_REC)

        def on_key(ev):
            if ev.event_type != "down":
                return
            time.sleep(0.05)
            combo = kb_hotkey.read_hotkey(suppress=False)
            self.result = combo
            self.win.after(0, self._rec_done, combo)

        self._hook = kb_hotkey.hook(on_key, suppress=False)

    def _rec_done(self, combo):
        self._unhook()
        self._slbl.config(text=combo, fg=C_SUCCESS)
        self._rbtn.config(text="Tamam", bg=C_SUCCESS, command=self.win.destroy)

    def _unhook(self):
        if self._hook:
            try:
                kb_hotkey.unhook(self._hook)
            except Exception:
                pass
            self._hook = None

    def _close(self):
        self._unhook()
        self.win.destroy()


# --- Ana Uygulama ---

class SpeechToTextApp:
    def __init__(self):
        self.config = load_config()
        self.state = "loading"
        self.audio_chunks = []
        self.stream = None
        self.model = None
        self.current_language = self.config["language"]
        self.kb = KeyboardController()
        self.hotkey_hook = None
        self.mouse_listener = None
        self._pulse_job = None
        self._wave_job = None
        self._wave_bars = []
        self._wave_heights = []
        self._recent_rms = 0.0

        self._setup_gui()
        threading.Thread(target=self._load_model, daemon=True).start()

    # --- GUI ---

    def _setup_gui(self):
        self.root = tk.Tk()
        self.root.withdraw()

        px, py = self.config["button_position"]

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self.root.geometry(f"{CVW}x{CVH}+{px}+{py}")

        self.cv = tk.Canvas(self.root, width=CVW, height=CVH,
                            bg=TRANSPARENT, highlightthickness=0)
        self.cv.pack()

        # Pill gorsellerini onceden render et
        self._pill_imgs = {}
        for name, (bg, bd, glow) in PILL_STYLES.items():
            pil = render_pill(bg, bd, glow)
            self._pill_imgs[name] = ImageTk.PhotoImage(pil)

        cx, cy = CVW // 2, CVH // 2

        # Pill arkaplan
        self._pill_item = self.cv.create_image(
            cx, cy, image=self._pill_imgs["loading"], anchor="center")

        # Spektrum barlari (gizli, kayit sirasinda gorunur)
        self._create_wave_bars(cx, cy)

        # Icerik: minik VD
        self._content = self.cv.create_text(
            cx, cy, text="VD", font=("Segoe UI", 8, "bold"),
            fill=C_DIM, anchor="center")

        # Bindings
        self._drag_started = False
        self._dsx = self._dsy = self._wx = self._wy = 0
        self.cv.bind("<ButtonPress-1>", self._press)
        self.cv.bind("<B1-Motion>", self._drag)
        self.cv.bind("<ButtonRelease-1>", self._release)
        self.cv.bind("<Button-3>", self._menu)

        self.root.deiconify()
        self.root.update_idletasks()
        make_non_activating(self.root)

    def _set_pill(self, name):
        if name in self._pill_imgs:
            self.cv.itemconfig(self._pill_item, image=self._pill_imgs[name])

    def _set_content_visible(self, visible):
        self.cv.itemconfig(self._content,
                           state=tk.NORMAL if visible else tk.HIDDEN)

    def _set_content_color(self, color):
        self.cv.itemconfig(self._content, fill=color)

    # --- Dalga Barlari ---

    def _create_wave_bars(self, cx, cy):
        n = 9
        bar_w = 3
        gap = 3
        total = n * bar_w + (n - 1) * gap
        start_x = cx - total / 2 + bar_w / 2

        self._wave_bars = []
        self._wave_heights = [0.0] * n
        for i in range(n):
            x = start_x + i * (bar_w + gap)
            h = 1.5
            bar = self.cv.create_rectangle(
                x - bar_w / 2, cy - h, x + bar_w / 2, cy + h,
                fill=C_REC_GLOW, outline="", state=tk.HIDDEN)
            self._wave_bars.append((bar, x, bar_w))

    def _update_wave_bars(self):
        if self.state != "recording":
            return
        rms = self._recent_rms
        cy = CVH // 2
        n = len(self._wave_bars)
        mid = n // 2
        max_half = PILL_H / 2 - 4

        for i, (bar, x, bw) in enumerate(self._wave_bars):
            dist = abs(i - mid) / mid
            envelope = math.sqrt(max(0, 1 - dist * dist))
            base_h = 2
            max_h = max_half * envelope
            level = min(math.sqrt(max(rms, 0) * 25), 1.0)
            phase = i * 0.7 + time.time() * 8
            wave = 0.7 + 0.3 * math.sin(phase)
            target_h = base_h + (max_h - base_h) * level * wave
            cur = self._wave_heights[i]
            smooth = cur + (target_h - cur) * 0.35
            smooth = max(base_h, smooth)
            self._wave_heights[i] = smooth
            self.cv.coords(bar, x - bw / 2, cy - smooth, x + bw / 2, cy + smooth)

        self._wave_job = self.root.after(45, self._update_wave_bars)

    def _show_wave_bars(self, show):
        st = tk.NORMAL if show else tk.HIDDEN
        for bar, _, _ in self._wave_bars:
            self.cv.itemconfig(bar, state=st)

    # --- Model ---

    def _load_model(self):
        try:
            self.model = WhisperModel(
                self.config["model_size"], device="cpu",
                compute_type="int8", cpu_threads=4)
            dummy = np.zeros(SAMPLE_RATE, dtype=np.float32)
            list(self.model.transcribe(dummy, language="tr"))
            self.root.after(0, self._on_model_ok)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Hata", str(e)))

    def _on_model_ok(self):
        self.state = "idle"
        self._set_pill("idle")
        self._set_content_color(C_ACCENT_GLOW)

        if self.config["input_device_index"] is None:
            devices = sd.query_devices()
            inputs = [(i, d["name"]) for i, d in enumerate(devices)
                      if d["max_input_channels"] > 0]
            if inputs:
                sel = DeviceSelector(self.root, inputs)
                self.config["input_device_index"] = sel.selected_index
                self.config["input_device_name"] = sel.selected_name
                save_config(self.config)

        self._setup_hotkey()

    # --- Hotkey ---

    def _setup_hotkey(self):
        self._cleanup_hotkey()
        hk = self.config["hotkey"]
        if hk.startswith("mouse_"):
            bmap = {"mouse_middle": pynput_mouse.Button.middle,
                    "mouse_x1": pynput_mouse.Button.x1,
                    "mouse_x2": pynput_mouse.Button.x2}
            btn = bmap.get(hk)
            if btn:
                def on_click(x, y, button, pressed):
                    if button == btn and pressed:
                        self.root.after(0, self._toggle)
                self.mouse_listener = pynput_mouse.Listener(on_click=on_click)
                self.mouse_listener.daemon = True
                self.mouse_listener.start()
        else:
            try:
                self.hotkey_hook = kb_hotkey.add_hotkey(
                    hk, lambda: self.root.after(0, self._toggle), suppress=False)
            except Exception:
                pass

    def _cleanup_hotkey(self):
        if self.hotkey_hook:
            try:
                kb_hotkey.unhook_all_hotkeys()
            except Exception:
                pass
            self.hotkey_hook = None
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
            self.mouse_listener = None

    # --- Drag / Click ---

    def _press(self, e):
        self._drag_started = False
        self._dsx, self._dsy = e.x_root, e.y_root
        self._wx, self._wy = self.root.winfo_x(), self.root.winfo_y()

    def _drag(self, e):
        dx, dy = e.x_root - self._dsx, e.y_root - self._dsy
        if abs(dx) > 5 or abs(dy) > 5:
            self._drag_started = True
            self.root.geometry(f"+{self._wx + dx}+{self._wy + dy}")

    def _release(self, e):
        if self._drag_started:
            self.config["button_position"] = [
                self.root.winfo_x(), self.root.winfo_y()]
            save_config(self.config)
        else:
            self._toggle()

    # --- Kayit ---

    def _toggle(self):
        if self.state == "idle":
            self._rec_start()
        elif self.state == "recording":
            self._rec_stop()

    def _rec_start(self):
        self.state = "recording"
        self.audio_chunks = []
        self._recent_rms = 0.0
        self._wave_heights = [0.0] * len(self._wave_bars)

        self._set_pill("recording")
        self._set_content_visible(False)
        self._show_wave_bars(True)
        self._update_wave_bars()
        self._start_pulse()

        try:
            self.stream = sd.InputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                callback=self._audio_cb,
                device=self.config["input_device_index"])
            self.stream.start()
        except Exception:
            self.state = "idle"
            self._show_wave_bars(False)
            self._set_content_visible(True)
            self._idle_look()

    def _audio_cb(self, indata, frames, time_info, status):
        self.audio_chunks.append(indata.copy())
        self._recent_rms = float(np.sqrt(np.mean(indata ** 2)))

    def _rec_stop(self):
        self._stop_pulse()
        self._stop_wave()
        self._show_wave_bars(False)
        self._set_content_visible(True)

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if not self.audio_chunks:
            self.state = "idle"
            self._idle_look()
            return

        audio = np.concatenate(self.audio_chunks, axis=0).flatten()
        if len(audio) < SAMPLE_RATE * MIN_RECORDING_SECONDS:
            self.state = "idle"
            self._idle_look()
            return

        self.state = "transcribing"
        self._set_pill("transcribing")
        self._set_content_color(C_TRANS_GLOW)

        threading.Thread(target=self._transcribe, args=(audio,), daemon=True).start()

    def _transcribe(self, audio):
        try:
            prompt = self.config.get("initial_prompt", "")
            segs, _ = self.model.transcribe(
                audio, language=self.current_language,
                beam_size=self.config["beam_size"], vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500,
                                    speech_pad_ms=200),
                initial_prompt=prompt or None)
            text = " ".join(s.text.strip() for s in segs)
            self.root.after(0, self._on_done, text)
        except Exception:
            self.root.after(0, self._idle_look)
            self.state = "idle"

    def _on_done(self, text):
        self.state = "idle"
        if text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(text.strip())
            self.root.update()
            time.sleep(0.05)
            self.kb.press(Key.ctrl)
            self.kb.press("v")
            self.kb.release("v")
            self.kb.release(Key.ctrl)
            self._set_pill("success")
            self._set_content_color(C_SUCCESS)
            self.root.after(400, self._idle_look)
        else:
            self._idle_look()

    def _idle_look(self):
        self._set_pill("idle")
        self._set_content_color(C_ACCENT_GLOW)

    # --- Pulse animasyon ---

    def _start_pulse(self):
        self._pulse_step = 0

        def pulse():
            if self.state != "recording":
                return
            self._pulse_step += 1
            t = (math.sin(self._pulse_step * 0.15) + 1) / 2
            clr = blend(C_REC, C_REC_GLOW, t * 0.7)
            for bar, _, _ in self._wave_bars:
                self.cv.itemconfig(bar, fill=clr)
            self._pulse_job = self.root.after(50, pulse)

        pulse()

    def _stop_pulse(self):
        if self._pulse_job:
            self.root.after_cancel(self._pulse_job)
            self._pulse_job = None

    def _stop_wave(self):
        if self._wave_job:
            self.root.after_cancel(self._wave_job)
            self._wave_job = None

    # --- Startup ---

    _STARTUP_SHORTCUT = Path(os.environ.get("APPDATA", "")) / \
        "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / \
        "VD Speech-to-Text.lnk"

    def _is_startup_enabled(self):
        return self._STARTUP_SHORTCUT.exists()

    def _toggle_startup(self):
        if self._is_startup_enabled():
            try:
                self._STARTUP_SHORTCUT.unlink()
            except OSError:
                pass
        else:
            script = str(Path(__file__).parent / "start_vd.pyw")
            workdir = str(Path(__file__).parent)
            ps = (
                f'$ws = New-Object -ComObject WScript.Shell; '
                f'$s = $ws.CreateShortcut(\'{self._STARTUP_SHORTCUT}\'); '
                f'$s.TargetPath = \'pythonw.exe\'; '
                f'$s.Arguments = \'"{script}"\'; '
                f'$s.WorkingDirectory = \'{workdir}\'; '
                f'$s.Description = \'VD Speech-to-Text\'; '
                f'$s.Save()'
            )
            try:
                subprocess.run(["powershell", "-Command", ps],
                               capture_output=True, creationflags=0x08000000)
            except OSError:
                pass

    # --- Menu ---

    def _menu(self, event):
        m = tk.Menu(self.root, tearoff=0, bg=C_SURFACE, fg=C_TEXT,
                    activebackground=C_ACCENT, activeforeground="white",
                    font=("Segoe UI", 9), bd=0)
        tr = "\u2713 " if self.current_language == "tr" else "   "
        en = "\u2713 " if self.current_language == "en" else "   "
        m.add_command(label=f"{tr}Turkce", command=lambda: self._lang("tr"))
        m.add_command(label=f"{en}English", command=lambda: self._lang("en"))
        m.add_separator()
        m.add_command(label="   Mikrofon...", command=self._sel_device)
        m.add_command(label="   Terimler...", command=self._edit_terms)
        hk = get_hotkey_display(self.config["hotkey"])
        m.add_command(label=f"   Kisayol: {hk}", command=self._chg_hotkey)
        m.add_separator()
        st = "\u2713 " if self._is_startup_enabled() else "   "
        m.add_command(label=f"{st}Windows ile Baslat",
                      command=self._toggle_startup)
        m.add_separator()
        m.add_command(label="   Cikis", command=self._quit)
        m.post(event.x_root, event.y_root)

    def _lang(self, l):
        self.current_language = l
        self.config["language"] = l
        save_config(self.config)

    def _sel_device(self):
        devs = [(i, d["name"]) for i, d in enumerate(sd.query_devices())
                if d["max_input_channels"] > 0]
        if not devs:
            return
        sel = DeviceSelector(self.root, devs, self.config["input_device_index"])
        self.config["input_device_index"] = sel.selected_index
        self.config["input_device_name"] = sel.selected_name
        save_config(self.config)

    def _chg_hotkey(self):
        rec = HotkeyRecorder(self.root, self.config["hotkey"])
        if rec.result != self.config["hotkey"]:
            self.config["hotkey"] = rec.result
            save_config(self.config)
            self._setup_hotkey()

    def _edit_terms(self):
        w = tk.Toplevel(self.root)
        w.title("Terimler")
        w.geometry("420x250")
        w.configure(bg=C_BG)
        w.transient(self.root)
        t = tk.Text(w, font=("Segoe UI", 9), bg=C_SURFACE, fg=C_TEXT,
                    insertbackground=C_TEXT, wrap=tk.WORD, bd=0)
        t.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        t.insert("1.0", self.config.get("initial_prompt", ""))

        def save():
            self.config["initial_prompt"] = t.get("1.0", tk.END).strip()
            save_config(self.config)
            w.destroy()

        tk.Button(w, text="Kaydet", command=save, font=("Segoe UI", 9),
                  bg=C_ACCENT, fg="white", relief=tk.FLAT,
                  cursor="hand2").pack(pady=(0, 8))

    def _quit(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        self._stop_pulse()
        self._stop_wave()
        self._cleanup_hotkey()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    SpeechToTextApp().run()
