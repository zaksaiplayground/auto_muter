"""GUI for the AutoMuter."""

# TODO: add tests
import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class AutoMuterGUI:
    """GUI for the Auto Muter application"""

    def __init__(self, audio_muter):
        """Initialize the GUI with a reference to the AudioMuter instance"""
        self.audio_muter = audio_muter
        self.root = None

    def create_gui(self):
        """Create the Tkinter GUI"""
        self.root = tk.Tk()
        self.root.title("Auto Muter")
        self.root.geometry("500x450")
        self.root.resizable(True, True)

        # Create a frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Auto Muter", font=("Helvetica", 16)).pack(pady=10)

        # Device selection
        ttk.Label(main_frame, text="Select Input Device:").pack(anchor="w")
        device_names = [f"{dev['name']}" for dev in self.audio_muter.devices]
        self.device_var = tk.StringVar()
        if device_names:
            self.device_var.set(device_names[0])
        device_combo = ttk.Combobox(
            main_frame, textvariable=self.device_var, values=device_names, width=50
        )
        device_combo.pack(fill=tk.X, pady=5)

        # Energy threshold
        ttk.Label(main_frame, text="Energy Threshold:").pack(anchor="w")
        self.threshold_var = tk.IntVar(value=self.audio_muter.energy_threshold)
        threshold_scale = ttk.Scale(
            main_frame, from_=100, to=2000, variable=self.threshold_var
        )
        threshold_scale.pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, textvariable=self.threshold_var).pack()

        # Silence timeout
        ttk.Label(main_frame, text="Silence Timeout (seconds):").pack(anchor="w")
        self.timeout_var = tk.DoubleVar(value=self.audio_muter.silence_timeout)
        timeout_scale = ttk.Scale(
            main_frame, from_=0.5, to=10.0, variable=self.timeout_var
        )
        timeout_scale.pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, textvariable=self.timeout_var).pack()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Start", command=self._start_from_gui).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Stop", command=self.audio_muter.stop).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            button_frame, text="Test Mute", command=self.audio_muter.toggle_mute
        ).pack(side=tk.LEFT, padx=5)

        # FIXME: keep speaker to start_up state before exit
        self.exit_button = ttk.Button(
            button_frame, text="Exit", command=self._exit_application
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Status labels
        self.run_status_label = ttk.Label(main_frame, text="Status: Stopped")
        self.run_status_label.pack(pady=5)
        self.audio_muter.run_status_label = self.run_status_label

        initial_mute_state = (
            "Muted" if self.audio_muter.initial_mute_state else "Unmuted"
        )
        self.status_label = ttk.Label(
            main_frame, text=f"Current State: {initial_mute_state}"
        )
        self.status_label.pack(pady=5)
        self.audio_muter.status_label = self.status_label

        # Add dependency status
        dependencies_frame = ttk.LabelFrame(main_frame, text="Dependencies")
        dependencies_frame.pack(fill=tk.X, pady=5)

        # Setup update loop for GUI
        def update_gui():
            if self.audio_muter.running:
                mute_text = "Muted" if self.audio_muter.muted else "Unmuted"
                self.status_label.config(text=f"Current State: {mute_text}")
            self.root.after(100, update_gui)

        update_gui()

        # When closing window
        def on_close():
            self.audio_muter.stop()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_close)

        # Start the GUI main loop
        self.root.mainloop()

    def _start_from_gui(self):
        """Start with updated settings from GUI"""
        # Update settings
        device_str = self.device_var.get()
        if device_str:
            # Find device ID for the selected name
            for device in self.audio_muter.devices:
                if device["name"] == device_str:
                    self.audio_muter.input_device = device["id"]
                    break

        self.audio_muter.energy_threshold = self.threshold_var.get()
        self.audio_muter.silence_timeout = self.timeout_var.get()

        # Start service
        self.audio_muter.start()

    def _exit_application(self):
        """Clean up and exit application"""
        # Make sure to restore initial mute state before exit
        self.audio_muter.cleanup_before_exit()

        # Then destroy the window
        if self.root:
            self.root.destroy()

    def _stop_from_gui(self):
        """Stop the auto-muter"""
        # Existing stop code will work since we've updated the AudioMuter class
        self.audio_muter.stop()
