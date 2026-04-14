"""GLORB Desktop Installer — flash firmware to ESP32-S3 via esptool."""

import json
import os
import queue
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk

import serial.tools.list_ports

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_TITLE = "GLORB Desktop Installer"
CHIP = "esp32s3"
BAUD_RATE = "921600"

# Firmware options mirroring index.htm <select id="ver">
# Structure: list of (group_label, [(display_name, manifest_path), ...])
FIRMWARE_OPTIONS = [
    ("Main Releases", [
        ("GLORB 0.15.4-2.0-b0", "bin/GLORB_0_15_4-2_0-b0/manifest.json"),
        ("GLORB 0.14.4-1.3", "bin/GLORB_0_14_4-1_3/manifest_gma_83.json"),
        ("GLORB 0.14.4-1.2", "bin/GLORB_0_14_4-1_2/manifest_gma_83.json"),
        ("GLORB 0.14.4-1.1", "bin/GLORB_0_14_4-1_1/manifest_gma_83.json"),
        ("GLORB 0.14.4-1.0", "bin/GLORB_0_14_4-1_0/manifest_gma_83.json"),
    ]),
    ("Pre-production Units", [
        ("GLORB 0.14.4-1.1 (sph_81)", "bin/GLORB_0_14_4-1_1/manifest_sph_81.json"),
        ("GLORB 0.14.4-1.0 (sph_81)", "bin/GLORB_0_14_4-1_0/manifest_sph_81.json"),
    ]),
    ("Debug Builds", [
        ("GLORB 0.15.4-2.0-b0 (Debug)", "bin/GLORB_0_15_4-2_0-b0/manifest_debug.json"),
        ("GLORB 0.14.4-1.3 (Debug)", "bin/GLORB_0_14_4-1_3/manifest_gma_83_debug.json"),
        ("GLORB 0.14.4-1.2 (Debug)", "bin/GLORB_0_14_4-1_2/manifest_gma_83_debug.json"),
    ]),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_resource_path(relative_path):
    """Resolve a path relative to the repo root (dev) or PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), "..", relative_path)


def load_manifest(manifest_relative_path):
    """Parse a manifest JSON and return (name, version, [(offset, bin_path)])."""
    manifest_path = get_resource_path(manifest_relative_path)
    manifest_dir = os.path.dirname(manifest_path)
    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)
    build = data["builds"][0]
    parts = []
    for part in build["parts"]:
        bin_path = os.path.join(manifest_dir, part["path"])
        parts.append((part["offset"], bin_path))
    return data["name"], data["version"], parts


def list_serial_ports():
    """Return list of (device, display_string) for available serial ports."""
    ports = serial.tools.list_ports.comports()
    return [(p.device, f"{p.device} - {p.description}") for p in ports]


# ---------------------------------------------------------------------------
# Stdout capture — intercepts esptool's print output
# ---------------------------------------------------------------------------


class OutputCapture:
    """Redirect stdout to a queue so the UI thread can display it."""

    def __init__(self, msg_queue):
        self._queue = msg_queue
        self._original = sys.stdout

    def write(self, text):
        if text.strip():
            self._queue.put(("log", text.strip()))
            # Parse esptool progress lines like "Writing at 0x00010000... (3 %)"
            m = re.search(r"\((\d+)\s*%\)", text)
            if m:
                self._queue.put(("progress", int(m.group(1))))
        # Also write to original stdout for debugging
        if self._original:
            self._original.write(text)

    def flush(self):
        if self._original:
            self._original.flush()


# ---------------------------------------------------------------------------
# Flash worker — runs esptool in a background thread
# ---------------------------------------------------------------------------


class FlashWorker(threading.Thread):
    """Run erase + flash operations in a background thread."""

    def __init__(self, port, manifest_path, msg_queue):
        super().__init__(daemon=True)
        self.port = port
        self.manifest_path = manifest_path
        self.queue = msg_queue
        self.cancelled = False

    def run(self):
        import esptool

        capture = OutputCapture(self.queue)
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = capture
        sys.stderr = capture

        try:
            name, version, parts = load_manifest(self.manifest_path)
            self.queue.put(("log", f"Firmware: {name} v{version}"))
            self.queue.put(("log", f"Port: {self.port}"))
            self.queue.put(("log", f"Parts to flash: {len(parts)}"))

            base_args = ["--chip", CHIP, "--port", self.port, "--baud", BAUD_RATE]

            # Step 1: Erase flash
            self.queue.put(("status", "Erasing flash..."))
            self.queue.put(("progress_mode", "indeterminate"))
            erase_args = base_args + ["erase_flash"]
            self.queue.put(("log", f"Running: esptool {' '.join(erase_args)}"))
            try:
                esptool.main(erase_args)
            except SystemExit:
                pass  # esptool.main() calls sys.exit(0) on success
            if self.cancelled:
                self.queue.put(("status", "Cancelled"))
                return
            self.queue.put(("log", "Flash erased successfully"))

            # Step 2: Write firmware
            self.queue.put(("status", "Writing firmware..."))
            self.queue.put(("progress_mode", "determinate"))
            self.queue.put(("progress", 0))

            write_args = base_args + [
                "write_flash",
                "--flash_mode", "dio",
                "--flash_size", "detect",
            ]
            for offset, filepath in parts:
                write_args.extend([hex(offset), filepath])

            self.queue.put(("log", f"Running: esptool write_flash with {len(parts)} parts"))
            try:
                esptool.main(write_args)
            except SystemExit:
                pass  # esptool.main() calls sys.exit(0) on success

            if self.cancelled:
                self.queue.put(("status", "Cancelled"))
                return

            self.queue.put(("progress", 100))
            self.queue.put(("status", "Installation complete!"))
            self.queue.put(("done", True))

        except Exception as e:
            self.queue.put(("log", f"ERROR: {e}"))
            self.queue.put(("status", f"Error: {e}"))
            self.queue.put(("done", False))
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------


class GlorbInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg="#000000")
        self.resizable(False, False)
        self.geometry("520x680")

        self.msg_queue = queue.Queue()
        self.worker = None

        # Build flat list of firmware options for the dropdown
        self._fw_options = []  # [(display_name, manifest_path), ...]
        for _group, items in FIRMWARE_OPTIONS:
            for display_name, manifest_path in items:
                self._fw_options.append((display_name, manifest_path))

        self._ports = []
        self._known_port_devices = set()
        self._auto_poll_active = True

        self._build_ui()
        self._refresh_ports()
        self._schedule_auto_poll()

    # ---- UI construction ----

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Configure dark theme styles
        style.configure("Dark.TFrame", background="#000000")
        style.configure("Dark.TLabel", background="#000000", foreground="#ffffff",
                         font=("Arial", 12))
        style.configure("Title.TLabel", background="#000000", foreground="#ffffff",
                         font=("Arial", 18, "bold"))
        style.configure("Status.TLabel", background="#000000", foreground="#ffffff",
                         font=("Arial", 11))
        style.configure("Small.TLabel", background="#000000", foreground="#aaaaaa",
                         font=("Arial", 10))
        style.configure("Dark.TCheckbutton", background="#000000", foreground="#ffffff",
                         font=("Arial", 11))
        style.map("Dark.TCheckbutton",
                  background=[("active", "#000000")],
                  foreground=[("active", "#ffffff")])
        style.configure("Install.TButton", font=("Arial", 13, "bold"), padding=(20, 12))
        style.configure("Refresh.TButton", font=("Arial", 10), padding=(8, 4))

        main_frame = ttk.Frame(self, style="Dark.TFrame")
        main_frame.pack(fill="both", expand=True, padx=24, pady=16)

        # Title
        ttk.Label(main_frame, text="GLORB", style="Title.TLabel",
                  anchor="center").pack(pady=(0, 0))
        ttk.Label(main_frame, text="DESKTOP INSTALLER", style="Dark.TLabel",
                  anchor="center").pack(pady=(0, 16))

        # Firmware selector
        fw_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        fw_frame.pack(fill="x", pady=(8, 4))
        ttk.Label(fw_frame, text="Firmware:", style="Dark.TLabel").pack(anchor="w")

        self.fw_var = tk.StringVar()
        fw_names = [name for name, _path in self._fw_options]
        self.fw_combo = ttk.Combobox(fw_frame, textvariable=self.fw_var,
                                      values=fw_names, state="readonly",
                                      font=("Arial", 11), width=42)
        self.fw_combo.current(0)
        self.fw_combo.pack(fill="x", pady=(4, 0))

        # Serial port selector
        port_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        port_frame.pack(fill="x", pady=(12, 4))
        ttk.Label(port_frame, text="Serial Port:", style="Dark.TLabel").pack(anchor="w")

        port_row = ttk.Frame(port_frame, style="Dark.TFrame")
        port_row.pack(fill="x", pady=(4, 0))

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_row, textvariable=self.port_var,
                                        state="readonly", font=("Arial", 11))
        self.port_combo.pack(side="left", fill="x", expand=True)

        self.refresh_btn = ttk.Button(port_row, text="Refresh",
                                       style="Refresh.TButton",
                                       command=self._refresh_ports)
        self.refresh_btn.pack(side="left", padx=(8, 0))

        # Install button
        btn_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        btn_frame.pack(fill="x", pady=(20, 8))
        self.install_btn = ttk.Button(btn_frame, text="INSTALL FIRMWARE",
                                       style="Install.TButton",
                                       command=self._on_install)
        self.install_btn.pack()

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var,
                  style="Status.TLabel").pack(anchor="w", pady=(8, 4))

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                             maximum=100, length=460)
        self.progress_bar.pack(fill="x", pady=(0, 8))

        # Log area
        ttk.Label(main_frame, text="Log:", style="Small.TLabel").pack(anchor="w")
        self.log_text = tk.Text(main_frame, height=10, bg="#111111", fg="#ffffff",
                                 font=("Courier", 10), relief="flat",
                                 insertbackground="#ffffff", wrap="word",
                                 state="disabled")
        self.log_text.pack(fill="both", expand=True, pady=(4, 0))

    # ---- Port management ----

    def _refresh_ports(self):
        """Scan serial ports, update dropdown, and auto-select new devices."""
        ports = list_serial_ports()
        new_devices = {dev for dev, _ in ports}
        old_devices = self._known_port_devices

        # Detect newly connected devices
        added = new_devices - old_devices
        removed = old_devices - new_devices

        # Remember current selection
        prev_idx = self.port_combo.current()
        prev_device = self._ports[prev_idx][0] if prev_idx >= 0 and self._ports else None

        self._ports = ports
        self._known_port_devices = new_devices
        display_names = [display for _dev, display in ports]
        self.port_combo["values"] = display_names

        if added:
            # Auto-select the first newly connected device
            new_device = next(iter(added))
            for i, (dev, _) in enumerate(ports):
                if dev == new_device:
                    self.port_combo.current(i)
                    self._log(f"Device connected: {dev}")
                    break
        elif prev_device and prev_device in new_devices:
            # Keep previous selection if still present
            for i, (dev, _) in enumerate(ports):
                if dev == prev_device:
                    self.port_combo.current(i)
                    break
        elif ports:
            self.port_combo.current(0)
        else:
            self.port_var.set("")

        if removed:
            for dev in removed:
                self._log(f"Device disconnected: {dev}")

    def _schedule_auto_poll(self):
        """Poll for serial port changes every second."""
        if not self._auto_poll_active:
            return
        # Don't poll during flashing — esptool owns the port
        if not (self.worker and self.worker.is_alive()):
            self._refresh_ports()
        self.after(1000, self._schedule_auto_poll)

    # ---- Logging ----

    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ---- Install / Cancel ----

    def _on_install(self):
        if self.worker and self.worker.is_alive():
            # Cancel
            self.worker.cancelled = True
            self.install_btn.configure(text="INSTALL FIRMWARE")
            self.status_var.set("Cancelling...")
            return

        # Validate port selection
        if not self._ports:
            self.status_var.set("No serial port selected")
            self._log("ERROR: No serial port available. Connect your GLORB via USB-C.")
            return

        idx = self.port_combo.current()
        if idx < 0:
            self.status_var.set("No serial port selected")
            return

        port = self._ports[idx][0]
        fw_idx = self.fw_combo.current()
        manifest_path = self._fw_options[fw_idx][1]

        self._log(f"\n--- Starting installation ---")
        self._log(f"Firmware: {self._fw_options[fw_idx][0]}")
        self._log(f"Port: {port}")

        # Disable controls during flash
        self.fw_combo.configure(state="disabled")
        self.port_combo.configure(state="disabled")
        self.refresh_btn.configure(state="disabled")
        self.install_btn.configure(text="CANCEL")
        self.progress_var.set(0)

        # Start worker
        self.worker = FlashWorker(port, manifest_path, self.msg_queue)
        self.worker.start()
        self._poll_queue()

    def _poll_queue(self):
        """Process messages from the flash worker."""
        try:
            while True:
                msg_type, msg_data = self.msg_queue.get_nowait()
                if msg_type == "log":
                    self._log(str(msg_data))
                elif msg_type == "status":
                    self.status_var.set(str(msg_data))
                elif msg_type == "progress":
                    self.progress_var.set(msg_data)
                elif msg_type == "progress_mode":
                    if msg_data == "indeterminate":
                        self.progress_bar.configure(mode="indeterminate")
                        self.progress_bar.start(20)
                    else:
                        self.progress_bar.stop()
                        self.progress_bar.configure(mode="determinate")
                elif msg_type == "done":
                    self._on_flash_done(msg_data)
                    return
        except queue.Empty:
            pass

        if self.worker and self.worker.is_alive():
            self.after(100, self._poll_queue)
        else:
            # Worker died unexpectedly
            self._on_flash_done(False)

    def _on_flash_done(self, success):
        """Re-enable UI after flashing completes."""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.fw_combo.configure(state="readonly")
        self.port_combo.configure(state="readonly")
        self.refresh_btn.configure(state="normal")
        self.install_btn.configure(text="INSTALL FIRMWARE")

        if success:
            self.progress_var.set(100)
            self.status_var.set("Installation complete!")
            self._log("--- Installation finished successfully ---\n")
        else:
            self.status_var.set("Installation failed — see log for details")
            self._log("--- Installation failed ---\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = GlorbInstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
